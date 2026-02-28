from flask import Flask, render_template, request
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from core.modules.extractor import extract_text_from_pdf
from core.modules.matcher import clean_for_nlp, calculate_match_score

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return "No file part in the request", 400

    pdf_file = request.files["resume"]
    if pdf_file.filename == "":
        return "No file selected", 400

    pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], pdf_file.filename)
    pdf_file.save(pdf_path)

    job_text = request.form.get("job_desc", "")
    job_title = request.form.get("job_title", "Target Role")

    # Basic Extractor test("Running AI pipeline...")
    raw_resume_text = extract_text_from_pdf(pdf_path)
    resume_skills = clean_for_nlp(raw_resume_text)
    job_skills = clean_for_nlp(job_text)

    score, gap, extra = calculate_match_score(resume_skills, job_skills)

    # Get the system's current username to display in the frontend
    current_user = os.getlogin()

    return render_template(
        "result.html",
        score=score,
        gap=gap,
        extra=extra,
        job_title=job_title,
        job_description=job_text,
        job_skills=job_skills,
        resume_skills=resume_skills,
        resume_text=raw_resume_text,
        user_name=current_user,
    )


if __name__ == "__main__":
    print("🚀 Starting SkillGap-AI Web Server...")
    app.run(debug=True, port=5000)
