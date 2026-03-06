import sys
import os
import mysql.connector

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.modules.matcher import clean_for_nlp, calculate_match_score

from core.modules.extractor import extract_text_from_pdf


def analyze_pdf_against_database_job(pdf_path, job_id):
    # reading the pdf

    print("Extracting text from PDF...")
    raw_resume_text = extract_text_from_pdf(pdf_path)
    resume_hard, resume_soft = clean_for_nlp(raw_resume_text)

    try:

        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="sg_ai",
        )

        cursor = db.cursor()
        cursor.execute("SELECT description_text FROM jobs WHERE id = %s", (job_id,))

        job_data = cursor.fetchone()
        db.close()

        if not job_data:
            print(f"Error: Could not find Job ID {job_id} in the database.")
            return

        job_title = job_data[0]
        job_hard, job_soft = clean_for_nlp(job_title)

        score, missing_hard, extra_hard, aug_hard, missing_soft, extra_soft, aug_soft = calculate_match_score(
            resume_hard, resume_soft, job_hard, job_soft, role_type="technical"
        )

        # 4. Display the Core Output
        print("\n=========================================")
        print("🎓 STUDENT SKILL GAP ANALYSIS")
        print("=========================================")
        print(f"🎯 TARGET ROLE  : {job_title}")
        print(f"🔥 MATCH SCORE  : {score}%")

        if missing_hard or missing_soft:
            print(f"📚 TECH STUDY LIST   : {missing_hard}")
            print(f"📚 SOFT SKILL LIST   : {missing_soft}")
            print(f"💡 TIP: Focus your upcoming projects on these missing skills!")
        else:
            print("🚀 STUDY LIST   : None! You have all the required skills!")

        print(f"🌟 EXTRA TECH SKILLS : {extra_hard}")
        print(f"🌟 EXTRA SOFT SKILLS : {extra_soft}")
        print("=========================================\n")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")


def test_pdf_match_against_db():
    test_pdf = r"C:\Users\aksha\Desktop\SG_AI\tests\my_notes.pdf"
    analyze_pdf_against_database_job(test_pdf, 3)
