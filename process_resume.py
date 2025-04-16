import fitz  # PyMuPDF
import spacy
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Predefined skills
SKILL_SET = {
    "python", "java", "machine learning", "sql", "flask", "react", "html", "css", "docker", "aws",
    "kubernetes", "nlp", "deep learning", "data analysis", "javascript", "c++", "c#", "ruby", "php",
    "swift", "typescript", "go", "scala", "rust", "matlab", "r", "sas", "hadoop", "spark", "tableau",
    "powerbi", "excel", "git", "github", "jenkins", "ansible", "terraform", "linux", "unix", "windows",
    "networking", "cybersecurity", "penetration testing", "ethical hacking", "cloud computing", "devops"
}

def extract_text_from_pdf(pdf_path):
    """Extracts and returns lowercase text from a PDF file."""
    try:
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        return text.lower()
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

def extract_skills(text):
    """Extracts predefined skills from resume text using spaCy."""
    doc = nlp(text)
    return {token.text.lower() for token in doc if token.text.lower() in SKILL_SET}

def rank_resumes_from_folder(resume_folder, job_desc_path):
    """
    Ranks resumes in the folder based on skill match and similarity to job description.
    Returns a list of tuples: (filename, score, [skills])
    """
    if not os.path.exists(job_desc_path):
        raise FileNotFoundError(f"Job description file not found: {job_desc_path}")

    with open(job_desc_path, "r", encoding="utf-8") as f:
        job_description = f.read().lower()

    resume_scores = []

    for file in os.listdir(resume_folder):
        if file.endswith(".pdf"):
            full_path = os.path.join(resume_folder, file)
            resume_text = extract_text_from_pdf(full_path)
            if not resume_text:
                continue

            resume_skills = extract_skills(resume_text)

            # Compute similarity
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([job_description, resume_text])
            similarity_score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

            score = len(resume_skills) + (similarity_score * 10)
            resume_scores.append((file, round(score, 2), list(resume_skills)))

    resume_scores.sort(key=lambda x: x[1], reverse=True)
    return resume_scores
