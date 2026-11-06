import re

from pypdf import PdfReader
from pypdf.errors import PdfReadError


SECTION_NAMES = {
    "summary", "objective", "education", "experience", "work experience",
    "projects", "skills", "technical skills", "certifications",
    "achievements", "coursework", "internships",
}
SECTION_ALIASES = {
    "summary": ("summary", "profile", "about me"),
    "education": ("education", "academic background"),
    "experience": ("experience", "work experience", "employment"),
    "projects": ("projects", "personal projects"),
    "skills": ("skills", "technical skills", "technologies"),
    "certifications": ("certifications", "certificates"),
    "achievements": ("achievements", "awards"),
    "internships": ("internships", "internship experience"),
}
TECHNICAL_TERMS = {
    "python", "java", "javascript", "typescript", "sql", "c++", "react",
    "node", "fastapi", "django", "aws", "azure", "docker", "kubernetes",
    "git", "linux", "tensorflow", "pytorch", "scikit-learn", "html", "css",
    "postgresql", "mongodb", "machine learning", "data analysis",
    "cybersecurity", "rest api",
}


def extract_resume_text(file_obj) -> str:
    """Extract text from a PDF resume and reject image-only or unreadable files."""
    try:
        text = "\n".join(page.extract_text() or "" for page in PdfReader(file_obj).pages)
    except (OSError, PdfReadError, ValueError) as exc:
        raise ValueError("Could not read this PDF resume.") from exc
    text = re.sub(r"[ \t]+", " ", text).strip()
    if len(text) < 80:
        raise ValueError("This PDF has too little readable text. Upload a text-based PDF, not a scanned image.")
    return text


def analyze_resume(text: str) -> dict:
    """Return a transparent, ATS-style resume score and actionable suggestions."""
    lowered = text.lower()
    words = re.findall(r"\b[\w+#.-]+\b", lowered)
    sections = {
        section for section, aliases in SECTION_ALIASES.items()
        if any(re.search(rf"(?mi)^\s*{re.escape(alias)}\s*:?\s*$", text) for alias in aliases)
    }
    technical_terms = sorted(term for term in TECHNICAL_TERMS if term in lowered)
    quantified = len(re.findall(r"\b\d+(?:\.\d+)?%?\b", text))
    bullets = len(re.findall(r"(?m)^\s*[-•*]\s+", text))
    email_found = bool(re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.I))
    phone_found = bool(re.search(r"(?<!\d)(?:\+?\d[\d ()-]{8,}\d)(?!\d)", text))
    detection_checks = {
        "Email address": email_found,
        "Phone number": phone_found,
        "Resume sections": len(sections) >= 2,
        "Education or experience": bool({"education", "experience", "internships"} & sections),
        "Skills or projects": bool({"skills", "projects"} & sections),
    }
    detection_score = sum((25, 20, 25, 15, 15)[index] for index, passed in enumerate(detection_checks.values()) if passed)
    is_resume = (
        email_found
        and phone_found
        and len(sections) >= 2
        and bool({"education", "experience", "internships"} & sections)
        and bool({"skills", "projects"} & sections)
    )
    if not is_resume:
        return {
            "is_resume": False,
            "detection_score": detection_score,
            "score": None,
            "status": "Not a resume",
            "word_count": len(words),
            "sections": sorted(sections),
            "technical_terms": technical_terms,
            "checks": [(name, passed) for name, passed in detection_checks.items()],
            "suggestions": [
                "Upload a resume or CV PDF containing contact details and clear sections such as Education, Experience, Skills or Projects.",
                "Avoid uploading assignments, certificates, cover letters, invoices or other documents.",
            ],
        }

    checks = [
        ("Contact details", email_found and phone_found, 15, "Add a professional email address and phone number."),
        ("Core sections", len(sections) >= 4, 25, "Add clear sections such as Education, Experience, Projects and Skills."),
        ("Technical keywords", len(technical_terms) >= 5, 20, "Match relevant technical skills to the target role."),
        ("Readable structure", 1 <= len(text.splitlines()) <= 120 and len(words) <= 900, 15, "Keep the resume concise, scannable and ideally one or two pages."),
        ("Achievement evidence", quantified >= 2 or bullets >= 4, 15, "Use bullet points with measurable outcomes, such as percentages, scale or time saved."),
        ("Text parseability", "\n" in text and len(words) >= 120, 10, "Use selectable text and standard headings instead of text inside images or complex graphics."),
    ]
    score = sum(weight for _, passed, weight, _ in checks if passed)
    suggestions = [suggestion for _, passed, _, suggestion in checks if not passed]
    return {
        "is_resume": True,
        "detection_score": detection_score,
        "score": score,
        "status": "Strong ATS match" if score >= 80 else "Needs improvement" if score >= 55 else "Low ATS match",
        "word_count": len(words),
        "pages": None,
        "sections": sorted(sections),
        "technical_terms": technical_terms,
        "checks": [(name, passed) for name, passed, _, _ in checks],
        "suggestions": suggestions,
    }
