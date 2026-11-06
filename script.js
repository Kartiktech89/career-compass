const STORAGE_KEY = "placement-preparation-student-plan";
const state = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
let currentStep = 1;

const domainPlans = {
  "Web Development": {
    time: "6–9 months", note: "At 8–10 focused hours per week, you can build a portfolio with 3 strong projects.",
    resources: [["MDN Web Docs", "Free · The web platform reference", "https://developer.mozilla.org/"], ["freeCodeCamp", "Free · Guided practice and projects", "https://www.freecodecamp.org/"], ["The Odin Project", "Free · Full-stack curriculum", "https://www.theodinproject.com/"], ["Frontend Masters", "Paid · Deep technical courses", "https://frontendmasters.com/"]],
    roadmap: ["HTML, CSS & Git", "JavaScript & browser APIs", "A framework + backend", "Deploy 3 portfolio projects"]
  },
  "Mobile App Development": {
    time: "6–10 months", note: "Start with one platform and ship small apps regularly before expanding.",
    resources: [["Android Developers", "Free · Official Android learning path", "https://developer.android.com/"], ["Flutter Docs", "Free · Cross-platform development", "https://docs.flutter.dev/"], ["CS50 Mobile", "Free · Harvard course", "https://cs50.harvard.edu/mobile/"], ["Udemy", "Paid · Project-based courses", "https://www.udemy.com/courses/development/mobile-apps/"]],
    roadmap: ["Programming foundations", "UI and navigation", "APIs, storage & auth", "Publish a polished app"]
  },
  "Data Science / Machine Learning": {
    time: "8–12 months", note: "Consistent practice with data projects matters more than rushing through theory.",
    resources: [["Kaggle Learn", "Free · Short, practical lessons", "https://www.kaggle.com/learn"], ["Python Docs", "Free · Official language reference", "https://docs.python.org/3/"], ["NPTEL", "Free · Academic foundations", "https://nptel.ac.in/"], ["Coursera", "Paid · Structured specializations", "https://www.coursera.org/browse/data-science"]],
    roadmap: ["Python & statistics", "Data cleaning and visualisation", "ML models & evaluation", "Deploy a useful model"]
  },
  Cybersecurity: {
    time: "8–12 months", note: "Build ethical, hands-on lab experience alongside your security fundamentals.",
    resources: [["OWASP", "Free · Web security standards", "https://owasp.org/"], ["TryHackMe", "Free + paid · Guided labs", "https://tryhackme.com/"], ["Cisco NetAcad", "Free · Networking foundations", "https://www.netacad.com/"], ["Coursera", "Paid · Security certificates", "https://www.coursera.org/browse/information-technology/cybersecurity"]],
    roadmap: ["Networking & Linux", "Security fundamentals", "Web and system labs", "Document a security portfolio"]
  },
  "DevOps / Cloud": {
    time: "6–10 months", note: "Learn by automating and deploying real applications, not just watching tutorials.",
    resources: [["AWS Skill Builder", "Free + paid · Cloud learning", "https://skillbuilder.aws/"], ["Docker Docs", "Free · Container fundamentals", "https://docs.docker.com/get-started/"], ["Linux Journey", "Free · Linux basics", "https://linuxjourney.com/"], ["KodeKloud", "Paid · Hands-on DevOps labs", "https://kodekloud.com/"]],
    roadmap: ["Linux, Git & scripting", "Containers and CI/CD", "Cloud fundamentals", "Operate a production project"]
  },
  "Game Development": {
    time: "8–12 months", note: "A small, finished game teaches more than an ambitious project you never ship.",
    resources: [["Unity Learn", "Free · Official guided tutorials", "https://learn.unity.com/"], ["Godot Docs", "Free · Open-source engine", "https://docs.godotengine.org/"], ["Brackeys", "Free · YouTube tutorials", "https://www.youtube.com/@Brackeys"], ["Udemy", "Paid · Complete game courses", "https://www.udemy.com/courses/development/game-development/"]],
    roadmap: ["Engine and programming basics", "2D mechanics and UI", "Level design & polish", "Release a playable game"]
  },
  Other: {
    time: "6–12 months", note: "Choose a focused outcome and use projects to turn your curiosity into evidence.",
    resources: [["roadmap.sh", "Free · Community learning roadmaps", "https://roadmap.sh/"], ["YouTube", "Free · Explore expert-led tutorials", "https://www.youtube.com/"], ["NPTEL", "Free · University-level courses", "https://nptel.ac.in/"], ["Udemy", "Paid · Broad course catalogue", "https://www.udemy.com/"]],
    roadmap: ["Choose fundamentals", "Follow a guided curriculum", "Build small projects", "Publish and get feedback"]
  }
};

const careerHubs = {
  "Frontend Development": {
    goal: "Build professional websites and user interfaces.",
    resources: [["HTML, CSS and web fundamentals", "https://developer.mozilla.org/en-US/docs/Learn_web_development"], ["Practice HTML, CSS and JavaScript", "https://www.freecodecamp.org/learn/"], ["JavaScript fundamentals", "https://javascript.info/"], ["Git and GitHub", "https://skills.github.com/"], ["React", "https://react.dev/learn"], ["Web accessibility", "https://www.w3.org/WAI/fundamentals/"], ["Projects and practice", "https://www.frontendmentor.io/"]],
    order: "HTML → CSS → Responsive Design → JavaScript → Git/GitHub → React → Accessibility → Projects → Deployment."
  },
  "Full Stack Development": {
    goal: "Build complete web applications, including frontend, backend and databases.",
    resources: [["Complete web development curriculum", "https://www.theodinproject.com/"], ["JavaScript and Node.js", "https://nodejs.org/en/learn"], ["Backend development with Node.js", "https://fullstackopen.com/en/"], ["React frontend", "https://react.dev/learn"], ["SQL and PostgreSQL", "https://www.postgresql.org/docs/current/tutorial.html"], ["REST APIs", "https://developer.mozilla.org/en-US/docs/Web/HTTP"], ["Deployment and hosting", "https://docs.github.com/en/pages"]],
    order: "HTML/CSS → JavaScript → Git → React → Node.js → APIs → SQL → Authentication → Testing → Deployment."
  },
  "Data Science": {
    goal: "Analyze data, build predictive models and solve problems using machine learning.",
    resources: [["Python", "https://www.kaggle.com/learn/python"], ["Data analysis with Pandas", "https://www.kaggle.com/learn/pandas"], ["Statistics fundamentals", "https://www.khanacademy.org/math/statistics-probability"], ["Data visualization", "https://www.kaggle.com/learn/data-visualization"], ["Machine learning", "https://www.kaggle.com/learn/intro-to-machine-learning"], ["Deep learning", "https://www.kaggle.com/learn/intro-to-deep-learning"], ["Machine learning library", "https://scikit-learn.org/stable/getting_started.html"], ["Projects and datasets", "https://www.kaggle.com/datasets"]],
    order: "Python → Statistics → NumPy/Pandas → Data Visualization → SQL → Machine Learning → Model Evaluation → Projects."
  },
  "Data Analytics": {
    goal: "Turn data into reports, dashboards and business decisions.",
    resources: [["Excel training", "https://support.microsoft.com/en-us/excel"], ["SQL practice", "https://sqlbolt.com/"], ["Python fundamentals", "https://www.kaggle.com/learn/python"], ["Pandas data analysis", "https://www.kaggle.com/learn/pandas"], ["Power BI", "https://learn.microsoft.com/en-us/training/powerplatform/power-bi/"], ["Tableau learning resources", "https://www.tableau.com/learn/training"], ["Real datasets", "https://ourworldindata.org/"]],
    order: "Excel → SQL → Data Cleaning → Statistics → Power BI or Tableau → Python Basics → Dashboards → Portfolio Projects."
  },
  "Cybersecurity": {
    goal: "Understand systems, identify vulnerabilities and learn defensive security.",
    resources: [["Networking fundamentals", "https://skillsforall.com/"], ["Linux fundamentals", "https://linuxjourney.com/"], ["Cybersecurity beginner training", "https://tryhackme.com/"], ["Web security training", "https://portswigger.net/web-security"], ["Security practice challenges", "https://overthewire.org/wargames/"], ["Cybersecurity certifications and learning", "https://www.cisco.com/site/us/en/learn/training-certifications/index.html"], ["OWASP security guidance", "https://owasp.org/www-project-top-ten/"]],
    order: "Networking → Linux → Operating Systems → Security Fundamentals → Web Security → Hands-on Labs → Defensive Monitoring → Projects.",
    note: "Practice only in authorized labs and systems you own or have permission to test."
  },
  "Cloud Computing": {
    goal: "Deploy and manage applications, storage, networks and cloud infrastructure.",
    resources: [["Cloud fundamentals", "https://learn.microsoft.com/en-us/training/azure/"], ["AWS cloud training", "https://skillbuilder.aws/"], ["Google Cloud learning", "https://cloud.google.com/learn"], ["Linux fundamentals", "https://linuxjourney.com/"], ["Docker", "https://docs.docker.com/get-started/"], ["Kubernetes basics", "https://kubernetes.io/docs/tutorials/kubernetes-basics/"], ["Cloud architecture guidance", "https://aws.amazon.com/architecture/"]],
    order: "Networking → Linux → Cloud Fundamentals → Compute → Storage → IAM/Security → Networking in the Cloud → Deployment → Monitoring.",
    note: "Training content may be free while some cloud labs or deployed resources require payment. Check costs before creating resources."
  },
  "DevOps Engineering": {
    goal: "Automate software delivery, infrastructure and application operations.",
    resources: [["Git and GitHub", "https://skills.github.com/"], ["Linux", "https://linuxjourney.com/"], ["Python scripting", "https://www.kaggle.com/learn/python"], ["Docker", "https://docs.docker.com/get-started/"], ["GitHub Actions CI/CD", "https://docs.github.com/en/actions"], ["Kubernetes", "https://kubernetes.io/docs/tutorials/"], ["Terraform infrastructure automation", "https://developer.hashicorp.com/terraform/tutorials"], ["DevOps roadmap", "https://roadmap.sh/devops"]],
    order: "Linux → Git → Scripting → Networking → Docker → CI/CD → Cloud → Terraform → Kubernetes → Monitoring."
  },
  "Android Development": {
    goal: "Build Android applications using modern Android development tools.",
    resources: [["Official Android development courses", "https://developer.android.com/courses"], ["Kotlin programming", "https://kotlinlang.org/docs/home.html"], ["Android Basics with Compose", "https://developer.android.com/courses/android-basics-compose/course"], ["Jetpack Compose", "https://developer.android.com/develop/ui/compose"], ["Android architecture", "https://developer.android.com/topic/architecture"], ["Android app testing", "https://developer.android.com/training/testing"], ["Publish an Android application", "https://developer.android.com/studio/publish"]],
    order: "Kotlin → Programming Fundamentals → Jetpack Compose → UI Layouts → State → App Architecture → APIs and Storage → Testing → App Release."
  },
  "Software Testing / QA": {
    goal: "Find defects, verify software quality and automate tests.",
    resources: [["Software testing concepts", "https://www.guru99.com/software-testing.html"], ["ISTQB syllabus and resources", "https://www.istqb.org/"], ["API testing with Postman", "https://learning.postman.com/"], ["Playwright browser automation", "https://playwright.dev/docs/intro"], ["Selenium automation", "https://www.selenium.dev/documentation/"], ["Git and GitHub", "https://skills.github.com/"], ["Testing practice", "https://www.ministryoftesting.com/"]],
    order: "Testing Fundamentals → Test Cases → Bug Reporting → Manual Testing → API Testing → SQL Basics → Automation → CI/CD → Testing Projects."
  },
  "UI/UX Design": {
    goal: "Design useful, accessible and visually consistent digital experiences.",
    resources: [["Figma design resources", "https://help.figma.com/"], ["UX design fundamentals", "https://www.nngroup.com/articles/"], ["User experience design principles", "https://lawsofux.com/"], ["Accessibility standards", "https://www.w3.org/WAI/"], ["Design systems", "https://m3.material.io/"], ["Design practice and challenges", "https://www.frontendmentor.io/"]],
    order: "Design Fundamentals → User Research → User Flows → Wireframes → Visual Design → Figma → Prototyping → Usability Testing → Portfolio Case Studies."
  },
  "Blockchain Development": {
    goal: "Build and test smart contracts and decentralized applications.",
    resources: [["Blockchain fundamentals and developer guides", "https://ethereum.org/en/developers/"], ["Solidity programming", "https://docs.soliditylang.org/en/latest/"], ["Smart contract tutorials", "https://cryptozombies.io/"], ["Ethereum development tools", "https://hardhat.org/docs"], ["Foundry development framework", "https://getfoundry.sh/introduction/overview/"], ["Web3 application development", "https://docs.ethers.org/"], ["Smart contract security", "https://ethereum.org/en/developers/docs/smart-contracts/security/"]],
    order: "Programming Fundamentals → Blockchain Concepts → Ethereum → Solidity → Smart Contracts → Development Tools → Testing → Security → Decentralized Application Projects."
  }
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

function value(name) {
  const selected = document.querySelector(`[name="${name}"]:checked`);
  return selected ? selected.value : "";
}

function showError(name, message) {
  const error = $(`[data-error-for="${name}"]`);
  if (error) error.textContent = message;
}

function clearErrors(panel) {
  panel.querySelectorAll(".error").forEach((error) => { error.textContent = ""; });
}

function validateStep(step) {
  const panel = $(`[data-panel="${step}"]`);
  clearErrors(panel);
  let valid = true;
  if (step === 1) {
    const name = $("#fullName").value.trim();
    const cgpa = Number($("#cgpa").value);
    if (!name) { showError("fullName", "Please enter your full name."); valid = false; }
    if ($("#cgpa").value === "" || !Number.isFinite(cgpa) || cgpa < 0 || cgpa > 10) { showError("cgpa", "CGPA must be between 0.00 and 10.00."); valid = false; }
    if (!$$('[name="programmingSkills"]:checked').length) { showError("programmingSkills", "Select at least one programming skill."); valid = false; }
  }
  if (step === 2) {
    ["communicationLevel", "englishLevel"].forEach((name) => { if (!value(name)) { showError(name, "Please choose an option."); valid = false; } });
  }
  if (step === 3) {
    ["aptitudeLevel", "logicalReasoning", "quantitativeAptitude", "verbalAbility", "problemSolving"].forEach((name) => { if (!value(name)) { showError(name, "Please choose a level."); valid = false; } });
  }
  if (step === 4 && !value("domain")) { showError("domain", "Choose a domain to continue."); valid = false; }
  return valid;
}

function collectAnswers() {
  state.fullName = $("#fullName").value.trim();
  state.cgpa = $("#cgpa").value;
  state.branch = $("#branch").value || "Not specified";
  state.programmingSkills = $$('[name="programmingSkills"]:checked').map((input) => input.value);
  state.programmingLevel = $("#programmingLevel").value;
  state.projectsCount = $("#projectsCount").value;
  state.internshipsCount = $("#internshipsCount").value;
  state.communicationLevel = value("communicationLevel");
  state.englishLevel = value("englishLevel");
  state.presentation = value("presentation");
  state.groupDiscussion = value("groupDiscussion");
  state.interviewConfidence = value("interviewConfidence");
  state.aptitudeLevel = value("aptitudeLevel");
  state.logicalReasoning = value("logicalReasoning");
  state.quantitativeAptitude = value("quantitativeAptitude");
  state.verbalAbility = value("verbalAbility");
  state.problemSolving = value("problemSolving");
  state.domain = value("domain");
  state.weeklyHours = $("#weeklyHours").value;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function updateProgress(step) {
  currentStep = step;
  $$(".progress-step").forEach((item) => {
    const number = Number(item.dataset.step);
    item.classList.toggle("active", number === step);
    item.classList.toggle("complete", number < step);
  });
  $("#progressBar").style.width = `${((step - 1) / 4) * 100}%`;
  $$(".step-panel").forEach((panel) => panel.classList.toggle("active", Number(panel.dataset.panel) === step));
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function renderResult() {
  const plan = domainPlans[state.domain] || domainPlans.Other;
  const hub = careerHubs[state.domain] || careerHubs["Frontend Development"];
  $("#resultTitle").textContent = `${state.fullName.split(" ")[0]}'s ${state.domain} plan is ready.`;
  $("#resultSubtitle").textContent = "A practical next step, built around where you are today.";
  $("#timeEstimate").textContent = plan.time;
  $("#timeNote").textContent = plan.note;
  const entries = [["Name", state.fullName], ["Branch", state.branch], ["CGPA", `${Number(state.cgpa).toFixed(2)} / 10`], ["Skills", state.programmingSkills.join(", ")], ["Programming", state.programmingLevel], ["Projects", state.projectsCount], ["Internships", state.internshipsCount], ["Communication", state.communicationLevel], ["English", state.englishLevel], ["Aptitude", state.aptitudeLevel], ["Domain", state.domain], ["Study time", `${state.weeklyHours} hrs/week`]];
  $("#profileSummary").innerHTML = entries.map(([label, text]) => `<div class="summary-item"><small>${label}</small><strong>${text}</strong></div>`).join("");
  $("#resources").innerHTML = plan.resources.map(([title, description, link]) => `<div class="resource"><b>${title}</b><span>${description}</span><a href="${link}" target="_blank" rel="noopener noreferrer">Explore resource ↗</a></div>`).join("");
  $("#hubGoal").textContent = `Goal: ${hub.goal}`;
  $("#hubResources").innerHTML = hub.resources.map(([title, link], index) => `<div class="hub-resource"><span>${String(index + 1).padStart(2, "0")}. ${title}</span><a href="${link}" target="_blank" rel="noopener noreferrer">Open ↗</a></div>`).join("");
  $("#hubOrder").textContent = hub.order;
  $("#hubNote").textContent = hub.note || "Free learning resources may include optional paid features or certificates. Build projects after each major topic and publish your work where appropriate.";
  $("#learningRoadmap").innerHTML = plan.roadmap.map((item, index) => `<div class="timeline-item"><b>0${index + 1}</b><span>${item}</span></div>`).join("");
}

function restoreSavedAnswers() {
  if (!state.fullName) return;
  $("#fullName").value = state.fullName;
  $("#cgpa").value = state.cgpa;
  $("#branch").value = state.branch === "Not specified" ? "" : state.branch;
  $("#programmingLevel").value = state.programmingLevel || "Beginner";
  $("#projectsCount").value = state.projectsCount || 0;
  $("#internshipsCount").value = state.internshipsCount || 0;
  $("#weeklyHours").value = state.weeklyHours || 8;
  $("#weeklyHoursValue").textContent = state.weeklyHours || 8;
  state.programmingSkills?.forEach((skill) => { const input = document.querySelector(`[name="programmingSkills"][value="${skill}"]`); if (input) input.checked = true; });
  ["communicationLevel", "englishLevel", "presentation", "groupDiscussion", "interviewConfidence", "aptitudeLevel", "logicalReasoning", "quantitativeAptitude", "verbalAbility", "problemSolving", "domain"].forEach((name) => { const input = document.querySelector(`[name="${name}"][value="${state[name]}"]`); if (input) input.checked = true; });
}

$$("[data-next]").forEach((button) => button.addEventListener("click", () => {
  const step = Number(button.dataset.next);
  if (!validateStep(step)) { $(".status-message").textContent = "Please review the highlighted fields before continuing."; return; }
  $(".status-message").textContent = "";
  collectAnswers();
  if (step === 4) { renderResult(); updateProgress(5); } else updateProgress(step + 1);
}));

$$("[data-back]").forEach((button) => button.addEventListener("click", () => updateProgress(Number(button.dataset.back) - 1)));
$("#editProfile").addEventListener("click", () => updateProgress(1));
$("#startOver").addEventListener("click", () => { localStorage.removeItem(STORAGE_KEY); window.location.reload(); });
$("#savePlan").addEventListener("click", () => {
  const text = `Career Compass learning plan for ${state.fullName}\nDomain: ${state.domain}\nEstimated time: ${($("#timeEstimate").textContent)}\n\nLearning roadmap:\n${(domainPlans[state.domain] || domainPlans.Other).roadmap.map((item, i) => `${i + 1}. ${item}`).join("\n")}\n\nProject milestones:\nWeek 1 - Define & research\nWeeks 2-3 - Build the foundation\nWeek 4 - Test & improve\nWeek 5 - Document & present`;
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([text], { type: "text/plain" }));
  link.download = "placement-preparation-learning-plan.txt";
  link.click();
  URL.revokeObjectURL(link.href);
});
restoreSavedAnswers();
$("#weeklyHours").addEventListener("input", (event) => { $("#weeklyHoursValue").textContent = event.target.value; });
