import io
import sys, pathlib
from html import escape
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pandas as pd
import altair as alt
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle, SimpleDocTemplate, KeepTogether,
)
from placementiq import data, model, gaps, career
from placementiq import ats_engine
from placementiq.config import FEATURES, NAMES, RANGES, ROLES, PALETTE as P, LABELS
from placementiq.validation import is_valid_full_name, is_valid_technical_domain

st.set_page_config(page_title="Career Compass | Career Navigator", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")
if "dark_theme" not in st.session_state: st.session_state.dark_theme = False

st.markdown("""<style>
:root{--ink:#1f2328;--muted:#656d76;--line:#d0d7de;--panel:#ffffff;--accent:#0969da;--soft:#ddf4ff;--green:#1a7f37;--purple:#8250df;--canvas:#f6f8fa;--indigo:#6e40c9;--orange:#bc4c00}
html{font-size:16px}*,*:before,*:after{box-sizing:border-box}
html,body,[class*="css"]{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif;color:var(--ink);overflow-wrap:normal;word-break:normal}
.stApp{background:radial-gradient(circle at 8% 2%,#ddf4ff 0,transparent 24rem),radial-gradient(circle at 95% 18%,#fbefff 0,transparent 26rem),var(--canvas)}
.block-container{max-width:1180px;padding-top:1.5rem;padding-bottom:3rem}
.hero{background:linear-gradient(120deg,#1f2328 0%,#24292f 47%,#3b1f70 100%);padding:2rem 2.2rem;border:1px solid #57606a;border-radius:8px;color:#fff;margin-bottom:1.4rem;box-shadow:0 8px 24px #1f23283d;position:relative;overflow:hidden}.hero:before{content:'';position:absolute;width:380px;height:180px;background:linear-gradient(90deg,#0969da55,#8250df66);filter:blur(35px);right:-90px;bottom:-80px;transform:rotate(-12deg)}.hero:after{content:'';position:absolute;width:220px;height:220px;border:1px solid #ffffff20;border-radius:50%;right:-70px;top:-95px;box-shadow:0 0 0 28px #ffffff08,0 0 0 56px #ffffff05}
.hero h1{font-size:clamp(1.7rem,3vw,2.1rem);font-weight:600;color:white;margin:0;line-height:1.2}.hero p{color:#d0d7de;margin:.45rem 0 0;font-size:1rem;line-height:1.5}.hero-content{position:relative;z-index:1}.hero-badge{display:inline-flex;align-items:center;gap:.4rem;border:1px solid #8c959f;border-radius:6px;padding:.3rem .65rem;color:#f0f6fc;font-size:.74rem;font-weight:600;margin-bottom:.75rem}
.eyebrow{color:#79c0ff;font-weight:600;letter-spacing:.08em;text-transform:uppercase;font-size:.72rem}
.panel{background:rgba(255,255,255,.92);border:1px solid var(--line);border-radius:8px;padding:1.25rem 1.4rem;margin:.55rem 0;box-shadow:0 3px 10px #1f232812}
.step{font-size:.78rem;font-weight:600;color:var(--accent);letter-spacing:.06em;text-transform:uppercase}
.title{font-size:clamp(1.25rem,2.5vw,1.55rem);font-weight:600;line-height:1.25;margin:.2rem 0}.sub{color:var(--muted);margin-bottom:1rem;line-height:1.5}
.metric{background:linear-gradient(145deg,#fff,#f6f8fa);border:1px solid var(--line);padding:1rem;border-radius:8px;min-height:96px;overflow:hidden;box-shadow:0 2px 6px #1f232810}.metric .v{font-size:clamp(1.15rem,2vw,1.65rem);font-weight:600;color:var(--accent);line-height:1.25;overflow-wrap:break-word}.metric .k{color:var(--muted);font-size:.82rem;line-height:1.3}
.domain-card{border:1px solid var(--line);border-radius:8px;padding:1rem;background:linear-gradient(145deg,#fff,#f6f8fa);min-height:128px;overflow:hidden;box-shadow:0 2px 5px #1f23280c;transition:transform .2s,box-shadow .2s,border-color .2s}.domain-card:hover{transform:translateY(-3px);border-color:#54aeff;box-shadow:0 8px 18px #0969da24}.domain-card>div:first-child{display:inline-flex!important;align-items:center;justify-content:center;width:2.35rem;height:2.35rem;border-radius:8px;background:linear-gradient(135deg,#ddf4ff,#fbefff);margin-bottom:.35rem}.domain-card b{display:block;line-height:1.3;margin:.2rem 0}.domain-card .small-muted{line-height:1.4}
.assessment-card{border:1px solid #b6e3ff;border-radius:8px;padding:.85rem 1rem;background:linear-gradient(135deg,#f0f8ff,#fff 70%,#fbefff);min-height:108px;margin:.35rem 0;overflow:hidden;box-shadow:0 2px 6px #0969da12}
.assessment-card b{color:#0969da}.assessment-card span{color:var(--muted);font-size:.84rem}
.external-resource{display:flex;align-items:center;justify-content:space-between;gap:.7rem;border:1px solid var(--line);border-radius:6px;padding:.72rem .85rem;margin:.35rem 0;color:var(--accent);background:#fff;text-decoration:none!important;font-weight:600;line-height:1.3;overflow-wrap:normal;word-break:normal;transition:transform .2s,box-shadow .2s,background .2s}
.external-resource span:first-child{min-width:0}
.external-resource:hover{transform:translateY(-2px);background:#ddf4ff;box-shadow:0 5px 12px #0969da24}
.external-resource:active{animation:leaving-platform .8s ease-in-out}
.external-resource .arrow{font-size:1.15rem;animation:external-pulse 1.8s ease-in-out infinite;color:var(--accent)}
@keyframes external-pulse{0%,100%{transform:translateX(0);opacity:.65}50%{transform:translateX(4px);opacity:1}}
@keyframes leaving-platform{0%{transform:scale(1)}45%{transform:scale(.97);background:#dff3f3}100%{transform:scale(1)}}
.small-muted{color:var(--muted);font-size:.88rem}
div.stButton>button,div.stDownloadButton>button{border-radius:6px;font-weight:600;min-height:2.7rem;white-space:normal;line-height:1.25;border:1px solid var(--line);transition:transform .15s,box-shadow .15s}
div.stButton>button:hover,div.stDownloadButton>button:hover{transform:translateY(-1px);box-shadow:0 3px 8px #1f232826}
[data-testid="stFormSubmitButton"] button,[data-testid="stButton"] button[kind="primary"]{background:#2da44e;border-color:#1a7f37;color:#fff}
[data-testid="stFormSubmitButton"] button:hover,[data-testid="stButton"] button[kind="primary"]:hover{background:#1a7f37}
[data-testid="stMetricValue"],[data-testid="stMetricLabel"]{overflow-wrap:normal;word-break:normal}
[data-testid="stForm"]{background:#fff;border:1px solid var(--line);border-radius:6px;padding:1.2rem}
[data-testid="stWidgetLabel"] p{font-size:.88rem;font-weight:700;color:#304563}
[data-baseweb="input"],[data-baseweb="select"]{border-radius:9px}
[data-testid="stExpander"]{border:1px solid #e2e9f0;border-radius:14px;background:#fff;overflow:hidden}
[data-testid="stExpander"] details summary{font-weight:700;color:#193b5a}
[data-testid="stAlert"]{border-radius:11px}
[data-testid="stTabs"] button{font-weight:700}
.section-heading{display:flex;align-items:center;gap:.55rem;margin:1.35rem 0 .55rem;color:#193b5a;font-family:Manrope,sans-serif;font-weight:800;font-size:1.05rem}
.section-heading:before{content:'';width:4px;height:1.15rem;border-radius:3px;background:#2c9b9b}
.step-item{padding:.65rem .2rem;border-bottom:3px solid #dce4ec;color:#8290a2;text-align:center;font-size:.78rem;font-weight:700;line-height:1.3}.step-item.active{border-color:#16748b;color:#145d78}.step-item.done{border-color:#56b2a7;color:#287e78}.step-number{display:block;font-size:.9rem;margin-bottom:.15rem}
[data-testid="stProgressBar"]>div>div{background:#2da44e}
footer{visibility:hidden}
@media (max-width:640px){.block-container{padding-left:1rem;padding-right:1rem}.hero{padding:1.4rem}.panel{padding:1rem}.metric{padding:.75rem;min-height:84px}.metric .v{font-size:1.05rem}.domain-card{min-height:112px}.assessment-card{min-height:96px}}
</style>""", unsafe_allow_html=True)

if st.session_state.dark_theme:
    st.markdown("""<style>
    :root{--ink:#f0f6fc;--muted:#a8b3c2;--line:#3b4654;--panel:#17212b;--canvas:#0d1117;--soft:#172b3a}
    .stApp,[data-testid="stAppViewContainer"]{background:radial-gradient(circle at 8% 2%,#12304a 0,transparent 24rem),radial-gradient(circle at 95% 18%,#2b1742 0,transparent 26rem),#0d1117;color:#f0f6fc}
    [data-testid="stHeader"],header{background:#0d1117!important;border-bottom:1px solid #212b36!important}
    .block-container{color:#f0f6fc}
    .panel,.metric,.domain-card,.assessment-card,[data-testid="stForm"],[data-testid="stExpander"]{background:#17212b!important;border-color:#3b4654!important;color:#f0f6fc}
    .metric{background:linear-gradient(145deg,#17212b,#111820)!important}
    .domain-card{background:linear-gradient(145deg,#17212b,#111820)!important}
    .assessment-card{background:linear-gradient(135deg,#132c40,#17212b 70%,#2b1742)!important}
    .external-resource{background:#17212b;color:#79c0ff;border-color:#3b4654}
    .external-resource:hover{background:#1d3446}
    .sub,.small-muted,.metric .k,.assessment-card span{color:#a8b3c2!important}
    [data-testid="stWidgetLabel"] p,[data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] h1,[data-testid="stMarkdownContainer"] h2,[data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4,[data-testid="stMarkdownContainer"] h5,
    [data-testid="stMarkdownContainer"] strong,[data-testid="stMarkdownContainer"] b,
    [data-testid="stCaptionContainer"],[data-testid="stAlert"] *{color:#f0f6fc!important}
    [data-testid="stAppViewContainer"] label,[data-testid="stAppViewContainer"] legend,
    [data-testid="stAppViewContainer"] small,[data-testid="stAppViewContainer"] span,
    [data-testid="stAppViewContainer"] li{color:#f0f6fc}
    [data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-baseweb="select"]>div,
    [data-baseweb="input"],textarea{background:#0d1117!important;color:#f0f6fc!important;border-color:#3b4654}
    [data-baseweb="select"] *,[data-baseweb="input"] *{color:#f0f6fc!important}
    [data-baseweb="popover"],[role="listbox"],[role="option"]{background:#17212b!important;color:#f0f6fc!important}
    [role="option"]:hover,[aria-selected="true"]{background:#21435d!important;color:#fff!important}
    div.stButton>button,div.stDownloadButton>button,
    [data-testid="stFormSubmitButton"] button{color:#f0f6fc!important;background:#1f6feb;border-color:#58a6ff}
    div.stButton>button:hover,div.stDownloadButton>button:hover,
    [data-testid="stFormSubmitButton"] button:hover{background:#388bfd;border-color:#79c0ff}
    a{color:#79c0ff!important}
    [data-testid="stCode"],code{background:#161b22!important;color:#f0f6fc!important}
    [data-testid="stFileUploader"] section{background:#ffffff!important;border:1px solid #8b949e!important}
    [data-testid="stFileUploader"] section *,
    [data-testid="stFileUploader"] section small,
    [data-testid="stFileUploader"] section span,
    [data-testid="stFileUploader"] section p{color:#000000!important}
    [data-testid="stFileUploader"] section button{background:#f6f8fa!important;color:#000000!important;border-color:#8b949e!important}
    [data-testid="stExpander"]:has([data-testid="stFileUploader"]){background:#ffffff!important;border-color:#8b949e!important}
    [data-testid="stExpander"]:has([data-testid="stFileUploader"]) *,
    [data-testid="stExpander"]:has([data-testid="stFileUploader"]) p,
    [data-testid="stExpander"]:has([data-testid="stFileUploader"]) label,
    [data-testid="stExpander"]:has([data-testid="stFileUploader"]) span,
    [data-testid="stExpander"]:has([data-testid="stFileUploader"]) small,
    [data-testid="stExpander"]:has([data-testid="stFileUploader"]) h1,
    [data-testid="stExpander"]:has([data-testid="stFileUploader"]) h2,
    [data-testid="stExpander"]:has([data-testid="stFileUploader"]) h3{color:#000000!important}
    [data-testid="stExpander"]:has([data-testid="stFileUploader"]) [data-baseweb="select"]>div,
    [data-testid="stExpander"]:has([data-testid="stFileUploader"]) [data-baseweb="input"],
    [data-testid="stExpander"]:has([data-testid="stFileUploader"]) textarea{background:#ffffff!important;color:#000000!important;border-color:#8b949e!important}
    [data-testid="stExpander"]:has([data-testid="stFileUploader"]) [data-baseweb="select"] *,
    [data-testid="stExpander"]:has([data-testid="stFileUploader"]) [data-baseweb="input"] *{color:#000000!important}
    [data-testid="stExpander"]:has([data-testid="stFileUploader"]) button{color:#000000!important}
    [data-testid="stExpander"]:has([data-testid="stFileUploader"]) [data-testid="stAlert"]{background:#eef6fb!important;color:#000000!important}
    [data-testid="stMetric"]{background:#17212b!important;border:1px solid #3b4654!important;border-radius:8px;padding:.65rem}
    [data-testid="stMetric"] *,[data-testid="stMetricLabel"],[data-testid="stMetricValue"]{color:#f0f6fc!important}
    [data-testid="stMetricValue"]{font-size:1.35rem!important;color:#79c0ff!important}
    [data-testid="stTabs"] button,[data-testid="stTabs"] button p{color:#000000!important;background:#ffffff!important;border-radius:6px 6px 0 0}
    [data-testid="stTabs"] button[aria-selected="true"]{color:#000000!important;background:#dbeafe!important;border-bottom:3px solid #0969da!important}
    [data-testid="stDataFrame"],[data-testid="stDataEditor"]{background:#17212b!important}
    [data-testid="stDataFrame"] iframe{filter:none}
    [data-testid="stTextArea"] textarea{background:#0d1117!important;color:#f0f6fc!important;border-color:#3b4654!important}
    [data-testid="stTextArea"] label,[data-testid="stTextArea"] label p{color:#f0f6fc!important}
    [data-testid="stExpander"] [data-testid="stCaptionContainer"]{color:#c9d1d9!important}
    [data-testid="stExpander"] [data-testid="stTabs"]{background:#ffffff!important;border:1px solid #8b949e!important;border-radius:8px;padding:.35rem}
    [data-testid="stExpander"] details summary{color:#b9d7f0}
    hr,[data-testid="stSeparator"]{border-color:#3b4654!important;background:#3b4654!important}
    [data-testid="stCheckbox"]{background:#17212b;border:1px solid #58a6ff;border-radius:10px;padding:.35rem .7rem;box-shadow:0 3px 12px #0008}
    [data-testid="stCheckbox"] label,[data-testid="stCheckbox"] p{color:#f0f6fc!important;font-weight:700}
    .step-item{border-color:#3b4654;color:#8b98a8}.step-item.active{border-color:#58a6ff;color:#79c0ff}.step-item.done{border-color:#56b2a7;color:#7ee2d2}
    </style>""", unsafe_allow_html=True)

st.markdown("""<style>
:root{--ink:#172b4d;--muted:#6b7b93;--line:#e4eaf2;--panel:#ffffff;--accent:#3563e9;--teal:#18a999;--canvas:#f5f7fb}
.stApp{background:linear-gradient(180deg,#f8faff 0%,#f5f7fb 52%,#eef3f8 100%)}
.block-container{max-width:1220px;padding:2.25rem 3rem 4rem}
.hero{background:linear-gradient(120deg,#172b4d 0%,#244a82 58%,#3563e9 100%);border:0;border-radius:24px;padding:2.7rem 3rem;margin:0 0 2rem;box-shadow:0 20px 45px #294b8126}
.hero:before{background:radial-gradient(circle,#61d8cc66,transparent 65%);filter:blur(10px);right:-60px;bottom:-120px}
.hero:after{border-color:#ffffff20;box-shadow:0 0 0 28px #ffffff08,0 0 0 56px #ffffff05}
.hero-badge{border:1px solid #ffffff3d;border-radius:999px;padding:.42rem .8rem;font-size:.7rem;letter-spacing:.08em}
.hero h1{font-size:clamp(2rem,4vw,3rem);font-weight:750;letter-spacing:-.04em}
.hero p{color:#d8e6ff;font-size:1.04rem;max-width:540px}
.eyebrow{color:#8fe5da;font-size:.68rem;letter-spacing:.14em}
.step{color:var(--accent);font-size:.7rem;letter-spacing:.14em}
.title{color:var(--ink);font-size:clamp(1.6rem,2.7vw,2.05rem);font-weight:750;letter-spacing:-.035em;margin:.4rem 0 .45rem}
.sub{color:var(--muted);font-size:.95rem;max-width:680px}
.panel,.metric,.domain-card,.assessment-card,[data-testid="stForm"],[data-testid="stExpander"]{border:1px solid var(--line);border-radius:18px;background:var(--panel);box-shadow:0 8px 24px #294b8110}
.panel{padding:1.5rem 1.65rem;margin:.75rem 0}
.metric{min-height:122px;padding:1.35rem}
.metric .v{color:var(--ink);font-size:clamp(1.25rem,2vw,1.8rem);font-weight:750}
.metric .k{color:var(--muted);font-size:.78rem;margin-top:.4rem}
.domain-card{min-height:138px;padding:1.2rem;transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}
.domain-card:hover{border-color:#93aaf5;box-shadow:0 15px 28px #294b8120;transform:translateY(-3px)}
.domain-card>div:first-child{background:#edf1ff;border-radius:12px}
.assessment-card{background:linear-gradient(135deg,#f1fffc,#fff 70%);border-color:#c8eee8;min-height:116px;padding:1.1rem 1.2rem}
.assessment-card b{color:#147f75}
.external-resource{border:1px solid var(--line);border-radius:12px;padding:.9rem 1rem;background:#fbfcfe;color:var(--accent);transition:transform .2s ease,box-shadow .2s ease,background .2s ease}
.external-resource:hover{background:#f0f4ff;box-shadow:0 8px 18px #294b8118;transform:translateY(-2px)}
div.stButton>button,div.stDownloadButton>button,[data-testid="stFormSubmitButton"] button{border-radius:11px;min-height:2.9rem;font-weight:700;transition:transform .18s ease,box-shadow .18s ease,background .18s ease}
div.stButton>button:hover,div.stDownloadButton>button:hover,[data-testid="stFormSubmitButton"] button:hover{box-shadow:0 8px 18px #294b8122;transform:translateY(-1px)}
[data-testid="stFormSubmitButton"] button,[data-testid="stButton"] button[kind="primary"]{background:var(--accent);border-color:var(--accent)}
[data-testid="stFormSubmitButton"] button:hover,[data-testid="stButton"] button[kind="primary"]:hover{background:#294fca}
[data-testid="stForm"]{padding:1.6rem}
[data-testid="stWidgetLabel"] p{color:var(--ink);font-weight:700;font-size:.84rem}
[data-baseweb="input"],[data-baseweb="select"],[data-baseweb="textarea"]{border-radius:11px}
[data-testid="stTabs"] button{font-weight:700}
[data-testid="stProgressBar"]>div>div{background:linear-gradient(90deg,var(--teal),var(--accent))}
.step-item{border-bottom:3px solid #dfe6f0;color:#9aa8ba;padding:.8rem .2rem}
.step-item.active{border-color:var(--accent);color:var(--accent)}
.step-item.done{border-color:var(--teal);color:#16877c}
@media (max-width:760px){.block-container{padding:1.2rem 1rem 3rem}.hero{border-radius:18px;padding:1.8rem 1.4rem}.hero h1{font-size:2rem}.panel{padding:1rem}.metric{min-height:96px;padding:1rem}}
</style>""", unsafe_allow_html=True)

st.markdown("""<style>
[data-testid="stHorizontalBlock"]:has([data-testid="stCheckbox"]){position:fixed;top:.65rem;right:1.25rem;z-index:1000;width:180px;background:transparent}
[data-testid="stHorizontalBlock"]:has([data-testid="stCheckbox"]) [data-testid="column"]{width:100%!important;flex:none}
[data-testid="stCheckbox"]{background:#ffffff;border:2px solid #0969da;border-radius:10px;padding:.35rem .7rem;box-shadow:0 3px 12px #1f23283d}
[data-testid="stCheckbox"] label{font-weight:700;color:#193b5a!important}
</style>""", unsafe_allow_html=True)
if st.session_state.dark_theme:
    st.markdown("""<style>
    [data-testid="stCheckbox"]{background:#17212b;border-color:#58a6ff;box-shadow:0 3px 12px #0008}
    [data-testid="stCheckbox"] label{color:#f0f6fc!important}
    </style>""", unsafe_allow_html=True)
st.toggle("🌙 Dark theme", key="dark_theme", help="Switch between light and dark themes.")

st.markdown("""<div class='hero'><div class='hero-content'><div class='hero-badge'>✦ PERSONALIZED CAREER GUIDANCE</div><div class='eyebrow'>Your skills. Your direction. Your next step.</div><h1>Career Compass</h1><p>Build a clearer path from your current skills to your next opportunity.</p></div></div>""", unsafe_allow_html=True)

if "bundle" not in st.session_state: st.session_state.bundle = model.load_or_train()
if "step" not in st.session_state: st.session_state.step = 1
if "profile" not in st.session_state: st.session_state.profile = {}
if "completed_topics" not in st.session_state: st.session_state.completed_topics = []
B = st.session_state.bundle

@st.cache_data(show_spinner=False)
def run_ats(file_data: bytes, filename: str, role: str, job_description: str):
    return ats_engine.analyze_resume(file_data, filename, role, job_description)

steps = [(1,"Your details"),(2,"Communication"),(3,"Aptitude"),(4,"Career domain"),(5,"Your roadmap")]
st.session_state.step = min(max(int(st.session_state.step), 1), len(steps))
cols = st.columns(len(steps))
for i,(n,label) in enumerate(steps):
    with cols[i]:
        state = "✓" if n < st.session_state.step else str(n)
        status = "done" if n < st.session_state.step else "active" if n == st.session_state.step else ""
        st.markdown(f"<div class='step-item {status}'><span class='step-number'>{state}</span>{label}</div>", unsafe_allow_html=True)

profile = st.session_state.profile

def option_index(options, value, default=0):
    """Return a valid select-widget index for persisted session state."""
    try:
        return options.index(value)
    except (ValueError, TypeError):
        return default

def go_to_step(step):
    st.session_state.step = min(max(step, 1), len(steps))

def next_step(): go_to_step(st.session_state.step + 1)

def back_step(): go_to_step(st.session_state.step - 1)

def build_career_report_pdf(name, role, label, score, rows, plan, domain, roadmap, strengths, focus_areas):
    """Build a professional PDF report for download."""
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=16 * mm,
        title=f"Career Compass Career Report - {name}",
        author="Career Compass",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#193b5a"), spaceAfter=6))
    styles.add(ParagraphStyle(name="ReportSubtitle", parent=styles["Normal"], alignment=TA_CENTER, textColor=colors.HexColor("#5f6b7a"), spaceAfter=16))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], textColor=colors.HexColor("#145d78"), spaceBefore=12, spaceAfter=6))
    styles.add(ParagraphStyle(name="Small", parent=styles["Normal"], fontSize=8.5, leading=11, textColor=colors.HexColor("#4b5563")))
    story = [
        Paragraph("Career Compass", styles["ReportTitle"]),
        Paragraph("Professional Career Readiness Report", styles["ReportSubtitle"]),
        Paragraph(f"<b>Student:</b> {escape(name)}<br/><b>Target role:</b> {escape(role)}<br/><b>Recommended domain:</b> {escape(domain)}<br/><b>Generated:</b> Career guidance summary", styles["Normal"]),
        Spacer(1, 8),
    ]
    summary = Table([
        ["Role-fit benchmark", "Readiness category", "Estimated learning time"],
        [f"{score:.0f}/100", label, f"{roadmap['estimated_months']} months"],
    ], colWidths=[55 * mm, 55 * mm, 55 * mm])
    summary.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#193b5a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#eef6fb")),
        ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor("#193b5a")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#c9d8e5")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [summary, Paragraph("Assessment overview", styles["Section"])]
    gap_table = [["Skill", "Score", "Benchmark", "Status"]]
    gap_table += [[r["skill"], f"{r['score']:.1f}", f"{r['benchmark']:.1f}", r["severity"]] for r in rows]
    gaps_table = Table(gap_table, colWidths=[72 * mm, 25 * mm, 30 * mm, 35 * mm], repeatRows=1)
    gaps_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6f4f1")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#145d78")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#d5dee7")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(gaps_table)
    story.append(Paragraph("Strengths and focus areas", styles["Section"]))
    story.append(Paragraph("<b>Strengths</b><br/>" + "<br/>".join(f"• {escape(item)}" for item in strengths), styles["Normal"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Focus areas</b><br/>" + "<br/>".join(f"• {escape(item)}" for item in (focus_areas or ["Maintain current skills and build portfolio depth."])), styles["Normal"]))
    story.append(Paragraph("14-day improvement plan", styles["Section"]))
    for days, focus, tasks, resources in plan:
        content = f"<b>{escape(days)} — {escape(focus)}</b><br/>" + "<br/>".join(f"• {escape(task)}" for task in tasks)
        if resources:
            content += f"<br/><font color='#5f6b7a'>Resources: {escape(resources)}</font>"
        story.append(KeepTogether([Paragraph(content, styles["Normal"]), Spacer(1, 6)]))
    story.append(Paragraph("Roadmap and responsible use", styles["Section"]))
    story.append(Paragraph(
        f"Recommended roadmap: {escape(roadmap['url'])}<br/>"
        "This report is decision-support guidance based on self-reported information and is not a guarantee of placement outcomes.",
        styles["Small"],
    ))
    document.build(story)
    return buffer.getvalue()

if st.session_state.step == 1:
    st.markdown("<div class='step'>Step 01 / Student profile</div><div class='title'>Let's start with the basics</div><div class='sub'>Tell us a little about your academic background and the tools you have used.</div>", unsafe_allow_html=True)
    with st.form("basic_form"):
        name = st.text_input("Full name *", value=profile.get("name", ""), placeholder="Enter your full name")
        a,b = st.columns(2)
        with a:
            cgpa = st.number_input("CGPA (0–10) *", min_value=0.0, max_value=10.0, value=float(profile.get("cgpa", 7.0)), step=.1)
            branch_options = ["Computer Science Engineering", "Artificial Intelligence and Machine Learning", "Information Science", "Electronics and Communication", "Electrical Engineering", "Mechanical Engineering", "Civil Engineering", "Other"]
            saved_branch = profile.get("branch", branch_options[0])
            branch_index = option_index(branch_options, saved_branch, option_index(branch_options, "Other"))
            branch = st.selectbox("Branch *", branch_options, index=branch_index)
            custom_domain = ""
            if branch == "Other":
                custom_domain = st.text_input(
                    "Custom technical domain *",
                    value=profile.get("custom_domain", ""),
                    placeholder="e.g., Robotics Engineering",
                    help="Only technical or engineering-related domains can continue.",
                )
                if custom_domain and not is_valid_technical_domain(custom_domain):
                    st.warning("Only technical or engineering-related domains are allowed for the next steps.")
        with b:
            skills_options = ["C", "C++", "Java", "Python", "JavaScript", "HTML & CSS", "SQL", "Other"]
            saved_skills = [skill for skill in profile.get("programming_skills", []) if skill in skills_options]
            skills = st.multiselect("Programming skills *", skills_options, default=saved_skills, help="Select every language or technology you have worked with.")
            programming_levels = ["Beginner", "Basic", "Intermediate", "Advanced"]
            programming_level = st.selectbox("Overall programming level", programming_levels, index=option_index(programming_levels, profile.get("programming_level", "Beginner")))
        c,d = st.columns(2)
        with c: projects = st.number_input("Projects completed (optional)", 0, 20, int(profile.get("projects_count", 0)))
        with d: internships = st.number_input("Internships completed (optional)", 0, 10, int(profile.get("internships_count", 0)))
        submitted = st.form_submit_button("Submit & continue to Communication →", use_container_width=True, type="primary")
    if submitted:
        clean_name = name.strip()
        clean_domain = custom_domain.strip()
        if not clean_name: st.error("Please enter your full name.")
        elif not is_valid_full_name(clean_name):
            st.error("Full name can contain only alphabetic characters and spaces.")
        elif branch == "Other" and not is_valid_technical_domain(clean_domain):
            st.error("Enter a valid technical or engineering-related domain to continue.")
        elif not skills: st.error("Please select at least one programming skill.")
        else:
            profile.update(name=clean_name, cgpa=cgpa, branch=clean_domain if branch == "Other" else branch, custom_domain=clean_domain, programming_skills=skills, programming_level=programming_level, projects_count=projects, internships_count=internships)
            next_step(); st.rerun()

elif st.session_state.step == 2:
    st.markdown("<div class='step'>Step 02 / Communication</div><div class='title'>Let's make your voice a strength</div><div class='sub'>There are no wrong answers here. Your responses help us add the right speaking and interview practice to your roadmap.</div>", unsafe_allow_html=True)
    with st.form("communication_form"):
        st.markdown("<div class='assessment-card'><b>🎙️ Communication check-in</b><br><span>Think about how you communicate in class, presentations, group discussions and interviews.</span></div>", unsafe_allow_html=True)
        comm_options = ["Beginner", "Basic", "Intermediate", "Advanced", "Fluent"]
        comm = st.radio("Which statement sounds most like you?", comm_options, index=option_index(comm_options, profile.get("communication_level", "Beginner")), horizontal=True, format_func=lambda x: {"Beginner":"Beginner — I am building confidence.","Basic":"Basic — I can share simple ideas.","Intermediate":"Intermediate — I manage most situations.","Advanced":"Advanced — I speak with confidence.","Fluent":"Fluent — I communicate naturally."}[x])
        levels = ["Beginner", "Intermediate", "Advanced"]
        saved_presentation = profile.get("presentation", "Beginner") if profile.get("presentation") in levels else "Beginner"
        saved_group = profile.get("group_discussion", "Beginner") if profile.get("group_discussion") in levels else "Beginner"
        saved_interview = profile.get("interview_confidence", "Beginner") if profile.get("interview_confidence") in levels else "Beginner"
        a,b,c = st.columns(3)
        with a:
            st.markdown("<div class='assessment-card'><b>🗣️ Presentations</b><br><span>Explain an idea clearly to an audience.</span></div>", unsafe_allow_html=True)
            presentation = st.select_slider("Presentation confidence", levels, value=saved_presentation)
        with b:
            st.markdown("<div class='assessment-card'><b>🤝 Group discussions</b><br><span>Listen, contribute and build on ideas.</span></div>", unsafe_allow_html=True)
            group = st.select_slider("Group discussion confidence", levels, value=saved_group)
        with c:
            st.markdown("<div class='assessment-card'><b>💼 Interviews</b><br><span>Answer questions calmly and clearly.</span></div>", unsafe_allow_html=True)
            interview = st.select_slider("Interview confidence", levels, value=saved_interview)
        st.info("Tip: Choose your current ability, not your target. Honest answers create a more useful practice plan.")
        submitted = st.form_submit_button("Submit & continue to Aptitude →", type="primary", use_container_width=True)
    if submitted:
        profile.update(communication_level=comm, presentation=presentation, group_discussion=group, interview_confidence=interview)
        next_step(); st.rerun()
    if st.button("← Back"): back_step(); st.rerun()

elif st.session_state.step == 3:
    st.markdown("<div class='step'>Step 03 / Aptitude</div><div class='title'>Turn curiosity into problem-solving power</div><div class='sub'>Aptitude is a skill you can improve with practice. Tell us where you are today and we will help you choose what to practise next.</div>", unsafe_allow_html=True)
    with st.form("aptitude_form"):
        st.markdown("<div class='assessment-card'><b>🧠 Aptitude warm-up</b><br><span>Pick the level that feels comfortable without guessing or looking up answers.</span></div>", unsafe_allow_html=True)
        apt_options = ["Beginner", "Basic", "Intermediate", "Advanced"]
        apt = st.radio("How ready do you feel for aptitude questions overall?", apt_options, index=option_index(apt_options, profile.get("aptitude_level", "Beginner")), horizontal=True, format_func=lambda x: {"Beginner":"Beginner — I am starting out.","Basic":"Basic — I solve simple questions.","Intermediate":"Intermediate — I improve with practice.","Advanced":"Advanced — I feel confident."}[x])
        levels = ["Beginner", "Intermediate", "Advanced"]
        saved_levels = {
            key: profile.get(key) if profile.get(key) in levels else "Beginner"
            for key in ("logical", "quantitative", "verbal", "problem_solving")
        }
        a,b = st.columns(2)
        with a:
            st.markdown("<div class='assessment-card'><b>🔍 Logical reasoning</b><br><span>Patterns, puzzles and structured thinking.</span></div>", unsafe_allow_html=True)
            logical = st.select_slider("Logical reasoning level", levels, value=saved_levels["logical"])
            st.markdown("<div class='assessment-card'><b>🔢 Quantitative aptitude</b><br><span>Numbers, data and time-based questions.</span></div>", unsafe_allow_html=True)
            quantitative = st.select_slider("Quantitative aptitude level", levels, value=saved_levels["quantitative"])
        with b:
            st.markdown("<div class='assessment-card'><b>📖 Verbal ability</b><br><span>Vocabulary, comprehension and communication logic.</span></div>", unsafe_allow_html=True)
            verbal = st.select_slider("Verbal ability level", levels, value=saved_levels["verbal"])
            st.markdown("<div class='assessment-card'><b>🧩 Problem solving</b><br><span>Break a challenge into smaller steps.</span></div>", unsafe_allow_html=True)
            problem = st.select_slider("Problem-solving level", levels, value=saved_levels["problem_solving"])
        st.success("You are not being graded here — this snapshot only helps us personalise your roadmap.")
        submitted = st.form_submit_button("Submit & continue to Career domain →", type="primary", use_container_width=True)
    if submitted:
        profile.update(aptitude_level=apt, logical=logical, quantitative=quantitative, verbal=verbal, problem_solving=problem)
        next_step(); st.rerun()
    if st.button("← Back"): back_step(); st.rerun()

elif st.session_state.step == 4:
    st.markdown("<div class='step'>Step 04 / Career direction</div><div class='title'>Choose up to two career directions</div><div class='sub'>Select one or two domains to compare. We will prepare a separate learning roadmap and video resources for each choice.</div>", unsafe_allow_html=True)
    domains = list(career.DOMAINS.keys()) + ["Not Sure — Recommend for me"]
    icons = ["🖥️","⚙️","🧩","✨","🤖","📊","📈","🛡️","☁️","🔧","📱","🧪","🎨","⛓️","🧭"]
    descriptions = [career.DOMAINS[d][1] for d in career.DOMAINS] + ["Get suggested career paths based on your skills and interests."]
    selected_domains = list(profile.get("selected_domains", []))
    if not selected_domains and profile.get("domain"):
        selected_domains = [profile["domain"]]
    st.info(f"{len(selected_domains)}/2 career directions selected")
    for start in range(0, len(domains), 3):
        cols = st.columns(3)
        for j,d in enumerate(domains[start:start+3]):
            idx = start+j
            with cols[j]:
                st.markdown(f"<div class='domain-card'><div style='font-size:1.45rem'>{icons[idx]}</div><b>{d}</b><div class='small-muted'>{descriptions[idx]}</div></div>", unsafe_allow_html=True)
                if st.button("Selected ✓" if d in selected_domains else "Choose this domain", key=f"domain_{idx}", use_container_width=True):
                    updated_domains = selected_domains.copy()
                    if d in selected_domains:
                        updated_domains.remove(d)
                    elif len(selected_domains) < 2:
                        updated_domains.append(d)
                    else:
                        st.warning("You can select a maximum of two career directions.")
                    profile["selected_domains"] = updated_domains
                    st.rerun()
    st.markdown("<div class='panel'><b>How much time can you study each week?</b><br><span class='small-muted'>We use this to estimate a realistic completion timeline.</span></div>", unsafe_allow_html=True)
    hours = st.slider("Learning hours per week", 4, 30, int(profile.get("weekly_hours", 8)), 1)
    profile["weekly_hours"] = hours
    if st.button("Submit & continue to Your roadmap →", type="primary", use_container_width=True):
        if not selected_domains:
            st.warning("Choose at least one career direction to continue.")
        else:
            profile["selected_domains"] = selected_domains
            profile["domain"] = selected_domains[0]
            go_to_step(5)
            st.rerun()
    if st.button("← Back", key="back_domain"): back_step(); st.rerun()

elif st.session_state.step == 5:
    selected_domains = profile.get("selected_domains", [])
    domain = profile.get("domain", "Not Sure — Recommend for me")
    recommendations = career.recommend_domain(profile)
    selected_domains = [
        recommendations[0][0] if selected == "Not Sure — Recommend for me" else selected
        for selected in selected_domains
    ]
    selected_domains = list(dict.fromkeys(selected_domains))
    if not selected_domains:
        selected_domains = [recommendations[0][0]]
    domain = st.selectbox(
        "Explore a selected roadmap",
        selected_domains,
        index=selected_domains.index(domain) if domain in selected_domains else 0,
    )
    role = "Data / ML Engineer" if domain in ("Artificial Intelligence", "Machine Learning", "Data Science", "Data Analytics") else "Software Developer"
    profile["selected_domains"] = selected_domains
    profile["recommended_domain"] = domain
    comm_score = career.LEVELS[profile.get("communication_level", "Beginner")]
    apt_score = career.LEVELS[profile.get("aptitude_level", "Beginner")]
    coding_score = career.LEVELS[profile.get("programming_level", "Beginner")]
    # Map the self-assessment to the existing model's feature schema; proxy estimates are explicitly disclosed.
    dsa = min(100, coding_score + min(20, len(profile.get("programming_skills", []))*3))
    core = 35 if profile.get("programming_level") in ("Beginner", "Basic") else 55 if profile.get("programming_level")=="Intermediate" else 70
    comm_sub = sum(career.LEVELS.get(profile.get(k,"Beginner"),25) for k in ("presentation","group_discussion","interview_confidence"))/3
    communication = round((comm_score + comm_sub)/2)
    aptitude = round((apt_score + sum(career.LEVELS.get(profile.get(k,"Beginner"),25) for k in ("logical","quantitative","verbal","problem_solving"))/4)/2)
    model_profile = {"cgpa":profile["cgpa"],"dsa":dsa,"core_cs":core,"aptitude":aptitude,"communication":communication,"projects":min(6,profile.get("projects_count",0)),"internships":min(3,profile.get("internships_count",0))}
    model_df = data.validate(pd.DataFrame([model_profile]))
    labels, probs = model.predict(B, model_df); label = labels.iloc[0]
    score, rows = gaps.analyze(model_profile, role)
    roadmap = career.build_roadmap(domain, profile, profile.get("weekly_hours",8))
    strengths = []
    if profile["cgpa"] >= 7.5: strengths.append("Academic performance is a positive foundation.")
    if len(profile.get("programming_skills",[])) >= 3: strengths.append("You have exposure to multiple programming languages/tools.")
    if coding_score >= 60: strengths.append("Your self-rated programming foundation is at least intermediate.")
    if communication >= 60: strengths.append("Your communication assessment indicates a useful starting strength.")
    if not strengths: strengths.append("You have completed a useful baseline assessment and can now follow a focused improvement plan.")
    weak = [r["skill"] for r in rows if r["severity"] != "Met"][:4]
    st.markdown(f"<div class='step'>Step 05 / Your career report</div><div class='title'>Your roadmap is ready, {profile['name'].split()[0]}.</div><div class='sub'>A practical starting point based on your self-assessment — review and adjust it as your skills grow.</div>", unsafe_allow_html=True)
    m1,m2,m3,m4 = st.columns(4)
    for col,val,key in [(m1, f"{score:.0f}/100", "Role-fit benchmark"),(m2,label,"ML readiness category"),(m3,f"{roadmap['estimated_months']} months","Estimated learning time"),(m4,domain,"Recommended domain")]:
        with col: st.markdown(f"<div class='metric'><div class='v' style='font-size:{'1.05rem' if len(str(val))>17 else '1.5rem'}'>{val}</div><div class='k'>{key}</div></div>", unsafe_allow_html=True)
    st.info("The readiness category is a Random Forest model trained on synthetic demonstration data. The role-fit score uses transparent benchmark weights. Neither is a validated hiring prediction.")
    left,right = st.columns([1,1])
    with left:
        st.markdown("### Student profile")
        st.write(f"**Branch:** {profile['branch']}  \n**CGPA:** {profile['cgpa']:.1f}/10  \n**Programming skills:** {', '.join(profile['programming_skills'])}  \n**Communication:** {profile['communication_level']}  \n**Aptitude:** {profile['aptitude_level']}")
        st.markdown("### Your strengths")
        for x in strengths: st.markdown(f"- {x}")
        st.markdown("### Focus areas")
        for x in weak or ["Maintain your current skill levels and build portfolio depth."]: st.markdown(f"- {x}")
    with right:
        st.markdown("### Skill-gap overview")
        chart_df = pd.DataFrame(rows)
        chart = alt.Chart(chart_df).mark_bar(cornerRadiusEnd=5).encode(y=alt.Y("skill:N", sort="-x", title=None), x=alt.X("score:Q", scale=alt.Scale(domain=[0,100]), title="Estimated skill score"), color=alt.Color("severity:N", scale=alt.Scale(domain=["Critical", "Moderate", "Met"], range=["#d66b5d", "#e5ae52", "#3c9b91"]), legend=None), tooltip=["skill","score","benchmark","severity"])
        st.altair_chart(chart.properties(height=270), use_container_width=True)
    st.markdown("---")
    st.markdown(f"## Personalized {domain} roadmap")
    st.write(roadmap["description"])
    st.markdown(f"**Primary roadmap reference:** [{domain} roadmap on roadmap.sh]({roadmap['url']})")
    st.caption(f"Planning assumption: {roadmap['weekly_hours']} study hours/week. Actual duration depends on consistency and prior experience.")
    hub = career.learning_hub_for(domain)
    st.markdown("## Free career learning hub")
    st.write(f"**Goal:** {hub['goal']}")
    st.caption("Follow these free resources in order from beginner foundations to job-ready projects.")
    hub_cols = st.columns(2)
    for index, (name, url) in enumerate(hub["resources"], start=1):
        with hub_cols[(index - 1) % 2]:
            st.markdown(
                f"<a class='external-resource' href='{escape(url, quote=True)}' target='_blank' rel='noopener noreferrer'>"
                f"<span>{index:02d}. {escape(name)}</span><span class='arrow'>→</span></a>",
                unsafe_allow_html=True,
            )
    st.markdown(f"**Learning order:** {escape(hub['order'])}")
    if hub.get("note"):
        st.info(hub["note"])
    st.markdown("### Your interactive study plan")
    st.caption("Choose one focus, use the linked course, then mark the phase complete when you can demonstrate the project milestone.")
    focus_options = [f"{phase}: {project}" for phase, _, _, _, project in roadmap["phases"]]
    focus = st.selectbox("What is your focus this week?", focus_options, key=f"focus_{domain}")
    for phase,topics,tools,duration,project in roadmap["phases"]:
        topic_key = f"{phase}:{domain}"
        done = topic_key in st.session_state.completed_topics
        with st.expander(f"{'✅' if done else '⬜'} {phase} level · {duration}", expanded=not done):
            st.markdown(f"**Learn:** {topics}  \n**Tools:** {tools}  \n**Build:** {project}")
            st.markdown("**Where to learn**")
            resource_cols = st.columns(min(4, len(career.resources_for_phase(topics, tools, roadmap["url"]))))
            for col, (name, url) in zip(resource_cols, career.resources_for_phase(topics, tools, roadmap["url"])):
                with col:
                    st.markdown(f"<a class='external-resource' href='{escape(url, quote=True)}' target='_blank' rel='noopener noreferrer'><span>↗ {escape(name)}</span><span class='arrow'>→</span></a>", unsafe_allow_html=True)
            youtube_name, youtube_url = career.youtube_for_phase(domain, phase, topics, tools)
            st.markdown("**Optional video support**")
            st.markdown(f"<a class='external-resource' href='{escape(youtube_url, quote=True)}' target='_blank' rel='noopener noreferrer'><span>▶ {escape(youtube_name)}</span><span class='arrow'>→</span></a>", unsafe_allow_html=True)
            st.progress(1.0 if done else 0.0, text="Phase complete" if done else "Not started")
            topic_key = f"{phase}:{domain}"
            if st.checkbox("Mark this phase completed", value=done, key=f"done_{phase}_{domain}"):
                if topic_key not in st.session_state.completed_topics: st.session_state.completed_topics.append(topic_key)
            elif topic_key in st.session_state.completed_topics: st.session_state.completed_topics.remove(topic_key)
    total = len(roadmap["phases"]); completed = sum(1 for p in roadmap["phases"] if f"{p[0]}:{domain}" in st.session_state.completed_topics)
    st.markdown("### Learning progress")
    st.progress(completed/total if total else 0)
    st.caption(f"{completed} of {total} roadmap phases completed")
    st.markdown("### Suggested weekly routine")
    learn_hours = max(2, round(roadmap["weekly_hours"] * .5))
    practice_hours = max(1, round(roadmap["weekly_hours"] * .3))
    build_hours = max(1, round(roadmap["weekly_hours"] * .2))
    routine = pd.DataFrame({"Activity": ["Learn", "Practice", "Build & review"], "Hours": [learn_hours, practice_hours, build_hours]})
    st.altair_chart(alt.Chart(routine).mark_bar(cornerRadiusEnd=6).encode(
        x=alt.X("Hours:Q", title="Hours"), y=alt.Y("Activity:N", sort=None, title=None),
        color=alt.Color("Activity:N", scale=alt.Scale(range=["#3c9b91", "#e5ae52", "#d66b5d"]), legend=None),
        tooltip=["Activity", "Hours"]), use_container_width=True)
    st.caption(f"Weekly target: {roadmap['weekly_hours']} hours · Current focus: {focus.split(':', 1)[0]}")
    report_pdf = build_career_report_pdf(
        profile["name"], role, label, score, rows, gaps.sprint(rows),
        domain, roadmap, strengths, weak,
    )
    st.download_button(
        "⬇ Download my career report (PDF)",
        report_pdf,
        file_name=f"{profile['name'].replace(' ', '_')}_career_report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
    if st.button("← Previous step", key="back_roadmap", use_container_width=True):
        back_step()
        st.rerun()
    if st.button("↻ Retake assessment", use_container_width=True):
        st.session_state.step=1; st.session_state.profile={}; st.session_state.completed_topics=[]; st.rerun()
    st.caption("Your assessment is guidance for learning and placement preparation, not a guarantee of employment. The app currently stores progress in the active Streamlit session.")

# Resume screening tool.
st.markdown("---")
with st.expander("Resume ATS check", expanded=False):
    st.write("Upload one or more PDF resumes for transparent ATS-style screening and actionable fixes.")
    settings_left, settings_right = st.columns(2)
    with settings_left:
        ats_role = st.selectbox("Target role", [ats_engine.GENERAL, *ats_engine.ROLE_KEYWORDS.keys()], key="ats_role")
        shortlist_cutoff = st.slider("Shortlist cut-off (ATS score)", 40, 95, 70, key="ats_cutoff")
    with settings_right:
        minimum_keyword_match = st.slider("Minimum keyword match (%)", 0, 90, 50, key="ats_min_keywords")
        job_description = st.text_area(
            "Optional job description",
            placeholder="Paste a job description for more realistic keyword matching.",
            height=100,
            key="ats_job_description",
        )
    st.caption("Files are processed in memory only; nothing is stored.")
    resume_files = st.file_uploader(
        "Upload resume PDF(s)", type="pdf", accept_multiple_files=True, key="resume_pdfs"
    )
    if resume_files:
        results = [
            run_ats(file.getvalue(), file.name, ats_role, job_description)
            for file in resume_files
        ]

        def ats_decision(result):
            if result.error or not result.is_resume or result.knockouts:
                return "Rejected", "; ".join(result.knockouts) or result.error or "Not a resume"
            if result.score < shortlist_cutoff:
                return "Improve", f"Score below cut-off {shortlist_cutoff}"
            if result.keyword_match is not None and result.keyword_match < minimum_keyword_match:
                return "Improve", f"Keyword match below {minimum_keyword_match}%"
            return "Shortlist", "Meets all criteria"

        overview_rows = []
        for result in results:
            decision, reason = ats_decision(result)
            overview_rows.append({
                "Candidate file": result.filename,
                "Resume?": "Yes" if result.is_resume else "No",
                "ATS score": result.score if result.is_resume else None,
                "Keyword match %": result.keyword_match if result.is_resume else None,
                "Pages": result.pages,
                "Decision": decision,
                "Reason": reason,
                "Verdict": result.verdict,
            })
        overview = pd.DataFrame(overview_rows).sort_values(
            "ATS score", ascending=False, na_position="last"
        ).reset_index(drop=True)
        st.subheader("Screening results")
        st.dataframe(
            overview,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ATS score": st.column_config.ProgressColumn(
                    "ATS score", min_value=0, max_value=100, format="%.1f"
                ),
                "Keyword match %": st.column_config.NumberColumn(format="%.1f"),
            },
        )
        st.download_button(
            "Download results (CSV)",
            overview.to_csv(index=False).encode("utf-8"),
            "ats_screening_results.csv",
            "text/csv",
            key="download_ats_results",
        )
        st.subheader("Detailed reports")
        for result in results:
            decision, reason = ats_decision(result)
            score_label = f"{result.score:.1f}/100" if result.is_resume else "No score"
            with st.expander(f"{result.filename} · {score_label} · {decision}", expanded=len(results) == 1):
                if result.error or not result.is_resume:
                    st.warning("Caution: the selected PDF does not appear to be a resume or CV, so an ATS score was not generated.")
                    if result.error:
                        st.error(result.error)
                    if not result.checks.empty:
                        st.dataframe(result.checks, use_container_width=True, hide_index=True)
                    if not result.fixes.empty:
                        st.subheader("What to change")
                        st.dataframe(result.fixes, use_container_width=True, hide_index=True)
                    continue
                metric_values = [
                    ("ATS score", f"{result.score:.1f}/100"),
                    ("Keyword match", "n/a" if result.keyword_match is None else f"{result.keyword_match:.1f}%"),
                    ("Pages / words", f"{result.pages} / {result.words}"),
                    ("Resume confidence", f"{result.confidence:.0%}"),
                ]
                metric_cards = "".join(
                    f"<div style='background:#17212b;border:1px solid #3b4654;border-radius:8px;padding:12px;min-height:78px'>"
                    f"<div style='color:#c9d1d9;font-size:.78rem;font-weight:600'>{escape(label)}</div>"
                    f"<div style='color:#79c0ff;font-size:1.35rem;font-weight:700;margin-top:6px'>{escape(value)}</div></div>"
                    for label, value in metric_values
                )
                st.markdown(
                    f"<div style='display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:.5rem 0 1rem'>{metric_cards}</div>",
                    unsafe_allow_html=True,
                )
                st.write(f"**Verdict:** {result.verdict}  |  **Decision:** {decision} ({reason})")
                if result.knockouts:
                    st.error("Knock-out issues: " + "; ".join(result.knockouts))
                if result.sections:
                    st.caption("Sections detected: " + ", ".join(result.sections))
                t1, t2, t3, t4, t5, t6 = st.tabs(
                    ["Fixes (priority)", "All checks", "Keywords", "Replacements", "Bullet review", "Extracted text"]
                )
                with t1:
                    st.dataframe(result.fixes, use_container_width=True, hide_index=True)
                with t2:
                    st.dataframe(result.checks, use_container_width=True, hide_index=True)
                    with st.popover("Why was this treated as a resume?"):
                        st.dataframe(
                            pd.DataFrame({
                                "Signal": list(result.signals),
                                "Found": ["Yes" if value else "No" for value in result.signals.values()],
                            }),
                            use_container_width=True,
                            hide_index=True,
                        )
                with t3:
                    if result.keywords.empty:
                        st.info("Select a target role or paste a job description to enable keyword matching.")
                    else:
                        st.caption(f"Keywords from: {result.keyword_source}")
                        st.dataframe(result.keywords, use_container_width=True, hide_index=True)
                with t4:
                    st.dataframe(result.replacements, use_container_width=True, hide_index=True)
                with t5:
                    st.dataframe(result.bullets, use_container_width=True, hide_index=True)
                with t6:
                    st.caption("This is roughly what an ATS sees. If it looks jumbled, the resume layout may be the problem.")
                    st.text_area("Extracted text", result.text, height=350, key=f"ats_text_{result.filename}")
