import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.modules.matcher import clean_for_nlp, calculate_match_score  # noqa: E402
from core.modules.extractor import extract_text_from_pdf  # noqa: E402


def analyze_custum_inputs(pdf_path, custom_job_text, role_type="technical"):
    # reading the pdf

    print(f"\n--- Testing for Role Type: {role_type.upper()} ---")
    print("Extracting text from PDF...")
    raw_resume_text = extract_text_from_pdf(pdf_path)
    resume_hard, resume_soft = clean_for_nlp(raw_resume_text)

    print("Analyzing Custom job description...")
    job_hard, job_soft = clean_for_nlp(custom_job_text)

    score, missing_hard, extra_hard, aug_hard, missing_soft, extra_soft, aug_soft = (
        calculate_match_score(
            resume_hard, resume_soft, job_hard, job_soft, role_type=role_type
        )
    )

    # 4. Display the Core Output
    print("\n=========================================")
    print("🎓 STUDENT SKILL GAP ANALYSIS")
    print("=========================================")
    print(f"🔥 MATCH SCORE  : {score}%")

    if missing_hard or missing_soft:
        print(f"📚 TECH STUDY LIST   : {missing_hard}")
        print(f"📚 SOFT SKILL LIST   : {missing_soft}")
        print("💡 TIP: Focus your upcoming projects on these missing skills!")
    else:
        print("🚀 STUDY LIST   : None! You have all the required skills!")

    print(f"🌟 EXTRA TECH SKILLS : {extra_hard}")
    print(f"🌟 EXTRA SOFT SKILLS : {extra_soft}")
    print("=========================================\n")


# --- TEST YOUR MAIN GOAL ---
def test_custom_job_matching():
    # 1. Point to your resume
    my_pdf = r"C:\Users\aksha\Desktop\SG_AI\tests\my_notes.pdf"

    # 2. Paste any job description you want to test right here
    pasted_job_description = """
    We are looking for a backend engineer/manager to join our team. 
    The ideal candidate will have strong experience with Python and SQL. 
    Knowledge of Django or Flask is a major plus. 
    Familiarity with AWS, Git, Agile, Scrum and Leadership is required.
    """

    # Run the custom analysis
    analyze_custum_inputs(my_pdf, pasted_job_description, "technical")
    analyze_custum_inputs(my_pdf, pasted_job_description, "management")


if __name__ == "__main__":
    test_custom_job_matching()
