import unittest
from placementiq import data, model, gaps, career, resume
from placementiq.config import LABELS, ROLES
from placementiq.validation import is_valid_full_name, is_valid_technical_domain

class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.df = data.generate(600); cls.b = model.train(cls.df, save=False)
    def test_data_valid(self): data.validate(self.df, need_label=True); self.assertEqual(set(self.df.label), set(LABELS))
    def test_bad_csv(self):
        with self.assertRaises(ValueError): data.validate(self.df.drop(columns="dsa"))
        bad = self.df.copy(); bad.loc[0, "cgpa"] = 14
        with self.assertRaises(ValueError): data.validate(bad)
    def test_predict(self):
        lab, p = model.predict(self.b, self.df.head(5)); self.assertTrue(set(lab) <= set(LABELS)); self.assertAlmostEqual(p.iloc[0].sum(), 1.0)
    def test_gaps(self):
        top = dict(cgpa=9, dsa=95, core_cs=95, aptitude=95, communication=95, projects=5, internships=2)
        for r in ROLES:
            s, rows = gaps.analyze(top, r); self.assertEqual(s, 100.0); self.assertTrue(all(x["severity"] == "Met" for x in rows))
        s, rows = gaps.analyze(dict(top, dsa=20), "Software Developer")
        self.assertEqual(rows[0]["key"], "dsa"); self.assertEqual(rows[0]["severity"], "Critical")
    def test_career_roadmap(self):
        profile = {"programming_skills": ["Python", "SQL"], "branch": "Artificial Intelligence and Machine Learning",
                   "aptitude_level": "Intermediate", "programming_level": "Beginner"}
        recs = career.recommend_domain(profile)
        self.assertIn("Machine Learning", [x[0] for x in recs])
        plan = career.build_roadmap("Frontend Development", {"programming_level": "Beginner"}, 8)
        self.assertEqual(plan["url"], "https://roadmap.sh/frontend")
        self.assertEqual(len(plan["phases"]), 3)
        video_name, video_url = career.youtube_for_phase(
            "Cybersecurity", "Intermediate", "web security", "Burp Suite Community"
        )
        self.assertEqual(video_name, "Focused YouTube learning videos")
        self.assertIn("youtube.com/results?search_query=", video_url)
        self.assertNotIn(" ", video_url)
        self.assertIn("PortSwigger", video_url)

    def test_weights(self):
        for r in ROLES.values(): self.assertAlmostEqual(sum(r["weight"].values()), 1.0)
    def test_full_name_validation(self):
        for name in ("Kartik Kumar", "Élodie Martin"):
            self.assertTrue(is_valid_full_name(name))
        for name in ("", "   ", "Kartik123", "Kartik-Kumar", "Kartik@Kumar"):
            self.assertFalse(is_valid_full_name(name))
    def test_technical_domain_validation(self):
        for domain in ("Robotics Engineering", "Data Technology", "Cybersecurity"):
            self.assertTrue(is_valid_technical_domain(domain))
        for domain in ("Business Management", "Fine Arts", ""):
            self.assertFalse(is_valid_technical_domain(domain))
    def test_resume_ats_analysis(self):
        text = """Alex Kumar
alex@example.com +91 9876543210
SUMMARY
Software developer with Python and SQL experience.
SKILLS
Python, JavaScript, React, SQL, Docker, Git
PROJECTS
- Built an API serving 10,000 users and reduced response time by 30%.
EDUCATION
B.Tech Computer Science
"""
        result = resume.analyze_resume(text)
        self.assertTrue(result["is_resume"])
        self.assertGreaterEqual(result["score"], 80)
        self.assertEqual(result["status"], "Strong ATS match")
    def test_resume_rejects_non_resume_document(self):
        result = resume.analyze_resume(
            "Invoice 2026\nProducts and services\nAmount due: 5000\nPayment terms and conditions."
        )
        self.assertFalse(result["is_resume"])
        self.assertEqual(result["status"], "Not a resume")
        self.assertIsNone(result["score"])
if __name__ == "__main__": unittest.main()
