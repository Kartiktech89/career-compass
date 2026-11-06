import re
import numpy as np, pandas as pd
from .config import FEATURES, RANGES, LABELS

def generate(n=1500, seed=42):
    """SYNTHETIC data: hidden ability factor + noisy labels (not a deterministic rule).
    Replace with real outcomes via the Cohort tab / load_csv()."""
    r = np.random.default_rng(seed); a = r.normal(size=n)
    s = lambda base, k, sd: np.clip(base + k * a + r.normal(0, sd, n), 0, 100).round()
    df = pd.DataFrame({
        "cgpa": np.clip(6.8 + .9 * a + r.normal(0, .5, n), 4, 10).round(2),
        "dsa": s(52, 16, 11), "core_cs": s(55, 14, 11), "aptitude": s(58, 13, 12),
        "communication": s(58, 10, 14),
        "projects": np.clip(np.round(2 + .8 * a + r.normal(0, 1, n)), 0, 6),
        "internships": np.clip(np.round(.8 + .6 * a + r.normal(0, .7, n)), 0, 3)})
    z = a + r.normal(0, .55, n)
    df["label"] = np.where(z > .6, "Ready", np.where(z < -.5, "Not Ready", "Needs Improvement"))
    return df

def validate(df, need_label=False):
    miss = [c for c in FEATURES + (["label"] if need_label else []) if c not in df.columns]
    if miss: raise ValueError(f"Missing columns: {miss}")
    df = df.copy()
    for c in FEATURES:
        df[c] = pd.to_numeric(df[c], errors="coerce")
        lo, hi = RANGES[c]
        bad = df[c].isna() | (df[c] < lo) | (df[c] > hi)
        if bad.any(): raise ValueError(f"'{c}' must be numeric in [{lo}, {hi}] (rows {list(df.index[bad][:5])})")
    if need_label:
        unk = set(df["label"]) - set(LABELS)
        if unk: raise ValueError(f"Unknown labels {unk}; allowed {LABELS}")
    return df

def load_csv(f, need_label=False): return validate(pd.read_csv(f), need_label)

def load_pdf(f, need_label=False):
    """Extract cohort rows from a text-based PDF table.

    PDF text extraction does not preserve the visual table grid reliably, so
    headers and numeric cells are parsed independently of line breaks.
    """
    try:
        from pypdf import PdfReader
        from pypdf.errors import PdfReadError
    except ImportError as e:
        raise ValueError("PDF support requires the pypdf package.") from e

    try:
        text = "\n".join(page.extract_text() or "" for page in PdfReader(f).pages)
    except (OSError, PdfReadError) as e:
        raise ValueError("Could not read the uploaded PDF.") from e

    normalized = re.sub(r"[^a-z0-9_]+", " ", text.lower()).replace("core cs", "core_cs")
    header_pattern = r"\b" + r"\s+".join(map(re.escape, FEATURES)) + r"\b"
    if not re.search(header_pattern, normalized):
        raise ValueError("PDF must contain a table header with: " + ", ".join(FEATURES))

    number = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)"
    header_end = re.search(header_pattern, normalized).end()
    tokens = normalized[header_end:].split()
    rows = []
    numeric_values = []
    for token in tokens:
        if re.fullmatch(number, token):
            if len(numeric_values) == len(FEATURES):
                rows.append(dict(zip(FEATURES, map(float, numeric_values))))
                numeric_values = []
            numeric_values.append(token)
    if len(numeric_values) == len(FEATURES):
        rows.append(dict(zip(FEATURES, map(float, numeric_values))))
    labels = re.findall(r"\b(?:not ready|needs improvement|ready)\b", normalized[header_end:], re.I)
    if len(labels) == len(rows):
        for row, label in zip(rows, labels):
            row["label"] = next(value for value in LABELS if value.lower() == label.lower())
    if not rows:
        raise ValueError("PDF does not contain any readable cohort rows.")
    return validate(pd.DataFrame(rows), need_label)
