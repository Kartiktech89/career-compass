from .config import FEATURES, NAMES, SCALE, ROLES

TASKS = {
 "dsa": ["Solve 2 easy/medium problems daily (arrays, strings, hashing, two pointers)", "Second week: recursion, trees, binary search; time every solve", "Weekly: one 90-minute mock contest"],
 "core_cs": ["Revise OS (processes, scheduling, deadlock) and DBMS (normalisation, SQL joins)", "Write 10 SQL queries daily on a sample database", "Summarise Computer Networks layers on one page"],
 "aptitude": ["30 timed aptitude questions daily (percentages, ratios, time-work)", "Review every wrong answer in an error log", "Weekly: one full-length timed mock"],
 "communication": ["Record a 2-minute self-introduction; rewrite and re-record 3 times", "Practise 5 HR questions aloud daily (STAR format)", "Do 2 peer mock interviews this fortnight"],
 "projects": ["Pick one project; add a README, tests and a live demo link", "Be able to explain design trade-offs in 3 minutes", "Publish on GitHub with a clean commit history"],
 "internships": ["Apply to 5 internships per week (LinkedIn, Internshala, college cell)", "Contribute to one open-source issue as proof of work", "Complete one paid or volunteer micro-project"],
 "cgpa": ["Prioritise backlog clearance and upcoming internal exams", "Check CGPA cut-offs of your target companies"],
}
RES = {"dsa": "LeetCode, NeetCode roadmap, GeeksforGeeks", "core_cs": "Gate Smashers, college notes, SQL practice sheets",
       "aptitude": "IndiaBIX, R.S. Aggarwal, PrepInsta", "communication": "Pramp, Toastmasters, recorded self-review",
       "projects": "GitHub, Streamlit Cloud / Render for free hosting", "internships": "Internshala, LinkedIn, Wellfound", "cgpa": "Faculty mentors, past papers"}

def percent(profile): return {f: min(100.0, profile[f] * SCALE[f]) for f in FEATURES}

def analyze(profile, role):
    R, pct, rows = ROLES[role], percent(profile), []
    for f in FEATURES:
        b, w = R["bench"][f], R["weight"][f]; gap = max(0.0, b - pct[f])
        sev = "Critical" if gap >= 20 else "Moderate" if gap >= 8 else "Met"
        rows.append(dict(key=f, skill=NAMES[f], score=round(pct[f], 1), benchmark=b, gap=round(gap, 1),
                         severity=sev, priority=gap * w))
    score = sum(R["weight"][f] * (min(pct[f] / R["bench"][f], 1.0) if R["bench"][f] else 1.0) for f in FEATURES) * 100
    return round(score, 1), sorted(rows, key=lambda r: -r["priority"])

def sprint(rows, days=14):
    focus = [r for r in rows if r["severity"] != "Met"][:3]
    if not focus: return [("Days 1-14", "Maintain & polish", ["Weekly mock interviews and contests to stay sharp"], "")]
    per = days // len(focus); out = []
    for i, r in enumerate(focus):
        s, e = i * per + 1, days if i == len(focus) - 1 else (i + 1) * per
        out.append((f"Days {s}-{e}", r["skill"], TASKS[r["key"]], RES[r["key"]]))
    return out

def report(name, role, label, score, rows, plan):
    L = [f"Career Compass report - {name or 'Student'}", f"Target role: {role}", f"Readiness: {label} (score {score}/100)", "", "Skill gaps:"]
    L += [f"- {r['skill']}: {r['score']} vs {r['benchmark']} ({r['severity']})" for r in rows]
    L += ["", "14-day plan:"]
    for d, f, t, res in plan: L += [f"{d} - {f}"] + [f"  * {x}" for x in t] + ([f"  Resources: {res}"] if res else [])
    L += ["", "Decision-support only; not a guarantee of placement outcomes."]
    return "\n".join(L)
