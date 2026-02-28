import mysql.connector
import re


def get_matching_data(candidate_id, job_id):
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="sg_ai",
        )
        cursor = db.cursor()

        cursor.execute(
            "SELECT resume_text FROM candidates WHERE id = %s", (candidate_id,)
        )
        resume_text = cursor.fetchone()[0]

        cursor.execute("SELECT description_text FROM jobs WHERE id = %s", (job_id,))
        job_description = cursor.fetchone()[0]

        db.close()

        return resume_text, job_description

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None, None


# The Master Skill Dictionary for SkillGap-AI
MASTER_SKILLS = {
    # Core Languages
    "python",
    "java",
    "c",
    "c++",
    "c#",
    "javascript",
    "typescript",
    "ruby",
    "php",
    "swift",
    "kotlin",
    "go",
    "rust",
    "r",
    "bash",
    "perl",
    "scala",
    "dart",
    "matlab",
    # Web & UI (Frontend)
    "html",
    "css",
    "react",
    "angular",
    "vue",
    "next.js",
    "bootstrap",
    "tailwind",
    "jquery",
    "sass",
    "figma",
    # Backend Frameworks
    "django",
    "flask",
    "fastapi",
    "spring",
    "express",
    "node.js",
    "ruby on rails",
    "asp.net",
    "laravel",
    "graphql",
    "rest",
    "api",
    # Cloud & DevOps
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "jenkins",
    "git",
    "github",
    "gitlab",
    "terraform",
    "ansible",
    "linux",
    "unix",
    "ci/cd",
    "microservices",
    # Databases
    "sql",
    "nosql",
    "mysql",
    "postgresql",
    "sqlite",
    "mongodb",
    "redis",
    "cassandra",
    "oracle",
    "mariadb",
    "elasticsearch",
    "dynamodb",
    "firebase",
    # Data Science, AI & Machine Learning
    "ai",
    "ml",
    "nlp",
    "pandas",
    "numpy",
    "tensorflow",
    "keras",
    "pytorch",
    "scikit-learn",
    "matplotlib",
    "seaborn",
    "opencv",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "data science",
    "big data",
    "spark",
    "hadoop",
    "kafka",
    "powerbi",
    "tableau",
    "neural networks",
    # Core Computer Science Concepts
    "dsa",
    "oop",
    "cybersecurity",
    "agile",
    "scrum",
    "sdlc",
    "json",
    "xml",
}


def clean_for_nlp(text):

    stop_words = {
        "i",
        "am",
        "a",
        "and",
        "for",
        "the",
        "to",
        "with",
        "in",
        "of",
        "is",
        "looking",
        "we",
        "are",
    }
    text = re.sub(r"[^a-z\s]", " ", text.lower())
    words = text.split()

    unique_words = {
        word for word in words if word in MASTER_SKILLS and word not in stop_words
    }

    return unique_words


def calculate_match_score(resume_set, job_set):
    common_words = resume_set.intersection(job_set)

    # What to study (Job needs MINUS Resume has)
    missing_skills = job_set - resume_set

    # What makes you stand out (Resume has MINUS Job needs)
    extra_skills = resume_set - job_set

    if len(job_set) == 0:
        final_score = 0.0
    else:
        final_score = (len(common_words) / len(job_set)) * 100

    # Return all three variables
    return round(final_score, 2), missing_skills, extra_skills


def analyze_student_gap(student_id, target_job_id):
    # 1. Fetch exactly what this student needs using your existing function
    resume_text, job_desc = get_matching_data(student_id, target_job_id)

    if not resume_text or not job_desc:
        print("Error: Could not find that student or job in the database.")
        return

    print("\n=========================================")
    print("🎓 STUDENT SKILL GAP ANALYSIS")
    print("=========================================")

    # 2. Run the AI Cleaner
    student_skills = clean_for_nlp(resume_text)
    required_skills = clean_for_nlp(job_desc)

    print(f"Your Current Skills : {student_skills}")
    print(f"Target Job Requires : {required_skills}")
    print("-----------------------------------------")

    # 3. Calculate the match and the gap
    final_score, gap, extra = calculate_match_score(student_skills, required_skills)

    print(f"🔥 YOUR MATCH SCORE : {final_score}%")

    # 4. The Actionable Output (The Study List)
    if gap:
        print(f"📚 YOUR STUDY LIST  : {gap}")
        print("💡 TIP: Focus your upcoming projects on these missing skills!")
    else:
        print("🚀 YOUR STUDY LIST  : None! You have all the required skills!")
    print("=========================================\n")


# analyze_student_gap(1, 3)
