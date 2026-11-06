# Career Compass — Student Career Guidance & Learning Roadmap

Career Compass is a Streamlit mini-project that guides a student through a multi-step assessment, recommends a software career domain, shows a learning roadmap, and tracks completed roadmap phases. The existing placement-cell cohort analysis and Random Forest demonstration model are retained.

## Features

1. Student profile: name, CGPA, branch, programming skills, programming level, optional project and internship counts.
2. Communication assessment: English level, presentation, group discussion and interview confidence.
3. Aptitude assessment: overall level, logical reasoning, quantitative aptitude, verbal ability and problem solving.
4. Career domain selection across 14 software domains, or profile-based recommendations when the student is unsure.
5. Career report: role-fit benchmark score, model category, strengths, focus areas and skill-gap chart.
6. Domain-specific beginner/intermediate/advanced learning phases, with phase-specific course links and an interactive weekly plan.
7. Phase completion tracker, weekly study routine and downloadable text report.
8. Placement-cell cohort PDF analysis and model information. The PDF must be text-based and contain the ordered header `cgpa, dsa, core_cs, aptitude, communication, projects, internships`; each following row should contain seven numeric values.

## Run in VS Code (Windows)

1. Install Python 3.10 or newer and VS Code.
2. Extract `placementiq.zip` to a folder.
3. In VS Code, select **File → Open Folder** and open the extracted `placementiq` folder.
4. Open **Terminal → New Terminal**. Ensure the terminal is in the project root (the folder containing `requirements.txt`).
5. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, run this once in that terminal, then activate again:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

6. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

7. Start the website:

   ```powershell
   python -m streamlit run app/app.py
   ```

8. Open the local address printed in the terminal, normally `http://localhost:8501`.

### Run tests

```powershell
python -m unittest discover -s tests -v
```

You can also double-click `run.bat` after installing dependencies, or run `run_tests.bat` to execute the tests.

## Project structure

```text
placementiq/
├── app/app.py                 # Streamlit multi-step UI and dashboard
├── placementiq/
│   ├── career.py              # Domain recommendations and roadmap definitions
│   ├── config.py              # Model features, labels and role benchmarks
│   ├── data.py                # Synthetic training data and CSV validation
│   ├── gaps.py                # Explainable score, gap analysis and report
│   └── model.py               # Random Forest training and prediction
├── tests/test_core.py
├── requirements.txt
└── README.md
```

## Important project limitations

- This ZIP contains a Streamlit application, not a separate React frontend/backend. The redesign preserves the existing Python + Streamlit architecture.
- The supplied Random Forest is trained on synthetic demonstration data. Its readiness label and metrics are **not** validated placement predictions. For a credible model, retrain using anonymised historical placement outcomes from your institution.
- The assessment converts self-reported levels and selected technologies into approximate model inputs. A language selected in a form is not proof of proficiency; use the result as coaching guidance, not as an objective examination.
- Domain recommendations are explainable profile-based heuristics, while the readiness category comes from the existing ML model. No external LLM API is configured in this project. To add an LLM, implement a server-side API integration and keep its key in environment variables.
- Student data and checked roadmap phases currently live in Streamlit session state; there is no database or cross-device persistence. Add authenticated storage (for example, SQLite/PostgreSQL) before using this with real student records.
- Roadmap links are external references. The app does not scrape or embed roadmap.sh content; its own phase summaries are project guidance and should be reviewed as technologies change.

## Responsible use

Use the application to guide learning and placement preparation, never to exclude students. Obtain consent before collecting personal data, restrict access to student records, and use anonymised data for model training.
