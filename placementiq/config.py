"""Single source of truth: features, labels, role benchmarks, palette."""
FEATURES = ["cgpa", "dsa", "core_cs", "aptitude", "communication", "projects", "internships"]
NAMES = {"cgpa": "CGPA", "dsa": "DSA & Coding", "core_cs": "Core CS (OS/DBMS/CN)",
         "aptitude": "Aptitude & Reasoning", "communication": "Communication",
         "projects": "Projects", "internships": "Internships"}
RANGES = {"cgpa": (0.0, 10.0), "dsa": (0, 100), "core_cs": (0, 100), "aptitude": (0, 100),
          "communication": (0, 100), "projects": (0, 6), "internships": (0, 3)}
SCALE = {"cgpa": 10, "dsa": 1, "core_cs": 1, "aptitude": 1, "communication": 1,
         "projects": 100 / 5, "internships": 100 / 2}
LABELS = ["Not Ready", "Needs Improvement", "Ready"]
# Per-role benchmark (percent scale) and weight (sums to 1). Tune with your placement cell.
ROLES = {
    "Software Developer": {
        "bench": dict(cgpa=65, dsa=70, core_cs=65, aptitude=60, communication=60, projects=60, internships=50),
        "weight": dict(cgpa=.08, dsa=.30, core_cs=.15, aptitude=.10, communication=.10, projects=.17, internships=.10)},
    "Data / ML Engineer": {
        "bench": dict(cgpa=70, dsa=55, core_cs=55, aptitude=65, communication=60, projects=80, internships=50),
        "weight": dict(cgpa=.10, dsa=.15, core_cs=.10, aptitude=.15, communication=.10, projects=.30, internships=.10)},
    "IT Services / Mass Recruiter": {
        "bench": dict(cgpa=60, dsa=45, core_cs=50, aptitude=70, communication=70, projects=40, internships=0),
        "weight": dict(cgpa=.15, dsa=.12, core_cs=.10, aptitude=.28, communication=.25, projects=.07, internships=.03)},
}
PALETTE = {"navy": "#0F2A43", "teal": "#0E7C86", "ok": "#2E7D32", "warn": "#B7791F",
           "bad": "#B42318", "muted": "#64748B", "bg": "#F5F7FA"}
