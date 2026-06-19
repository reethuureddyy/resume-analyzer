import pdfplumber
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)


def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    return text.strip()


def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def get_match_score(resume_text, jd_text):
    cleaned_resume = clean_text(resume_text)
    cleaned_jd = clean_text(jd_text)
    documents = [cleaned_resume, cleaned_jd]
    vectorizer = CountVectorizer().fit_transform(documents)
    vectors = vectorizer.toarray()
    score = cosine_similarity([vectors[0]], [vectors[1]])[0][0]
    return round(score * 100, 2)


def extract_keywords(text):
    common_skills = [
        "python", "java", "sql", "machine learning", "deep learning",
        "pandas", "numpy", "scikit-learn", "tensorflow", "keras",
        "flask", "django", "fastapi", "docker", "kubernetes",
        "git", "github", "linux", "aws", "azure", "gcp",
        "nlp", "computer vision", "data analysis", "tableau",
        "power bi", "excel", "rest api", "html", "css", "javascript",
        "react", "node", "mongodb", "mysql", "postgresql",
        "c", "c++", "r", "scala", "spark", "hadoop",
        "communication", "teamwork", "problem solving", "leadership"
    ]
    text_lower = text.lower()
    found = [skill for skill in common_skills if skill in text_lower]
    return found


def get_missing_keywords(resume_text, jd_text):
    resume_keywords = set(extract_keywords(resume_text))
    jd_keywords = set(extract_keywords(jd_text))
    missing = jd_keywords - resume_keywords
    found = jd_keywords & resume_keywords
    return list(found), list(missing)


def get_ats_tips(resume_text, score):
    tips = []
    resume_lower = resume_text.lower()

    if score < 50:
        tips.append(
            ("warn", "Low match score — tailor your resume to match the job description keywords"))
    elif score < 75:
        tips.append(
            ("warn", "Moderate match — add more relevant skills and keywords from the job description"))
    else:
        tips.append(
            ("good", "Strong match! Your resume aligns well with this job"))

    if len(resume_text.split()) < 300:
        tips.append(
            ("warn", "Resume seems short — add more detail to your projects and experience"))

    if "github" not in resume_lower:
        tips.append(
            ("warn", "Add your GitHub profile link — recruiters always check it"))

    if not any(char.isdigit() for char in resume_text):
        tips.append(
            ("warn", "Add numbers and metrics to your projects — e.g. 'improved accuracy by 30%'"))
    else:
        tips.append(
            ("good", "Good — your resume contains measurable achievements"))

    if "intern" not in resume_lower:
        tips.append(
            ("info", "No internship detected — self-initiated projects become even more important"))

    tips.append(
        ("info", "Use standard section headings: Skills, Projects, Education, Experience"))

    return tips


def get_skill_gaps(resume_text, jd_text):
    _, missing = get_missing_keywords(resume_text, jd_text)
    gaps = []
    for skill in missing:
        gaps.append({
            "skill": skill,
            "suggestion": f"Learn {skill} — add to your skills section after practicing"
        })
    return gaps
