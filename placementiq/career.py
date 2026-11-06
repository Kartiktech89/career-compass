"""Domain guidance and transparent profile-to-roadmap personalization."""

from urllib.parse import urlencode

CAREER_HUBS = {
    "Frontend Development": {
        "goal": "Build professional websites and user interfaces.",
        "resources": [
            ("HTML, CSS and web fundamentals", "https://developer.mozilla.org/en-US/docs/Learn_web_development"),
            ("Practice HTML, CSS and JavaScript", "https://www.freecodecamp.org/learn/"),
            ("JavaScript fundamentals", "https://javascript.info/"),
            ("Git and GitHub", "https://skills.github.com/"),
            ("React", "https://react.dev/learn"),
            ("Web accessibility", "https://www.w3.org/WAI/fundamentals/"),
            ("Projects and practice", "https://www.frontendmentor.io/"),
        ],
        "order": "HTML → CSS → Responsive Design → JavaScript → Git/GitHub → React → Accessibility → Projects → Deployment.",
    },
    "Full Stack Development": {
        "goal": "Build complete web applications, including frontend, backend and databases.",
        "resources": [
            ("Complete web development curriculum", "https://www.theodinproject.com/"),
            ("JavaScript and Node.js", "https://nodejs.org/en/learn"),
            ("Backend development with Node.js", "https://fullstackopen.com/en/"),
            ("React frontend", "https://react.dev/learn"),
            ("SQL and PostgreSQL", "https://www.postgresql.org/docs/current/tutorial.html"),
            ("REST APIs", "https://developer.mozilla.org/en-US/docs/Web/HTTP"),
            ("Deployment and hosting", "https://docs.github.com/en/pages"),
        ],
        "order": "HTML/CSS → JavaScript → Git → React → Node.js → APIs → SQL → Authentication → Testing → Deployment.",
    },
    "Data Science": {
        "goal": "Analyze data, build predictive models and solve problems using machine learning.",
        "resources": [
            ("Python", "https://www.kaggle.com/learn/python"),
            ("Data analysis with Pandas", "https://www.kaggle.com/learn/pandas"),
            ("Statistics fundamentals", "https://www.khanacademy.org/math/statistics-probability"),
            ("Data visualization", "https://www.kaggle.com/learn/data-visualization"),
            ("Machine learning", "https://www.kaggle.com/learn/intro-to-machine-learning"),
            ("Deep learning", "https://www.kaggle.com/learn/intro-to-deep-learning"),
            ("Machine learning library", "https://scikit-learn.org/stable/getting_started.html"),
            ("Projects and datasets", "https://www.kaggle.com/datasets"),
        ],
        "order": "Python → Statistics → NumPy/Pandas → Data Visualization → SQL → Machine Learning → Model Evaluation → Projects.",
    },
    "Data Analytics": {
        "goal": "Turn data into reports, dashboards and business decisions.",
        "resources": [
            ("Excel training", "https://support.microsoft.com/en-us/excel"),
            ("SQL practice", "https://sqlbolt.com/"),
            ("Python fundamentals", "https://www.kaggle.com/learn/python"),
            ("Pandas data analysis", "https://www.kaggle.com/learn/pandas"),
            ("Power BI", "https://learn.microsoft.com/en-us/training/powerplatform/power-bi/"),
            ("Tableau learning resources", "https://www.tableau.com/learn/training"),
            ("Real datasets", "https://ourworldindata.org/"),
        ],
        "order": "Excel → SQL → Data Cleaning → Statistics → Power BI or Tableau → Python Basics → Dashboards → Portfolio Projects.",
    },
    "Cybersecurity": {
        "goal": "Understand systems, identify vulnerabilities and learn defensive security.",
        "resources": [
            ("Networking fundamentals", "https://skillsforall.com/"),
            ("Linux fundamentals", "https://linuxjourney.com/"),
            ("Cybersecurity beginner training", "https://tryhackme.com/"),
            ("Web security training", "https://portswigger.net/web-security"),
            ("Security practice challenges", "https://overthewire.org/wargames/"),
            ("Cybersecurity certifications and learning", "https://www.cisco.com/site/us/en/learn/training-certifications/index.html"),
            ("OWASP security guidance", "https://owasp.org/www-project-top-ten/"),
        ],
        "order": "Networking → Linux → Operating Systems → Security Fundamentals → Web Security → Hands-on Labs → Defensive Monitoring → Projects.",
        "note": "Practice only in authorized labs and systems you own or have permission to test.",
    },
    "Cloud Computing": {
        "goal": "Deploy and manage applications, storage, networks and cloud infrastructure.",
        "resources": [
            ("Cloud fundamentals", "https://learn.microsoft.com/en-us/training/azure/"),
            ("AWS cloud training", "https://skillbuilder.aws/"),
            ("Google Cloud learning", "https://cloud.google.com/learn"),
            ("Linux fundamentals", "https://linuxjourney.com/"),
            ("Docker", "https://docs.docker.com/get-started/"),
            ("Kubernetes basics", "https://kubernetes.io/docs/tutorials/kubernetes-basics/"),
            ("Cloud architecture guidance", "https://aws.amazon.com/architecture/"),
        ],
        "order": "Networking → Linux → Cloud Fundamentals → Compute → Storage → IAM/Security → Networking in the Cloud → Deployment → Monitoring.",
        "note": "Training content may be free while some cloud labs or deployed resources require payment. Check costs before creating resources.",
    },
    "DevOps Engineering": {
        "goal": "Automate software delivery, infrastructure and application operations.",
        "resources": [
            ("Git and GitHub", "https://skills.github.com/"),
            ("Linux", "https://linuxjourney.com/"),
            ("Python scripting", "https://www.kaggle.com/learn/python"),
            ("Docker", "https://docs.docker.com/get-started/"),
            ("GitHub Actions CI/CD", "https://docs.github.com/en/actions"),
            ("Kubernetes", "https://kubernetes.io/docs/tutorials/"),
            ("Terraform infrastructure automation", "https://developer.hashicorp.com/terraform/tutorials"),
            ("DevOps roadmap", "https://roadmap.sh/devops"),
        ],
        "order": "Linux → Git → Scripting → Networking → Docker → CI/CD → Cloud → Terraform → Kubernetes → Monitoring.",
    },
    "Android Development": {
        "goal": "Build Android applications using modern Android development tools.",
        "resources": [
            ("Official Android development courses", "https://developer.android.com/courses"),
            ("Kotlin programming", "https://kotlinlang.org/docs/home.html"),
            ("Android Basics with Compose", "https://developer.android.com/courses/android-basics-compose/course"),
            ("Jetpack Compose", "https://developer.android.com/develop/ui/compose"),
            ("Android architecture", "https://developer.android.com/topic/architecture"),
            ("Android app testing", "https://developer.android.com/training/testing"),
            ("Publish an Android application", "https://developer.android.com/studio/publish"),
        ],
        "order": "Kotlin → Programming Fundamentals → Jetpack Compose → UI Layouts → State → App Architecture → APIs and Storage → Testing → App Release.",
    },
    "Software Testing / QA": {
        "goal": "Find defects, verify software quality and automate tests.",
        "resources": [
            ("Software testing concepts", "https://www.guru99.com/software-testing.html"),
            ("ISTQB syllabus and resources", "https://www.istqb.org/"),
            ("API testing with Postman", "https://learning.postman.com/"),
            ("Playwright browser automation", "https://playwright.dev/docs/intro"),
            ("Selenium automation", "https://www.selenium.dev/documentation/"),
            ("Git and GitHub", "https://skills.github.com/"),
            ("Testing practice", "https://www.ministryoftesting.com/"),
        ],
        "order": "Testing Fundamentals → Test Cases → Bug Reporting → Manual Testing → API Testing → SQL Basics → Automation → CI/CD → Testing Projects.",
    },
    "UI/UX Design": {
        "goal": "Design useful, accessible and visually consistent digital experiences.",
        "resources": [
            ("Figma design resources", "https://help.figma.com/"),
            ("UX design fundamentals", "https://www.nngroup.com/articles/"),
            ("User experience design principles", "https://lawsofux.com/"),
            ("Accessibility standards", "https://www.w3.org/WAI/"),
            ("Design systems", "https://m3.material.io/"),
            ("Design practice and challenges", "https://www.frontendmentor.io/"),
        ],
        "order": "Design Fundamentals → User Research → User Flows → Wireframes → Visual Design → Figma → Prototyping → Usability Testing → Portfolio Case Studies.",
    },
    "Blockchain Development": {
        "goal": "Build and test smart contracts and decentralized applications.",
        "resources": [
            ("Blockchain fundamentals and developer guides", "https://ethereum.org/en/developers/"),
            ("Solidity programming", "https://docs.soliditylang.org/en/latest/"),
            ("Smart contract tutorials", "https://cryptozombies.io/"),
            ("Ethereum development tools", "https://hardhat.org/docs"),
            ("Foundry development framework", "https://getfoundry.sh/introduction/overview/"),
            ("Web3 application development", "https://docs.ethers.org/"),
            ("Smart contract security", "https://ethereum.org/en/developers/docs/smart-contracts/security/"),
        ],
        "order": "Blockchain Fundamentals → Ethereum → Solidity → Smart Contracts → Hardhat/Foundry → Web3 Apps → Testing → Security → Projects.",
    },
}

def learning_hub_for(domain):
    """Return the closest free learning hub for every selectable domain."""
    aliases = {
        "Artificial Intelligence": "Data Science",
        "Machine Learning": "Data Science",
        "Backend Development": "Full Stack Development",
        "Game Development": "Frontend Development",
    }
    return CAREER_HUBS.get(aliases.get(domain, domain), CAREER_HUBS["Full Stack Development"])

DOMAINS = {
    "Frontend Development": ("frontend", "Build accessible, responsive user interfaces.", "https://roadmap.sh/frontend", [
        ("Beginner", "HTML, CSS, JavaScript fundamentals; Git; responsive design", "HTML, CSS, JavaScript, Git", "4–6 weeks", "Build a personal portfolio and responsive landing page"),
        ("Intermediate", "DOM, async JavaScript, TypeScript, React, APIs, testing", "TypeScript, React, Vite, Jest", "6–8 weeks", "Build a job-board app using a public API"),
        ("Advanced", "Performance, accessibility, architecture, deployment", "Next.js, Playwright, Lighthouse", "4–6 weeks", "Deploy a polished full-stack portfolio project")]),
    "Backend Development": ("backend", "Design APIs, business logic, databases and services.", "https://roadmap.sh/backend", [
        ("Beginner", "One language, HTTP, Git, command line, SQL basics", "Python or Java, Git, PostgreSQL", "4–6 weeks", "Build a CRUD REST API"),
        ("Intermediate", "API design, authentication, database modelling, caching, testing", "FastAPI/Spring Boot, PostgreSQL, Redis", "6–8 weeks", "Build an authenticated task management API"),
        ("Advanced", "System design, queues, observability, security, deployment", "Docker, message queues, cloud platform", "4–6 weeks", "Deploy a monitored service with background jobs")]),
    "Full Stack Development": ("full-stack", "Develop complete applications across frontend and backend.", "https://roadmap.sh/full-stack", [
        ("Beginner", "HTML, CSS, JavaScript, Git and programming fundamentals", "HTML, CSS, JavaScript, Git", "5–7 weeks", "Create a responsive student profile site"),
        ("Intermediate", "React, backend APIs, SQL, authentication and testing", "React, Node.js, Express, PostgreSQL", "8–10 weeks", "Build a placement preparation portal"),
        ("Advanced", "Deployment, security, performance and system design", "Docker, CI/CD, cloud hosting", "5–7 weeks", "Deploy a complete application with role-based access")]),
    "Artificial Intelligence": ("ai-engineer", "Build applications that use modern AI models and techniques.", "https://roadmap.sh/ai-engineer", [
        ("Beginner", "Python, linear algebra basics, statistics and data handling", "Python, NumPy, pandas", "5–7 weeks", "Create a data exploration notebook"),
        ("Intermediate", "ML fundamentals, model evaluation, APIs and prompt workflows", "scikit-learn, FastAPI, model APIs", "8–10 weeks", "Build an AI-powered FAQ assistant"),
        ("Advanced", "RAG, embeddings, evaluation, deployment and responsible AI", "Vector databases, PyTorch, Docker", "6–8 weeks", "Build and evaluate a document question-answering system")]),
    "Machine Learning": ("machine-learning", "Train, evaluate and deploy predictive models.", "https://roadmap.sh/ai-data-scientist", [
        ("Beginner", "Python, statistics, data cleaning and visualisation", "Python, NumPy, pandas, Matplotlib", "5–7 weeks", "Analyse and visualise a public dataset"),
        ("Intermediate", "Regression, classification, feature engineering and validation", "scikit-learn, Jupyter", "8–10 weeks", "Build a well-evaluated prediction model"),
        ("Advanced", "Deep learning, deployment, monitoring and model explainability", "PyTorch, MLflow, FastAPI", "6–8 weeks", "Deploy a monitored ML inference API")]),
    "Data Science": ("ai-data-scientist", "Turn data into insights and predictive models.", "https://roadmap.sh/ai-data-scientist", [
        ("Beginner", "Python, spreadsheets, SQL, statistics and visualisation", "Python, SQL, pandas", "5–7 weeks", "Create an exploratory data analysis report"),
        ("Intermediate", "Hypothesis testing, ML, feature engineering and storytelling", "scikit-learn, Power BI or Tableau", "8–10 weeks", "Complete an end-to-end analytics project"),
        ("Advanced", "Experiment design, advanced ML and reproducible pipelines", "Jupyter, MLflow, cloud data tools", "6–8 weeks", "Publish a reproducible predictive analytics project")]),
    "Data Analytics": ("sql", "Query, analyse and communicate business data.", "https://roadmap.sh/sql", [
        ("Beginner", "Spreadsheets, SQL basics and descriptive statistics", "Excel, SQL", "3–5 weeks", "Analyse a sales dataset"),
        ("Intermediate", "Joins, CTEs, dashboards and data storytelling", "PostgreSQL, Power BI", "5–7 weeks", "Build an interactive KPI dashboard"),
        ("Advanced", "Data modelling, automation and analytical experimentation", "Python, dbt basics, BI tools", "4–6 weeks", "Create an automated reporting pipeline")]),
    "Cybersecurity": ("cyber-security", "Understand systems, networks and defensive security.", "https://roadmap.sh/cyber-security", [
        ("Beginner", "Networking, Linux, operating systems and security basics", "Linux, Wireshark", "5–7 weeks", "Document a home-lab network security review"),
        ("Intermediate", "Web security, scripting, threat modelling and logging", "Python, Burp Suite Community, SIEM concepts", "8–10 weeks", "Complete legal beginner labs and write findings"),
        ("Advanced", "Incident response, cloud security and secure architecture", "Cloud IAM, detection tools", "6–8 weeks", "Create an incident-response playbook")]),
    "Cloud Computing": ("aws", "Deploy and operate reliable cloud infrastructure.", "https://roadmap.sh/aws", [
        ("Beginner", "Linux, networking, virtualisation and cloud concepts", "Linux, Git, cloud fundamentals", "4–6 weeks", "Deploy a static website"),
        ("Intermediate", "Compute, storage, IAM, networking and databases", "AWS/Azure/GCP, Terraform basics", "6–8 weeks", "Deploy a web app with managed database"),
        ("Advanced", "Infrastructure as code, reliability, monitoring and security", "Terraform, Docker, Kubernetes", "6–8 weeks", "Build a repeatable cloud deployment")]),
    "DevOps Engineering": ("devops", "Automate software delivery and infrastructure operations.", "https://roadmap.sh/devops", [
        ("Beginner", "Linux, Git, networking and shell scripting", "Linux, Bash, Git", "4–6 weeks", "Automate a local development task"),
        ("Intermediate", "CI/CD, containers, cloud and infrastructure as code", "Docker, GitHub Actions, Terraform", "7–9 weeks", "Create a CI/CD pipeline for an app"),
        ("Advanced", "Kubernetes, observability, reliability and security", "Kubernetes, Prometheus", "6–8 weeks", "Deploy and monitor a containerised service")]),
    "Android Development": ("android", "Build mobile applications for Android devices.", "https://roadmap.sh/android", [
        ("Beginner", "Kotlin basics, OOP and Android fundamentals", "Kotlin, Android Studio", "5–7 weeks", "Build a simple notes app"),
        ("Intermediate", "Layouts, navigation, APIs, persistence and architecture", "Jetpack Compose, Room, Retrofit", "7–9 weeks", "Build an app consuming a REST API"),
        ("Advanced", "Testing, performance, accessibility and release process", "JUnit, Compose testing", "4–6 weeks", "Publish a release-ready portfolio app")]),
    "Software Testing / QA": ("qa", "Improve software quality through systematic testing.", "https://roadmap.sh/qa", [
        ("Beginner", "SDLC, test cases, bug reports and testing fundamentals", "TestRail concepts, browser devtools", "3–5 weeks", "Write test cases for a sample website"),
        ("Intermediate", "API testing, SQL, automation and regression testing", "Postman, Selenium or Playwright", "6–8 weeks", "Automate a user registration test flow"),
        ("Advanced", "CI integration, performance and test strategy", "GitHub Actions, JMeter", "4–6 weeks", "Build a CI test suite")]),
    "UI/UX Design": ("ux-design", "Research users and design usable digital experiences.", "https://roadmap.sh/ux-design", [
        ("Beginner", "Design principles, user needs, wireframes and visual hierarchy", "Figma", "3–5 weeks", "Redesign a college website screen"),
        ("Intermediate", "Prototyping, usability testing and design systems", "Figma components, FigJam", "5–7 weeks", "Prototype and test a student workflow"),
        ("Advanced", "Accessibility, product strategy and portfolio case studies", "Figma, accessibility checklists", "4–6 weeks", "Publish a complete UX case study")]),
    "Blockchain Development": ("blockchain", "Understand distributed ledgers and smart-contract development.", "https://roadmap.sh/blockchain", [
        ("Beginner", "JavaScript or Solidity basics, cryptography concepts and networks", "JavaScript, Solidity", "5–7 weeks", "Build a simple local smart contract"),
        ("Intermediate", "Smart contracts, testing, wallets and web3 integration", "Hardhat, ethers.js", "7–9 weeks", "Build a testnet-based dApp"),
        ("Advanced", "Contract security, audits and decentralised architecture", "Foundry, static analysis tools", "5–7 weeks", "Test and document a secure contract")]),
}

LEVELS = {"Beginner": 25, "Basic": 40, "Intermediate": 60, "Advanced": 80, "Fluent": 90}

RESOURCE_LINKS = {
    "HTML": ("MDN HTML", "https://developer.mozilla.org/en-US/docs/Learn/HTML"),
    "CSS": ("MDN CSS", "https://developer.mozilla.org/en-US/docs/Learn/CSS"),
    "JavaScript": ("freeCodeCamp JavaScript", "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures-v8/"),
    "Python": ("Python for Everybody", "https://www.py4e.com/"),
    "SQL": ("SQLBolt", "https://sqlbolt.com/"),
    "Git": ("GitHub Skills", "https://skills.github.com/"),
    "React": ("React Learn", "https://react.dev/learn"),
    "TypeScript": ("TypeScript Handbook", "https://www.typescriptlang.org/docs/handbook/intro.html"),
    "PostgreSQL": ("PostgreSQL Tutorial", "https://www.postgresql.org/docs/current/tutorial.html"),
    "scikit-learn": ("scikit-learn Tutorials", "https://scikit-learn.org/stable/getting_started.html"),
    "NumPy": ("NumPy Learn", "https://numpy.org/learn/"),
    "pandas": ("pandas Getting Started", "https://pandas.pydata.org/docs/getting_started/intro_tutorials/"),
    "Docker": ("Docker Get Started", "https://docs.docker.com/get-started/"),
    "Kotlin": ("Kotlin Koans", "https://play.kotlinlang.org/koans/overview"),
    "Figma": ("Figma Learn", "https://help.figma.com/hc/en-us/categories/360002051613"),
}

VIDEO_SEARCH_TERMS = {
    "Cybersecurity": {
        "Beginner": "cybersecurity fundamentals networking Linux Professor Messer",
        "Intermediate": "web security Burp Suite OWASP PortSwigger threat modeling SIEM",
        "Advanced": "incident response cloud security threat detection SANS OWASP",
    },
    "Frontend Development": {
        "Beginner": "HTML CSS JavaScript fundamentals MDN freeCodeCamp",
        "Intermediate": "React TypeScript frontend testing official tutorial",
        "Advanced": "frontend performance accessibility architecture web.dev",
    },
    "Backend Development": {
        "Beginner": "HTTP REST API SQL backend development freeCodeCamp",
        "Intermediate": "FastAPI Spring Boot PostgreSQL authentication testing",
        "Advanced": "backend system design observability security deployment",
    },
}

def resources_for_phase(topics, tools, roadmap_url):
    """Return practical course links relevant to a roadmap phase."""
    haystack = f"{topics} {tools}"
    resources = [value for key, value in RESOURCE_LINKS.items() if key.lower() in haystack.lower()]
    if not resources:
        resources.append(("Roadmap.sh phase guide", roadmap_url))
    return resources[:4]


def youtube_for_phase(domain, phase, topics, tools):
    """Return a focused YouTube search link using trusted topic cues."""
    query = VIDEO_SEARCH_TERMS.get(domain, {}).get(
        phase, f"{domain} {phase} tutorial {topics} {tools}"
    )
    return ("Focused YouTube learning videos", f"https://www.youtube.com/results?{urlencode({'search_query': query})}")


def recommend_domain(profile):
    """Heuristic suggestions only; explainable fallback when user has no preference."""
    skills = set(profile.get("programming_skills", []))
    branch = profile.get("branch", "")
    scores = {d: 0 for d in DOMAINS}
    if skills & {"Python"}: 
        for d in ("Artificial Intelligence", "Machine Learning", "Data Science", "Data Analytics", "Backend Development"): scores[d] += 2
    if skills & {"JavaScript", "HTML & CSS"}:
        for d in ("Frontend Development", "Full Stack Development", "UI/UX Design"): scores[d] += 2
    if skills & {"Java", "C", "C++"}:
        for d in ("Backend Development", "Android Development", "Software Testing / QA"): scores[d] += 1
    if skills & {"SQL"}:
        for d in ("Data Analytics", "Data Science", "Backend Development"): scores[d] += 1
    if "Artificial Intelligence" in branch:
        for d in ("Artificial Intelligence", "Machine Learning", "Data Science"): scores[d] += 2
    if profile.get("aptitude_level") in ("Advanced", "Intermediate"):
        for d in ("Machine Learning", "Data Science", "Cybersecurity"): scores[d] += 1
    return sorted(scores.items(), key=lambda x: (-x[1], x[0]))[:3]


def build_roadmap(domain, profile, weekly_hours=8):
    key, description, url, phases = DOMAINS[domain]
    # Hours/week are used to scale a transparent estimate; phase ranges remain guidance.
    factor = max(0.5, min(2.0, 8 / max(weekly_hours, 4)))
    level = profile.get("programming_level", "Beginner")
    start = 0 if level in ("Beginner", "Basic") else 1
    selected = phases[start:]
    return {"description": description, "url": url, "phases": selected,
            "estimated_months": round(sum((5 if "weeks" in p[3] else 6) for p in selected) * factor / 4.3, 1),
            "weekly_hours": weekly_hours}
