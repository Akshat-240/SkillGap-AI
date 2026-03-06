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
    "dsa",
    "oop",
    "cybersecurity",
    "json",
    "xml",
    "rest api",
    "rest apis",
    "system design",
    "ui/ux",
    "responsive design",
    "webpack",
    "statistics",
    "data visualization",
    "jira",
    "roadmap planning",
    "user research",
    "analytics",
    "networking",
    "adobe xd",
    "wireframing",
    "prototyping",
    "user testing",
    "typography",
    "color theory",
}


def clean_for_nlp(text):
    stop_words = {
        "i", "am", "a", "and", "for", "the", "to", "with", "in", 
        "of", "is", "looking", "we", "are"
    }
    text_lower = text.lower()
    words = set(re.sub(r"[^a-z0-9\+\.\#\s-]", " ", text_lower).split())

    hard_skills = set()
    for skill in MASTER_SKILLS:
        if any(char in skill for char in [" ", "+", ".", "#", "-"]):
            if skill in text_lower:
                hard_skills.add(skill)
        else:
            if skill in words and skill not in stop_words:
                hard_skills.add(skill)

    from core.modules.skill_metadata import SOFT_SKILLS
    soft_skills = set()
    for skill in SOFT_SKILLS:
        if " " in skill:
            if skill in text_lower:
                soft_skills.add(skill)
        else:
            if skill in words and skill not in stop_words:
                soft_skills.add(skill)

    return hard_skills, soft_skills


from core.modules.skill_metadata import SKILL_METADATA

def get_augmented_gap(missing_skills, resume_skills):
    augmented_gap = []
    
    for skill in missing_skills:
        skill_data = SKILL_METADATA.get(skill, {
            "learning_paths": [
                {"title": f"Search for '{skill.capitalize()}' on Coursera", "url": f"https://www.coursera.org/search?query={skill}"},
                {"title": f"Search for '{skill.capitalize()}' on YouTube", "url": f"https://www.youtube.com/results?search_query={skill}+tutorial"}
            ],
            "project": f"Build a small weekend project using {skill.capitalize()} to practice its core concepts.",
            "implied_by": []
        })
        
        contextual_warning = ""
        # Contextual logic check
        implied_match = [have for have in resume_skills if have in skill_data.get("implied_by", [])]
        if implied_match:
            implies_str = ", ".join(implied_match)
            contextual_warning = f"You have '{implies_str}' which often implies '{skill}', but ATS systems look for explicit keywords."

        augmented_gap.append({
            "skill": skill,
            "status": "Missing",
            "contextual_warning": contextual_warning,
            "learning_paths": skill_data.get("learning_paths", []),
            "project": skill_data.get("project", "")
        })
        
    return augmented_gap


def calculate_match_score(resume_hard, resume_soft, job_hard, job_soft, role_type="technical"):
    # Hard Skills calculation
    common_hard = resume_hard.intersection(job_hard)
    missing_hard = job_hard - resume_hard
    extra_hard = resume_hard - job_hard
    hard_score = (len(common_hard) / len(job_hard) * 100) if len(job_hard) > 0 else 0.0
    augmented_hard_gap = get_augmented_gap(missing_hard, resume_hard)

    # Soft Skills calculation
    common_soft = resume_soft.intersection(job_soft)
    missing_soft = job_soft - resume_soft
    extra_soft = resume_soft - job_soft
    soft_score = (len(common_soft) / len(job_soft) * 100) if len(job_soft) > 0 else 0.0
    augmented_soft_gap = get_augmented_gap(missing_soft, resume_soft)

    if len(job_hard) == 0 and len(job_soft) == 0:
        final_score = 0.0
    elif len(job_hard) == 0:
        final_score = soft_score
    elif len(job_soft) == 0:
        final_score = hard_score
    else:
        if role_type == "management":
            final_score = (hard_score * 0.6) + (soft_score * 0.4)
        else:
            final_score = (hard_score * 0.8) + (soft_score * 0.2)
            
    return (
        round(final_score, 2),
        missing_hard, extra_hard, augmented_hard_gap,
        missing_soft, extra_soft, augmented_soft_gap
    )


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
    resume_hard, resume_soft = clean_for_nlp(resume_text)
    job_hard, job_soft = clean_for_nlp(job_desc)

    print(f"Your Technical Skills : {resume_hard} | Soft Skills: {resume_soft}")
    print(f"Target Job Requires   : {job_hard} | Soft Skills: {job_soft}")
    print("-----------------------------------------")

    # 3. Calculate the match and the gap
    final_score, missing_hard, extra_hard, aug_hard, missing_soft, extra_soft, aug_soft = calculate_match_score(
        resume_hard, resume_soft, job_hard, job_soft, role_type="technical"
    )

    print(f"🔥 YOUR MATCH SCORE : {final_score}%")

    # 4. The Actionable Output (The Study List)
    if missing_hard or missing_soft:
        print(f"📚 YOUR TECH STUDY LIST  : {missing_hard}")
        print(f"📚 YOUR SOFT SKILL LIST  : {missing_soft}")
        print("💡 TIP: Focus your upcoming projects on these missing skills!")
    else:
        print("🚀 YOUR STUDY LIST  : None! You have all the required skills!")
    print("=========================================\n")


# analyze_student_gap(1, 3)
