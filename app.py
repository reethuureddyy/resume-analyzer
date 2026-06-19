import streamlit as st
import tempfile
import os
from analyzer import (
    extract_text_from_pdf,
    get_match_score,
    get_missing_keywords,
    get_ats_tips,
    get_skill_gaps
)

st.set_page_config(
    page_title="ResumeAI - Smart Resume Analyzer",
    page_icon=":page_facing_up:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CUSTOM CSS - SOFT PASTEL THEME ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"], .stMarkdown, .stTextInput, .stTextArea, p, span, div {
        font-family: 'Inter', sans-serif !important;
    }

    .stApp {
        background-color: #EEF0FA;
    }

    .main-title {
        font-size: 26px;
        font-weight: 600;
        color: #2C2C2A;
        margin-bottom: 2px;
    }
    .sub-title {
        font-size: 14px;
        color: #888780;
        margin-bottom: 20px;
    }
    .section-label {
        font-size: 12px;
        font-weight: 600;
        color: #888780;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 8px;
    }

    .soft-card {
        background: #FFFFFF;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(30,30,60,0.06);
        margin-bottom: 16px;
    }

    .score-circle-box {
        text-align: center;
        padding: 10px 0;
    }
    .score-num {
        font-size: 40px;
        font-weight: 600;
        color: #3C3489;
    }
    .score-tag {
        font-size: 13px;
        color: #888780;
        margin-top: 2px;
    }

    .metric-soft {
        background: #F8F8FD;
        border-radius: 14px;
        padding: 14px;
        text-align: center;
    }
    .metric-val {
        font-size: 22px;
        font-weight: 600;
        color: #3C3489;
    }
    .metric-lbl {
        font-size: 11px;
        color: #888780;
        margin-top: 2px;
    }

    .pill-found {
        background: #EAF3DE;
        color: #27500A;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 12px;
        margin: 3px;
        display: inline-block;
        font-weight: 500;
    }
    .pill-missing {
        background: #FAECE7;
        color: #712B13;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 12px;
        margin: 3px;
        display: inline-block;
        font-weight: 500;
    }

    .tip-soft {
        background: #F8F8FD;
        border-radius: 12px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 13px;
        color: #5F5E5A;
        border-left: 3px solid #7F77DD;
    }
    .tip-soft.warn { border-left-color: #EF9F27; }
    .tip-soft.good { border-left-color: #5DCAA5; }

    .gap-soft {
        background: #F8F8FD;
        border-radius: 12px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 13px;
        color: #5F5E5A;
    }
    .gap-soft strong { color: #534AB7; }

    div.stButton > button {
        background-color: #534AB7;
        color: white;
        border-radius: 30px;
        border: none;
        font-weight: 500;
        padding: 10px 0;
    }
    div.stButton > button:hover {
        background-color: #3C3489;
        color: white;
    }
    div.stButton > button p {
        color: white !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #F1EFE8;
    }
    section[data-testid="stSidebar"] * {
        color: #2C2C2A !important;
    }
    [data-testid="stCaptionContainer"] {
        color: #888780 !important;
    }

    [data-testid="stFileUploader"] {
        background-color: #F8F8FD;
        border-radius: 14px;
        padding: 10px;
    }
    [data-testid="stFileUploaderDropzone"] {
        background-color: #F8F8FD !important;
    }
    [data-testid="stFileUploaderDropzone"] * {
        color: #5F5E5A !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
        background-color: #534AB7 !important;
        color: white !important;
        border-radius: 20px !important;
    }

    .stTextArea textarea {
        background-color: #F8F8FD !important;
        color: #2C2C2A !important;
        border: 1px solid #E5E5F0 !important;
        border-radius: 12px !important;
    }

    .stRadio label, .stRadio span {
        color: #2C2C2A !important;
    }

    .stAlert {
        background-color: #F8F8FD !important;
        border-radius: 14px !important;
    }
    .stAlert p {
        color: #5F5E5A !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### ResumeAI")
    st.caption("AI-powered resume analyzer")
    st.divider()

    page = st.radio(
        "Navigation",
        ["Analyzer", "History", "AI Tools"],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("Built by Akepati Reethu")
    st.caption("CS Engineering | SRM IST")

# ---------- MAIN HEADER ----------
st.markdown('<p class="main-title">AI Resume Analyzer</p>',
            unsafe_allow_html=True)
st.markdown('<p class="sub-title">Upload your resume and a job description to get instant ATS feedback</p>',
            unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.3], gap="large")

# ---------- LEFT PANEL ----------
with col1:
    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-label">Upload Resume</p>',
                unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=[
                                     "pdf"], label_visibility="collapsed")

    st.markdown('<p class="section-label" style="margin-top:16px;">Job Description</p>',
                unsafe_allow_html=True)
    job_description = st.text_area("Paste job description", height=200,
                                   label_visibility="collapsed", placeholder="Paste the full job description here...")

    analyze_btn = st.button(
        "Analyze Resume", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- RIGHT PANEL ----------
with col2:
    if analyze_btn:
        if not uploaded_file:
            st.error("Please upload your resume PDF first.")
        elif not job_description.strip():
            st.error("Please paste a job description.")
        else:
            with st.spinner("Analyzing your resume..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                resume_text = extract_text_from_pdf(tmp_path)
                os.unlink(tmp_path)

                score = get_match_score(resume_text, job_description)
                found_keywords, missing_keywords = get_missing_keywords(
                    resume_text, job_description)
                ats_tips = get_ats_tips(resume_text, score)
                skill_gaps = get_skill_gaps(resume_text, job_description)

            score_label = "Strong Match" if score >= 75 else "Moderate Match" if score >= 50 else "Low Match"

            st.markdown('<div class="soft-card">', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="score-circle-box">
                <div class="score-num">{score}%</div>
                <div class="score-tag">{score_label}</div>
            </div>
            """, unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(
                    f'<div class="metric-soft"><div class="metric-val">{len(found_keywords)}</div><div class="metric-lbl">Found</div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(
                    f'<div class="metric-soft"><div class="metric-val">{len(missing_keywords)}</div><div class="metric-lbl">Missing</div></div>', unsafe_allow_html=True)
            with m3:
                grade = "A+" if score >= 80 else "B+" if score >= 60 else "C"
                st.markdown(
                    f'<div class="metric-soft"><div class="metric-val">{grade}</div><div class="metric-lbl">Grade</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="soft-card">', unsafe_allow_html=True)
            if found_keywords:
                st.markdown(
                    '<p class="section-label">Keywords Found</p>', unsafe_allow_html=True)
                found_html = " ".join(
                    [f"<span class='pill-found'>{k}</span>" for k in found_keywords])
                st.markdown(found_html, unsafe_allow_html=True)

            if missing_keywords:
                st.markdown(
                    '<p class="section-label" style="margin-top:14px;">Keywords Missing</p>', unsafe_allow_html=True)
                missing_html = " ".join(
                    [f"<span class='pill-missing'>{k}</span>" for k in missing_keywords])
                st.markdown(missing_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="soft-card">', unsafe_allow_html=True)
            st.markdown(
                '<p class="section-label">ATS Tips and Suggestions</p>', unsafe_allow_html=True)
            for tip_type, tip_text in ats_tips:
                css_class = "warn" if tip_type == "warn" else "good" if tip_type == "good" else ""
                st.markdown(
                    f"<div class='tip-soft {css_class}'>{tip_text}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if skill_gaps:
                st.markdown('<div class="soft-card">', unsafe_allow_html=True)
                st.markdown(
                    '<p class="section-label">Skill Gaps to Close</p>', unsafe_allow_html=True)
                for gap in skill_gaps:
                    st.markdown(
                        f"<div class='gap-soft'><strong>{gap['skill'].title()}</strong> — {gap['suggestion']}</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.info(
            "Upload your resume and paste a job description, then click Analyze Resume.")
        st.markdown('</div>', unsafe_allow_html=True)
