import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.modules.matcher import get_matching_data, clean_for_nlp, calculate_match_score

from core.modules.extractor import extract_text_from_pdf

def analyze_custum_inputs(pdf_path, custom_job_text):
    #reading the pdf

    print("Extracting text from PDF...")
    raw_resume_text = extract_text_from_pdf(pdf_path)
    resume_skills = clean_for_nlp(raw_resume_text)

    print("Analyzing Custom job description...")
    job_skills = clean_for_nlp(custom_job_text)

    score , gap , extra = calculate_match_score(resume_skills, job_skills)

        # 4. Display the Core Output
    print(f"\n=========================================")
    print(f"🎓 STUDENT SKILL GAP ANALYSIS")
    print(f"=========================================")
    print(f"🔥 MATCH SCORE  : {score}%")
        
    if gap:
            print(f"📚 STUDY LIST   : {gap}")
            print(f"💡 TIP: Focus your upcoming projects on these missing skills!")
    else:
            print(f"🚀 STUDY LIST   : None! You have all the required skills!")
            
    print(f"🌟 EXTRA SKILLS : {extra}")
    print(f"=========================================\n")




# --- TEST YOUR MAIN GOAL ---
# 1. Point to your resume
my_pdf = r"C:\Users\aksha\Desktop\SG_AI\tests\my_notes.pdf"

# 2. Paste any job description you want to test right here
pasted_job_description = """
We are looking for a backend engineer to join our team. 
The ideal candidate will have strong experience with Python and SQL. 
Knowledge of Django or Flask is a major plus. 
Familiarity with AWS and Git is required.
"""

# Run the custom analysis
analyze_custum_inputs(my_pdf, pasted_job_description)