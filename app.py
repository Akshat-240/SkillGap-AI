from flask import Flask, render_template, request
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from core.modules.extractor import extract_text_from_pdf
from core.modules.cleaner import extract_name
from core.modules.matcher import clean_for_nlp, calculate_match_score
from core.modules.database_manager import get_all_jobs, get_job_by_id

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/explore", methods=["GET"])
def explore():
    # Fetch all jobs to populate the dropdown
    jobs = get_all_jobs()
    return render_template("explore.html", jobs=jobs)


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
    role_type = request.form.get("role_type", "technical")

    # Basic Extractor test("Running AI pipeline...")
    raw_resume_text = extract_text_from_pdf(pdf_path)
    resume_hard, resume_soft = clean_for_nlp(raw_resume_text)
    job_hard, job_soft = clean_for_nlp(job_text)

    score, missing_hard, extra_hard, aug_hard, missing_soft, extra_soft, aug_soft = calculate_match_score(
        resume_hard, resume_soft, job_hard, job_soft, role_type=role_type
    )

    # Get the extracted candidate name
    candidate_name = extract_name(raw_resume_text)

    return render_template(
        "result.html",
        score=score,
        aug_hard=aug_hard,
        aug_soft=aug_soft,
        raw_hard_gap_len=len(missing_hard),
        raw_soft_gap_len=len(missing_soft),
        extra_hard=extra_hard,
        extra_soft=extra_soft,
        job_title=job_title,
        job_description=job_text,
        job_hard=job_hard,
        job_soft=job_soft,
        resume_hard=resume_hard,
        resume_soft=resume_soft,
        resume_text=raw_resume_text,
        user_name=candidate_name,
        role_type=role_type,
    )


@app.route("/analyze_predefined", methods=["POST"])
def analyze_predefined():
    if "resume" not in request.files:
        return "No file part in the request", 400

    pdf_file = request.files["resume"]
    if pdf_file.filename == "":
        return "No file selected", 400

    pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], pdf_file.filename)
    pdf_file.save(pdf_path)

    job_id = request.form.get("job_id")
    role_type = request.form.get("role_type", "technical")

    # Fetch the predefined job from the DB
    job_data = get_job_by_id(job_id)
    if not job_data:
        return "Invalid Job Profile Selected", 400

    job_title = job_data["title"]
    job_text = job_data["description_text"]

    # Basic Extractor test("Running AI pipeline...")
    raw_resume_text = extract_text_from_pdf(pdf_path)
    resume_hard, resume_soft = clean_for_nlp(raw_resume_text)
    job_hard, job_soft = clean_for_nlp(job_text)

    score, missing_hard, extra_hard, aug_hard, missing_soft, extra_soft, aug_soft = calculate_match_score(
        resume_hard, resume_soft, job_hard, job_soft, role_type=role_type
    )

    # Get the extracted candidate name
    candidate_name = extract_name(raw_resume_text)

    return render_template(
        "result.html",
        score=score,
        aug_hard=aug_hard,
        aug_soft=aug_soft,
        raw_hard_gap_len=len(missing_hard),
        raw_soft_gap_len=len(missing_soft),
        extra_hard=extra_hard,
        extra_soft=extra_soft,
        job_title=job_title,
        job_description=job_text,
        job_hard=job_hard,
        job_soft=job_soft,
        resume_hard=resume_hard,
        resume_soft=resume_soft,
        resume_text=raw_resume_text,
        user_name=candidate_name,
        role_type=role_type,
    )


if __name__ == "__main__":
    print("🚀 Starting SkillGap-AI Web Server...")
    app.run(debug=True, port=5000)
