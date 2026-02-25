# SkillGap-AI
SkillGap AI is an AI-powered resume and job description matching system designed to evaluate how well a candidate’s resume aligns with a specific job role.


## 🚀 Overview
SkillGap-AI is a full-stack application that uses Natural Language Processing (NLP) to parse PDF resumes and compare them against job descriptions. It provides a match score, a targeted study list, and highlights extra qualifications.

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Framework:** Flask (Web UI)
* **Libraries:** PyPDF2 (Extraction), Scikit-learn (NLP logic)
* **Database:** MySQL (Persistence)

## 📁 Architecture
- `app.py`: Main Flask server and routing logic.
- `core/modules/`: Modular backend engines for extraction and matching.
- `templates/`: Jinja2 HTML frontend layers.
- `tests/`: Specialized scripts for pipeline validation.