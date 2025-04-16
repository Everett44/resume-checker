
import os
import re
import streamlit as st
import pdfplumber
from openai import OpenAI

# Set up the OpenAI client (new v1+ API style)


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ← Put your API key here

# Function to extract resume text from a PDF
def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

# Function to analyze resume against job description
def analyze_resume(resume_text, job_description):
    prompt = f"""
You are an expert recruiter. Evaluate how well the following resume matches the given job description.

Job Description:
{job_description}

Resume:
{resume_text}

Provide:
- A match score from 0 to 100
- Skills or keywords that match
- Skills or keywords that are missing
- A final recommendation: Interview, Maybe, or Reject
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    content = response.choices[0].message.content

    # Extract match score from the response
    match = re.search(r'(\d{1,3})', content)
    score = int(match.group(1)) if match else None

    return score, content


# Streamlit UI
st.title("🧠 Resume Screening AI for Businesses")
st.write("Paste a job description, upload a resume PDF, and get an AI-powered match analysis.")

job_desc = st.text_area("📋 Job Description")

uploaded_resumes = st.file_uploader(
    "📎 Upload One or More Resumes (PDF only)",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_resumes and job_desc:
    for uploaded_resume in uploaded_resumes:
        with st.spinner(f"Analyzing {uploaded_resume.name}..."):
            try:
                resume_text = extract_text_from_pdf(uploaded_resume)
                score, result = analyze_resume(resume_text, job_desc)

                st.markdown(f"## 📄 {uploaded_resume.name}")

                st.markdown("### 🎯 Match Score")
                if score is not None:
                    st.progress(score / 100)
                    st.write(f"**{score}/100** match")
                else:
                    st.warning("Could not extract a match score from the AI response.")

                st.markdown("### 🧠 AI Feedback")
                for line in result.split("\n"):
                    st.write(line)

            except Exception as e:
                st.error(f"❌ Error processing {uploaded_resume.name}")
                st.code(str(e))



