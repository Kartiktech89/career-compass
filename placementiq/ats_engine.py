"""
ats_engine.py - rule-based ATS resume screening.

Stack: pypdf (PDF text + hyperlinks), custom Python/regex logic, pandas (result tables).
No Streamlit code in here, so you can import it from anywhere, e.g. your FastAPI backend:

    from ats_engine import analyze_resume
    result = analyze_resume(pdf_bytes, "Kartik_Sardesai_Resume.pdf", role="Data Scientist / ML Engineer")
    print(result.score, result.verdict)
    print(result.fixes)

Every check is transparent: it has a weight, a pass/warn/fail status, the evidence found,
and a concrete fix. Tune the weights / word lists in the constants below.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from io import BytesIO

import pandas as pd
from pypdf import PdfReader

# --------------------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------------------
GENERAL = "General (no target role)"

# "canonical|variant|variant" - any variant counts as a match for that skill.
ROLE_KEYWORDS: dict[str, list[str]] = {
    "Data Scientist / ML Engineer": [
        "python", "machine learning|ml", "deep learning", "scikit-learn|sklearn", "pandas", "numpy",
        "tensorflow", "pytorch|torch", "sql", "feature engineering", "data preprocessing|data cleaning",
        "model evaluation", "nlp|natural language processing", "computer vision|opencv",
        "matplotlib|seaborn", "jupyter", "git|github", "statistics", "docker", "fastapi|flask",
        "streamlit", "llm|large language model", "transformers|hugging face", "rest api|api",
    ],
    "Data Analyst": [
        "sql", "excel", "power bi|powerbi", "tableau", "python", "pandas", "numpy",
        "data visualization|data visualisation", "statistics", "etl", "dashboard", "data cleaning",
        "a/b testing", "reporting", "data analysis|data analytics", "google sheets", "looker",
    ],
    "Software Developer": [
        "python", "java", "c++", "data structures", "algorithms", "oop|object-oriented|object oriented",
        "sql", "git", "rest api|restful", "docker", "linux", "unit testing|pytest|junit", "agile",
        "ci/cd", "system design", "debugging", "mongodb|postgresql|mysql",
    ],
    "Web Developer": [
        "html", "css", "javascript", "react", "node.js|nodejs", "rest api|restful", "git",
        "responsive design", "typescript", "sql|mongodb", "tailwind|bootstrap", "deployment|vercel|netlify",
        "express", "authentication|jwt",
    ],
}
ALL_SKILL_SPECS = sorted({s for specs in ROLE_KEYWORDS.values() for s in specs})

SECTION_ALIASES = {
    "summary": ["summary", "professional summary", "career summary", "career objective", "objective",
                "profile", "professional profile"],
    "education": ["education", "academic background", "academics", "educational qualifications",
                  "qualifications", "academic qualifications"],
    "experience": ["experience", "work experience", "professional experience", "employment history",
                   "internships", "internship experience", "work history", "internship"],
    "projects": ["projects", "personal projects", "academic projects", "key projects", "project work",
                 "technical projects"],
    "skills": ["skills", "technical skills", "core competencies", "key skills", "skills summary",
               "tools and technologies", "technical proficiency", "skills & tools", "skills and tools"],
    "certifications": ["certifications", "certificates", "licenses", "courses", "training",
                       "certifications & courses", "certifications and courses"],
    "achievements": ["achievements", "awards", "honors", "honours", "accomplishments",
                     "extracurricular activities", "leadership", "awards & achievements",
                     "publications", "research"],
}
ALIAS_LOOKUP = {a: sec for sec, aliases in SECTION_ALIASES.items() for a in aliases}

# Creative headings that ATS parsers often fail to map -> what to rename them to.
NONSTANDARD_HEADINGS = {
    "my journey": ("experience", "Experience"),
    "professional journey": ("experience", "Experience"),
    "toolbox": ("skills", "Skills"),
    "tech stack": ("skills", "Skills"),
    "core strengths": ("skills", "Skills"),
    "what i do": ("summary", "Summary"),
    "about me": ("summary", "Summary"),
    "who am i": ("summary", "Summary"),
    "my projects": ("projects", "Projects"),
    "things i built": ("projects", "Projects"),
    "what i have built": ("projects", "Projects"),
}

ACTION_VERBS = set("""
achieved analyzed analysed architected automated built championed collaborated compiled configured conducted
constructed containerized created customized debugged decreased delivered deployed designed detected developed
devised directed drove enabled engineered enhanced established evaluated executed expanded extracted fine-tuned
finetuned generated implemented improved increased initiated integrated introduced launched led leveraged
maintained managed mentored migrated modeled modelled monitored negotiated optimized optimised orchestrated
organized organised oversaw owned planned presented prioritized processed produced programmed prototyped
published reduced refactored released researched resolved restructured reviewed scaled scripted secured shipped
simplified solved spearheaded standardized streamlined structured supervised tested trained transformed tuned
upgraded validated visualized wrote ran won
build create design develop deploy implement lead manage optimize automate analyze engineer improve reduce train
test architect integrate launch
""".split())
WEAK_VERBS = {"worked", "helped", "assisted", "responsible", "involved", "participated", "handled", "did",
              "made", "used", "tried", "attended", "tasked", "was", "were", "have", "has"}

# (regex, replace-with options, why)
WEAK_PHRASES = [
    (r"\bresponsible for\b", "Led / Managed / Owned", "Describes a duty, not an achievement"),
    (r"\bworked (?:on|with)\b", "Built / Developed / Implemented", "Passive; hides what YOU did"),
    (r"\bhelped(?: to)?\b", "Supported / Contributed to / Co-developed", "Understates your contribution"),
    (r"\bassisted (?:in|with|on)\b", "Supported / Contributed to", "Understates your contribution"),
    (r"\binvolved in\b", "Executed / Delivered", "Vague - says nothing about your role"),
    (r"\bparticipated in\b", "Contributed to / Collaborated on", "Vague - says nothing about your role"),
    (r"\btasked with\b", "Delivered / Executed", "Describes assignment, not result"),
    (r"\bduties (?:included|include)\b", "Start each bullet with a result verb", "Job-description language"),
    (r"\bfamiliar with\b", "Proficient in / Hands-on with (only if true)", "Signals weak skill level"),
    (r"\bbasic knowledge of\b", "Working knowledge of / Applied ... in <project>", "Signals weak skill level"),
    (r"\bvarious\b|\betc\b\.?", "Name the exact tools, numbers or outcomes", "Vague filler; ATS cannot match it"),
]

# (regex, what to do instead)
CLICHES = [
    (r"\bhard[- ]?working\b", "Prove it with a result: 'Shipped X in Y weeks'"),
    (r"\bteam player\b", "Show it: 'Collaborated with a 4-member team to deliver ...'"),
    (r"\bgo[- ]getter\b", "Delete; replace with an achievement"),
    (r"\bself[- ]motivated\b", "Show it: 'Self-learned X and built Y'"),
    (r"\bdetail[- ]oriented\b", "Show it: 'Reduced errors by X% through validation checks'"),
    (r"\bresults?[- ]driven\b", "Delete; state the actual result with a number"),
    (r"\bquick(?:ly)? learner\b|\bfast learner\b", "Show it: 'Learned X in N weeks and built Y'"),
    (r"\bpassionate (?:about|for)\b", "Delete; show passion through projects/links"),
    (r"\bexcellent communication skills\b|\bgood communication skills\b",
     "Show it: 'Presented X to N people' / 'Wrote docs for Y'"),
    (r"\bthink(?:ing)? outside the box\b|\bout[- ]of[- ]the[- ]box\b", "Delete; describe the creative solution"),
    (r"\bsynergy\b|\bdynamic\b", "Delete; buzzword with no ATS value"),
]

# Info that is outdated / irrelevant / bias-prone on a modern resume.
PERSONAL_INFO = [
    (r"\bdate of birth\b|\bd\.?o\.?b\b", "Date of birth"),
    (r"\bmarital status\b", "Marital status"),
    (r"\bfather'?s? name\b|\bmother'?s? name\b", "Parent's name"),
    (r"\breligion\b", "Religion"),
    (r"\bi hereby declare\b|^\s*declaration\b", "Declaration paragraph"),
    (r"\bpassport[- ]size\b|\bphotograph\b", "Photograph"),
]

DEGREE_RE = re.compile(
    r"\b(?:B\.?\s?E\.?|B\.?\s?Tech|M\.?\s?Tech|M\.?\s?E\.?|BCA|MCA|B\.?\s?Sc|M\.?\s?Sc|MBA|B\.?\s?Com|Ph\.?D)\b"
    r"|(?i:bachelor|master|diploma|engineering|b\.tech|b\.e\b)"
)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d{1,3}[\s-]?)?(?:\d{10}|\d{5}[\s-]\d{5}|\d{3}[\s-]\d{3}[\s-]\d{4})(?!\d)")
LINKEDIN_RE = re.compile(r"linkedin\.com/(?:in|pub)/[\w%-]+", re.I)
GITHUB_RE = re.compile(r"github\.com/[\w-]+", re.I)
OTHER_URL_RE = re.compile(
    r"(?:https?://|www\.)?(?!(?:www\.)?(?:linkedin|github|gmail|outlook|yahoo)\.)"
    r"[a-z0-9-]+\.(?:me|dev|io|com|in|app|tech|xyz|net|org|ai)\b(?:/[\w./%-]*)?", re.I)
DATE_RANGE_RE = re.compile(
    r"(?i)\b(?:[A-Za-z]{3,9}\.?\s+)?(?:19|20)\d{2}\s*(?:-|–|—|to)\s*"
    r"(?:(?:[A-Za-z]{3,9}\.?\s+)?(?:19|20)\d{2}|present|current|ongoing|now)\b")
RESUME_VOCAB_RE = re.compile(
    r"(?i)\b(?:skills|projects?|experience|internship|education|certifications?|achievements?|"
    r"responsibilities|objective|summary|developed|built|implemented|cgpa|gpa)\b")
BULLET_RE = re.compile(r"^\s*[•●▪■◦○◆►▶\-–—*·\uf0b7\uf0a7]+\s*")
METRIC_RE = re.compile(r"(?<![A-Za-z0-9.\-_])(?:\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s?(?:%|\+|[kKmM]\b|x\b)?")
MONTHS_ABBR = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
MONTHS_FULL = r"(?:January|February|March|April|June|July|August|September|October|November|December)"
STOPWORDS = set("""
a an the and or of to in for on with at by from as is are be been being this that these those it its you your we our
they their will would can could should may might must have has had do does did not no yes if then than so such into
about over under between within across per via etc using use used work working works role roles job jobs candidate
candidates company team teams years year experience experienced skills skill knowledge ability able strong good
excellent required requirements preferred responsibilities responsibility looking join opportunity including include
includes related relevant plus new well also more most other any all both each ensure support develop development
developing build building help like based must-have nice-to-have etc. including environment environments
""".split())

_ICON = {"Pass": "✅ Pass", "Warn": "⚠️ Warn", "Fail": "❌ Fail"}


# --------------------------------------------------------------------------------------
# Result container
# --------------------------------------------------------------------------------------
@dataclass
class AtsResult:
    filename: str
    error: str = ""
    pages: int = 0
    words: int = 0
    is_resume: bool = False
    confidence: float = 0.0
    signals: dict = field(default_factory=dict)
    score: float = 0.0
    verdict: str = ""
    knockouts: list = field(default_factory=list)
    keyword_source: str = ""
    keyword_match: float | None = None
    sections: list = field(default_factory=list)
    checks: pd.DataFrame = field(default_factory=pd.DataFrame)
    keywords: pd.DataFrame = field(default_factory=pd.DataFrame)
    fixes: pd.DataFrame = field(default_factory=pd.DataFrame)
    replacements: pd.DataFrame = field(default_factory=pd.DataFrame)
    bullets: pd.DataFrame = field(default_factory=pd.DataFrame)
    text: str = ""


# --------------------------------------------------------------------------------------
# PDF extraction
# --------------------------------------------------------------------------------------
def extract_pdf(data: bytes) -> tuple[list[str], list[str]]:
    """Return (text per page, hyperlink URLs). Uses pypdf only."""
    reader = PdfReader(BytesIO(data))
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as exc:  # noqa: BLE001
            raise ValueError("PDF is password protected") from exc
    pages, links = [], []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:  # noqa: BLE001
            pages.append("")
        try:
            for annot in page.get("/Annots") or []:
                action = annot.get_object().get("/A")
                if action:
                    uri = action.get_object().get("/URI")
                    if uri:
                        links.append(str(uri))
        except Exception:  # noqa: BLE001
            pass
    return pages, links


def _clean(text: str) -> str:
    for a, b in (("ﬁ", "fi"), ("ﬂ", "fl"), ("\u00a0", " "), ("\u200b", ""), ("\u2022", "•")):
        text = text.replace(a, b)
    return text


# --------------------------------------------------------------------------------------
# Parsing helpers
# --------------------------------------------------------------------------------------
def _heading(line: str):
    """Return (section, nonstandard_suggestion|None) if the line is a section heading."""
    if len(line.split()) > 4 or len(line) > 40:
        return None
    norm = re.sub(r"\s+", " ", re.sub(r"[^a-z& ]", "", line.lower())).strip()
    if norm in ALIAS_LOOKUP:
        return ALIAS_LOOKUP[norm], None
    if norm in NONSTANDARD_HEADINGS:
        sec, suggestion = NONSTANDARD_HEADINGS[norm]
        return sec, (line, suggestion)
    return None


def split_sections(lines: list[str]):
    sections: dict[str, list[str]] = {"header": []}
    nonstandard, current = [], "header"
    for ln in lines:
        h = _heading(ln)
        if h:
            current = h[0]
            sections.setdefault(current, [])
            if h[1]:
                nonstandard.append(h[1])
            continue
        sections[current].append(ln)
    return sections, nonstandard


def _bullets(sections: dict[str, list[str]]) -> list[str]:
    out = []
    for sec in ("experience", "projects", "achievements"):
        lines = sections.get(sec, [])
        uses_bullets = any(BULLET_RE.match(l) for l in lines)
        cur = ""
        for ln in lines:
            has_b = bool(BULLET_RE.match(ln))
            body = BULLET_RE.sub("", ln).strip()
            if not body:
                continue
            if uses_bullets and not has_b and cur and body[:1].islower():
                cur = f"{cur} {body}"          # wrapped continuation line
            else:
                if cur:
                    out.append(cur)
                cur = body
        if cur:
            out.append(cur)
    return [b for b in out if len(b.split()) >= 6 and "|" not in b]


def _has_metric(text: str) -> bool:
    for m in METRIC_RE.finditer(text):
        if re.fullmatch(r"(?:19|20)\d{2}", m.group().strip()):
            continue
        return True
    return False


def _first_word(text: str) -> str:
    m = re.match(r"[A-Za-z\-]+", text)
    return m.group().lower() if m else ""


def _is_strong_verb(w: str) -> bool:
    if w in WEAK_VERBS:
        return False
    return w in ACTION_VERBS or (w.endswith("ed") and len(w) > 3)


def _kw_pattern(spec: str) -> re.Pattern:
    variants = sorted((v.strip() for v in spec.split("|") if v.strip()), key=len, reverse=True)
    pat = "|".join(re.escape(v) for v in variants)
    return re.compile(rf"(?<![\w+#])(?:{pat})(?![\w+#]|-\w)", re.I)


def jd_keywords(jd: str) -> list[str]:
    """Known skills found in the JD + frequent non-generic JD terms."""
    found = [s for s in ALL_SKILL_SPECS if _kw_pattern(s).search(jd)]
    covered = {v for s in found for v in s.lower().split("|")}
    words = [w.strip(".-") for w in re.findall(r"[A-Za-z][A-Za-z+#.\-]{2,}", jd.lower())]
    freq = Counter(w for w in words if w and w not in STOPWORDS and w not in covered)
    extras = [w for w, c in freq.most_common(30) if c >= 2][:10]
    return found + extras


def _check(rows, category, name, ratio, maximum, detail, fix="", pass_at=0.8, warn_at=0.4):
    ratio = max(0.0, min(1.0, float(ratio)))
    status = "Pass" if ratio >= pass_at else "Warn" if ratio >= warn_at else "Fail"
    earned = round(maximum * ratio, 2)
    rows.append({
        "Category": category, "Check": name, "Status": _ICON[status],
        "Score": f"{earned:g}/{maximum}", "Details": detail,
        "Fix": "" if status == "Pass" else fix, "Earned": earned, "Max": maximum, "_status": status,
    })


def _verdict(score: float) -> str:
    if score >= 80:
        return "Strong - likely to pass ATS"
    if score >= 65:
        return "Good - minor fixes needed"
    if score >= 50:
        return "Average - needs work"
    return "Weak - likely auto-rejected"


def _failed(filename: str, reason: str, pages: int = 0) -> AtsResult:
    checks = pd.DataFrame([{
        "Category": "Parsing", "Check": "Readable text", "Status": _ICON["Fail"], "Score": "0/1",
        "Details": reason,
        "Fix": "Export the resume as a text-based PDF (Word: File > Save As > PDF; Google Docs: File > Download > PDF). "
               "Do not use scanned images or 'Print to image'.",
        "Earned": 0, "Max": 1, "_status": "Fail"}])
    fixes = pd.DataFrame([{"Priority": "High", "Area": "Parsing - Readable text",
                           "Problem": reason, "Action": checks.iloc[0]["Fix"]}])
    return AtsResult(filename=filename, error=reason, pages=pages, verdict="Unreadable - rejected by ATS",
                     knockouts=[reason], checks=checks, fixes=fixes)


# --------------------------------------------------------------------------------------
# Main entry point
# --------------------------------------------------------------------------------------
def analyze_resume(data: bytes, filename: str, role: str = GENERAL, jd: str = "") -> AtsResult:
    try:
        pages, links = extract_pdf(data)
    except Exception as exc:  # noqa: BLE001
        return _failed(filename, f"Could not read PDF: {exc}")

    text = _clean("\n".join(pages))
    if len(text.strip()) < 150:
        return _failed(filename, "No selectable text found - this looks like a scanned/image PDF, "
                                 "so an ATS would see a blank resume.", pages=len(pages))

    lines = [re.sub(r"\s+", " ", l).strip() for l in text.splitlines()]
    lines = [l for l in lines if l]
    n_words = len(re.findall(r"\b[\w+#.'-]+\b", text))
    n_pages = len(pages)
    sections, nonstandard = split_sections(lines)
    found_sections = [s for s, body in sections.items() if s != "header" and body]
    link_text = text + "\n" + "\n".join(links)

    email = EMAIL_RE.search(text)
    phone = PHONE_RE.search(text)
    linkedin = LINKEDIN_RE.search(link_text)
    github = GITHUB_RE.search(link_text)
    portfolio = OTHER_URL_RE.search("\n".join(links) + "\n" + "\n".join(lines[:12]))

    # ---------------- Resume detection ----------------
    signals = {
        "Email address": bool(email),
        "Phone number": bool(phone),
        "2+ standard sections (Education / Skills / Experience ...)": len(found_sections) >= 2,
        "Degree / education terms": bool(DEGREE_RE.search(text)),
        "Date ranges (e.g. 2024 - Present)": bool(DATE_RANGE_RE.search(text)),
        "Resume vocabulary (skills, projects, experience ...)": len(RESUME_VOCAB_RE.findall(text)) >= 3,
    }
    confidence = sum(signals.values()) / len(signals)
    is_resume = confidence >= 0.5 and len(found_sections) >= 2 and n_words >= 80

    if not is_resume:
        rows = []
        for sig, ok in signals.items():
            _check(rows, "Resume detection", sig, 1.0 if ok else 0.0, 1,
                   "Found" if ok else "Not found", "A resume should contain this.")
        checks = pd.DataFrame(rows)
        fixes = pd.DataFrame([{
            "Priority": "High", "Area": "Resume detection",
            "Problem": f"Document does not look like a resume (confidence {confidence:.0%}).",
            "Action": "Upload an actual resume PDF with contact details and standard sections "
                      "(Education, Skills, Projects/Experience)."}])
        return AtsResult(filename=filename, pages=n_pages, words=n_words, is_resume=False,
                         confidence=confidence, signals=signals, verdict="Not a resume",
                         knockouts=["Document is not a resume"], sections=found_sections,
                         checks=checks, fixes=fixes, text=text)

    rows: list[dict] = []
    skills_text = " ".join(sections.get("skills", []))
    body_text = " ".join(" ".join(sections.get(s, [])) for s in
                         ("summary", "experience", "projects", "achievements", "certifications"))

    # ---------------- 1. Parsing & format ----------------
    _check(rows, "Parsing & format", "Readable text", 1, 4, f"{n_words} words extracted")
    pg_ratio = 1.0 if n_pages <= 2 else 0.5 if n_pages == 3 else 0.0
    _check(rows, "Parsing & format", "Length", pg_ratio, 4,
           f"{n_pages} page(s)",
           "Cut to 1 page (fresher / <3 yrs) or 2 pages max. Remove old, weak or irrelevant content.")
    wc_ratio = 1.0 if 300 <= n_words <= 900 else 0.6 if 200 <= n_words < 300 or 900 < n_words <= 1200 else 0.2
    _check(rows, "Parsing & format", "Word count", wc_ratio, 3, f"{n_words} words (ideal 300-900)",
           "Add concrete project/experience detail." if n_words < 300 else "Trim filler; keep it concise.")
    garbled = sum(1 for c in text if c in "\ufffd" or 0xE000 <= ord(c) <= 0xF8FF and c not in "\uf0b7\uf0a7")
    g_ratio = garbled / max(len(text), 1)
    _check(rows, "Parsing & format", "Clean characters (no garbled glyphs)", 1.0 if g_ratio < 0.01 else 0.3, 3,
           f"{garbled} unreadable symbols",
           "Icons/special fonts are being read as junk. Use plain text, standard fonts (Arial/Calibri/Times) "
           "and replace icons with words (e.g. 'Email:', 'GitHub:').")
    body_lines = [l for s, ls in sections.items() if s not in ("header", "skills") for l in ls]
    short = sum(1 for l in body_lines if len(l.split()) <= 2)
    short_ratio = short / max(len(body_lines), 1)
    layout_bad = len(body_lines) >= 15 and short_ratio > 0.55
    _check(rows, "Parsing & format", "Single-column, table-free layout", 0.3 if layout_bad else 1.0, 3,
           f"{short_ratio:.0%} of lines are 1-2 words" + (" (possible columns/tables)" if layout_bad else ""),
           "Use a single-column layout. Avoid tables, text boxes, side-bars and skill-rating bars; "
           "many ATS read them out of order.")
    stem = re.sub(r"\.pdf$", "", filename, flags=re.I)
    bad_name = bool(re.search(r"(?i)\(\d+\)|final|copy|\bnew\b|latest|untitled|document|\bdoc\b|resume\s*\d|cv\s*\d", stem))
    _check(rows, "Parsing & format", "Professional file name", 0.3 if bad_name else 1.0, 1,
           f"'{filename}'", "Rename to Firstname_Lastname_Resume.pdf")

    # ---------------- 2. Contact ----------------
    first = lines[0] if lines else ""
    name_ok = 2 <= len(first.split()) <= 4 and re.fullmatch(r"[A-Za-z .'\-]+", first) is not None and not _heading(first)
    _check(rows, "Contact info", "Name at top", 1.0 if name_ok else 0.3, 2,
           f"First line: '{first[:50]}'", "Put your full name alone on the first line, largest font.")
    local = email.group().split("@")[0] if email else ""
    unprof = bool(re.search(r"\d{4,}", local)) or bool(re.search(r"(?i)cool|sexy|hotty|lover|dude|baby|king|queen", local))
    e_ratio = 0.0 if not email else 0.5 if unprof else 1.0
    _check(rows, "Contact info", "Professional email", e_ratio, 3,
           email.group() if email else "No email found",
           "Add an email." if not email else "Use a name-based email (firstname.lastname@gmail.com).")
    _check(rows, "Contact info", "Phone number", 1.0 if phone else 0.0, 3,
           phone.group().strip() if phone else "No phone found", "Add a 10-digit phone number in the header.")
    _check(rows, "Contact info", "LinkedIn URL", 1.0 if linkedin else 0.0, 2,
           linkedin.group() if linkedin else "Not found",
           "Add linkedin.com/in/<your-id> as visible text (not just an icon).")
    _check(rows, "Contact info", "GitHub / portfolio link", 1.0 if (github or portfolio) else 0.0, 2,
           (github.group() if github else portfolio.group() if portfolio else "Not found"),
           "Add your GitHub or portfolio URL as visible text.")

    # ---------------- 3. Sections ----------------
    has = lambda s: bool(sections.get(s))  # noqa: E731
    _check(rows, "Sections", "Experience or Projects", 1.0 if (has("experience") or has("projects")) else 0.0, 6,
           ", ".join(s for s in ("experience", "projects") if has(s)) or "Missing",
           "Add a Projects (or Internships) section; freshers are judged mainly on projects.")
    _check(rows, "Sections", "Education", 1.0 if has("education") else 0.0, 5,
           "Found" if has("education") else "Missing", "Add an 'Education' section.")
    _check(rows, "Sections", "Skills", 1.0 if has("skills") else 0.0, 5,
           "Found" if has("skills") else "Missing", "Add a 'Skills' section - ATS keyword matching depends on it.")
    _check(rows, "Sections", "Projects", 1.0 if has("projects") else 0.0, 3,
           "Found" if has("projects") else "Missing", "Add 2-4 relevant projects with tech stack and results.")
    _check(rows, "Sections", "Summary / Objective", 1.0 if has("summary") else 0.4, 2,
           "Found" if has("summary") else "Missing",
           "Add a 2-3 line summary: role + top skills + one achievement.")
    _check(rows, "Sections", "Certifications / Achievements",
           1.0 if (has("certifications") or has("achievements")) else 0.3, 2,
           ", ".join(s for s in ("certifications", "achievements") if has(s)) or "Missing",
           "Add relevant certifications, hackathons or awards.")
    if nonstandard:
        _check(rows, "Sections", "Standard section headings", 0.2, 2,
               "; ".join(f"'{a}' -> '{b}'" for a, b in nonstandard),
               "Rename creative headings to the standard ones shown; ATS parsers look for exact names.")
    else:
        _check(rows, "Sections", "Standard section headings", 1.0, 2, "All headings are standard")

    # ---------------- 4. Education ----------------
    edu_text = " ".join(sections.get("education", []))
    deg = DEGREE_RE.search(edu_text or text)
    yr = re.search(r"(?:19|20)\d{2}", edu_text)
    gpa = re.search(r"(?i)\b(?:cgpa|gpa|percentage|aggregate)\b|\d{2}(?:\.\d+)?\s?%", edu_text)
    ed_ratio = (0.5 if deg else 0) + (0.3 if yr else 0) + (0.2 if gpa else 0)
    _check(rows, "Education", "Degree, year & grade stated", ed_ratio, 3,
           f"degree: {'yes' if deg else 'no'}, year: {'yes' if yr else 'no'}, grade: {'yes' if gpa else 'no'}",
           "State degree, institution, graduation year and CGPA/percentage in one line each.")

    # ---------------- 5. Keywords ----------------
    kw_df = pd.DataFrame(columns=["Keyword", "Status", "Found in", "Suggestion"])
    kw_source, kw_match = "", None
    if jd.strip():
        specs, kw_source = jd_keywords(jd), "job description"
    elif role in ROLE_KEYWORDS:
        specs, kw_source = ROLE_KEYWORDS[role], f"{role} skill bank"
    else:
        specs = []
    if specs:
        krows, matched = [], 0
        in_body = 0
        for spec in specs:
            pat = _kw_pattern(spec)
            in_sk = bool(pat.search(skills_text))
            in_bd = bool(pat.search(body_text))
            anywhere = bool(pat.search(text))
            canon = spec.split("|")[0]
            if anywhere:
                matched += 1
                in_body += in_bd
                where = ("Skills + Projects/Experience" if in_sk and in_bd else "Skills only" if in_sk
                         else "Projects/Experience only" if in_bd else "Elsewhere")
                tip = "Also use it in a project bullet." if where == "Skills only" else ""
                krows.append([canon, "✅ Found", where, tip])
            else:
                krows.append([canon, "❌ Missing", "-",
                              f"Add '{canon}' to Skills (only if you really know it) and use it in a bullet, e.g. "
                              f"'Built <project> using {canon} to <result>'."])
        kw_df = pd.DataFrame(krows, columns=["Keyword", "Status", "Found in", "Suggestion"])
        kw_df = kw_df.sort_values("Status", ascending=False, kind="stable").reset_index(drop=True)
        kw_match = matched / len(specs)
        missing = [r[0] for r in krows if r[1].startswith("❌")]
        _check(rows, "Keywords", f"Keyword match ({kw_source})", kw_match, 30,
               f"{matched}/{len(specs)} matched ({kw_match:.0%})",
               "Missing: " + ", ".join(missing[:12]) + ". Add the ones you genuinely have to Skills and to project bullets.",
               pass_at=0.7, warn_at=0.4)
        if matched and has("skills") and (has("projects") or has("experience")):
            ctx = in_body / matched
            _check(rows, "Keywords", "Skills proven in projects/experience", ctx, 3,
                   f"{in_body}/{matched} matched skills also appear in project/experience text",
                   "Recruiters distrust skills that only appear in a list. Mention each key skill in a project bullet.",
                   pass_at=0.6, warn_at=0.3)

    # ---------------- 6. Content quality ----------------
    bullets = _bullets(sections)
    b_rows = []
    if bullets:
        strong = [_is_strong_verb(_first_word(b)) for b in bullets]
        metric = [_has_metric(b) for b in bullets]
        v_ratio, m_ratio = sum(strong) / len(bullets), sum(metric) / len(bullets)
        _check(rows, "Content quality", "Bullets start with action verbs", v_ratio / 0.7, 5,
               f"{sum(strong)}/{len(bullets)} bullets ({v_ratio:.0%}); target 70%+",
               "Start every bullet with a strong past-tense verb: Built, Developed, Automated, Optimized, Deployed.")
        _check(rows, "Content quality", "Quantified achievements", m_ratio / 0.4, 5,
               f"{sum(metric)}/{len(bullets)} bullets ({m_ratio:.0%}); target 40%+",
               "Add numbers: accuracy %, users, records, time saved, response time, team size.")
        long_b = [b for b in bullets if len(b.split()) > 32]
        _check(rows, "Content quality", "Concise bullets", 1.0 if not long_b else 0.5, 2,
               f"{len(long_b)} bullet(s) over 32 words", "Split or shorten bullets to 1-2 lines (under 30 words).")
        for b, s, m in zip(bullets, strong, metric):
            if s and m:
                continue
            tips = []
            if not s:
                tips.append("Start with a strong verb (Built / Developed / Automated / Optimized)")
            if not m:
                tips.append("Add a number (%, users, rows, ms, hours saved)")
            b_rows.append({"Bullet": b[:140] + ("..." if len(b) > 140 else ""),
                           "Strong verb": "✅" if s else "❌", "Has metric": "✅" if m else "❌",
                           "Improve by": "; ".join(tips),
                           "Pattern": "Built <what> using <tech> that <result: +X% / N users / Y ms>"})
    else:
        _check(rows, "Content quality", "Bullets start with action verbs", 0.0, 5,
               "No bullet points detected under Experience/Projects",
               "Describe each project/role in 2-4 bullets starting with action verbs.")
        _check(rows, "Content quality", "Quantified achievements", 0.0, 5,
               "No bullets to evaluate", "Add measurable results to every project/role.")
        _check(rows, "Content quality", "Concise bullets", 0.5, 2, "No bullets to evaluate", "Use short bullets.")

    # ---- weak phrases, clichés, personal info, first-person ----
    repl_rows = []
    weak_hits = 0
    for ln in lines:
        for pat, repl, why in WEAK_PHRASES:
            for m in re.finditer(pat, ln, flags=re.I):
                weak_hits += 1
                repl_rows.append({"Type": "Weak phrase", "Found in": ln[:110], "Replace / remove": m.group(),
                                  "With / do": repl, "Why": why})
    _check(rows, "Content quality", "Weak / vague phrases", 1 - min(weak_hits, 5) / 5, 4,
           f"{weak_hits} found", "Replace each weak phrase using the 'Replacements' tab.")
    cliche_hits = 0
    for ln in lines:
        for pat, repl in CLICHES:
            for m in re.finditer(pat, ln, flags=re.I):
                cliche_hits += 1
                repl_rows.append({"Type": "Cliché / buzzword", "Found in": ln[:110], "Replace / remove": m.group(),
                                  "With / do": repl, "Why": "Generic; adds no keyword or proof"})
    _check(rows, "Content quality", "Clichés & buzzwords", 1 - min(cliche_hits, 4) / 4, 2,
           f"{cliche_hits} found", "Delete buzzwords and show the proof instead.")
    pron = [l for l in lines if "hereby" not in l.lower() and re.search(r"\b(?:I|my|me|myself)\b", l)]
    for l in pron[:6]:
        m = re.search(r"\b(?:I|my|me|myself)\b", l)
        repl_rows.append({"Type": "First-person pronoun", "Found in": l[:110], "Replace / remove": m.group(),
                          "With / do": "Remove pronouns; start with a verb ('Built ...')",
                          "Why": "Resumes are written without 'I / my'"})
    _check(rows, "Content quality", "No first-person pronouns", 1 - min(len(pron), 4) / 4, 2,
           f"{len(pron)} line(s) use I/my/me", "Rewrite those lines without pronouns.")
    pi_hits = []
    for pat, label in PERSONAL_INFO:
        for ln in lines:
            if re.search(pat, ln, flags=re.I):
                pi_hits.append(label)
                repl_rows.append({"Type": "Outdated personal info", "Found in": ln[:110], "Replace / remove": label,
                                  "With / do": "Delete it", "Why": "Not used for screening; can introduce bias; wastes space"})
                break
    _check(rows, "Content quality", "No outdated personal details", 1.0 if not pi_hits else 0.3, 2,
           ", ".join(pi_hits) if pi_hits else "None found",
           "Remove DOB, marital status, parents' names, religion, photo and the 'Declaration' paragraph.")
    for old, new in nonstandard:
        repl_rows.append({"Type": "Section heading", "Found in": old, "Replace / remove": old, "With / do": new,
                          "Why": "ATS parsers map only standard headings"})

    # ---- date format consistency ----
    styles = set()
    if re.search(rf"\b{MONTHS_ABBR}\.?\s+\d{{4}}\b", text):
        styles.add("Mon YYYY")
    if re.search(rf"\b{MONTHS_FULL}\s+\d{{4}}\b", text):
        styles.add("Month YYYY")
    if re.search(r"\b\d{1,2}[/.]\d{4}\b", text):
        styles.add("MM/YYYY")
    _check(rows, "Content quality", "Consistent date format", 1.0 if len(styles) <= 1 else 0.4, 2,
           ", ".join(sorted(styles)) or "Year-only / none", "Use one format everywhere, e.g. 'Jan 2025 - Mar 2025'.")

    # ---------------- Skills section richness ----------------
    if has("skills"):
        items = [i.strip() for i in re.split(r"[,|;•\n:]", " \n".join(sections["skills"])) if i.strip()]
        items = [i for i in items if 1 <= len(i.split()) <= 4]
        _check(rows, "Sections", "Skills section has enough skills", min(len(items) / 10, 1.0), 2,
               f"~{len(items)} skills listed", "List 10-20 relevant skills, grouped (Languages, Libraries, Tools).")

    # ---------------- Score ----------------
    checks = pd.DataFrame(rows)
    earned, maximum = checks["Earned"].sum(), checks["Max"].sum()
    score = round(100 * earned / maximum, 1)

    knockouts = []
    if not email:
        knockouts.append("No email address")
    if not phone:
        knockouts.append("No phone number")

    # ---------------- Fix list ----------------
    fx = checks[checks["_status"] != "Pass"].copy()
    fx["Lost"] = fx["Max"] - fx["Earned"]
    fx = fx.sort_values("Lost", ascending=False)
    fx["Priority"] = fx["Lost"].apply(lambda x: "High" if x >= 4 else "Medium" if x >= 2 else "Low")
    fixes = pd.DataFrame({
        "Priority": fx["Priority"], "Area": fx["Category"] + " - " + fx["Check"],
        "Problem": fx["Details"], "Action": fx["Fix"],
    }).reset_index(drop=True)

    # missing keywords as concrete additions
    if specs:
        for _, r in kw_df[kw_df["Status"].str.startswith("❌")].head(10).iterrows():
            repl_rows.append({"Type": "Missing keyword", "Found in": "-", "Replace / remove": "(nothing)",
                              "With / do": f"Add '{r['Keyword']}' to Skills + a project bullet", "Why": "Keyword gap vs " + kw_source})

    return AtsResult(
        filename=filename, pages=n_pages, words=n_words, is_resume=True, confidence=confidence, signals=signals,
        score=score, verdict=_verdict(score), knockouts=knockouts, keyword_source=kw_source,
        keyword_match=None if kw_match is None else round(100 * kw_match, 1), sections=found_sections,
        checks=checks.drop(columns=["_status"]), keywords=kw_df, fixes=fixes,
        replacements=pd.DataFrame(repl_rows, columns=["Type", "Found in", "Replace / remove", "With / do", "Why"]),
        bullets=pd.DataFrame(b_rows).head(25), text=text,
    )
