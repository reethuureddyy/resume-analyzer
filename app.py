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
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
<style>
    .main { padding: 2rem; }
    .score-big { font-size: 3rem; font-weight: 500; }
    .tag-found { background: rgba(16,185,129,0.15); color: #10b981; padding: 4px 12px; border-radius: 20px; font-size: 13px; margin: 3px; display: inline-block; }
    .tag-missing { background: rgba(239,68,68,0.15); color: #ef4444; padding: 4px 12px; border-radius: 20px; font-size: 13px; margin: 3px; display: inline-block; }
    .tip-warn { background: rgba(245,158,11,0.1); border-left: 3px solid #f59e0b; padding: 10px 14px; border-radius: 6px; margin: 6px 0; font-size: 14px; }
    .tip-good { background: rgba(16,185,129,0.1); border-left: 3px solid #10b981; padding: 10px 14px; border-radius: 6px; margin: 6px 0; font-size: 14px; }
    .tip-info { background: rgba(99,102,241,0.1); border-left: 3px solid #6366f1; padding: 10px 14px; border-radius: 6px; margin: 6px 0; font-size: 14px; }
    .gap-card { background: rgba(99,102,241,0.07); border: 0.5px solid rgba(99,102,241,0.3); border-radius: 10px; padding: 12px 16px; margin: 6px 0; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

st.title("📄 AI Resume Analyzer")
st.markdown("Upload your resume and paste a job description to get your ATS score, keyword analysis, and suggestions.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📁 Upload Resume")
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF only)", type=["pdf"])

    st.subheader("📋 Job Description")
    job_description = st.text_area("Paste the job description here",
                                   height=220, placeholder="Copy and paste the full job description...")

    analyze_btn = st.button(
        "🔍 Analyze Resume", use_container_width=True, type="primary")

with col2:
    if analyze_btn:
        if not uploaded_file:
            st.error("Please upload your resume PDF first!")
        elif not job_description.strip():
            st.error("Please paste a job description!")
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

            if score >= 75:
                score_color = "green"
                score_label = "Strong Match! ✅"
            elif score >= 50:
                score_color = "orange"
                score_label = "Moderate Match ⚠️"
            else:
                score_color = "red"
                score_label = "Low Match ❌"

            st.subheader("📊 Match Score")
            st.markdown(
                f"<p class='score-big' style='color:{score_color}'>{score}%</p>", unsafe_allow_html=True)
            st.markdown(f"**{score_label}**")
            st.progress(int(score))

            st.divider()

            st.subheader("🔑 Keyword Analysis")
            mcol1, mcol2 = st.columns(2)
            with mcol1:
                st.metric("Found", len(found_keywords))
            with mcol2:
                st.metric("Missing", len(missing_keywords))

            if found_keywords:
                st.markdown("**Found in your resume:**")
                found_html = " ".join(
                    [f"<span class='tag-found'>{k}</span>" for k in found_keywords])
                st.markdown(found_html, unsafe_allow_html=True)

            if missing_keywords:
                st.markdown("**Missing from your resume:**")
                missing_html = " ".join(
                    [f"<span class='tag-missing'>{k}</span>" for k in missing_keywords])
                st.markdown(missing_html, unsafe_allow_html=True)

            st.divider()

            st.subheader("💡 ATS Tips & Suggestions")
            for tip_type, tip_text in ats_tips:
                if tip_type == "warn":
                    st.markdown(
                        f"<div class='tip-warn'>⚠️ {tip_text}</div>", unsafe_allow_html=True)
                elif tip_type == "good":
                    st.markdown(
                        f"<div class='tip-good'>✅ {tip_text}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(
                        f"<div class='tip-info'>💡 {tip_text}</div>", unsafe_allow_html=True)

            if skill_gaps:
                st.divider()
                st.subheader("📈 Skill Gaps to Close")
                for gap in skill_gaps:
                    st.markdown(
                        f"<div class='gap-card'>🎯 <strong>{gap['skill'].title()}</strong> — {gap['suggestion']}</div>", unsafe_allow_html=True)
    else:
        st.info("👈 Upload your resume and paste a job description, then click Analyze!")
