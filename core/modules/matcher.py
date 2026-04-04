import re

from core.modules.skill_metadata import (
    HARD_SKILL_METADATA,
    SOFT_SKILL_METADATA,
)

# Lightweight library used by the optional `analyze_skills` helper.
MASTER_SKILLS = {
    "python",
    "java",
    "c++",
    "javascript",
    "html",
    "css",
    "sql",
    "flask",
    "django",
    "aws",
    "azure",
    "docker",
    "kubernetes",
    "git",
    "nlp",
    "ml",
    "ai",
    "dsa",
    "cybersecurity",
    "sqlite",
    "github",
}

_WORD_EDGE = r"[a-z0-9]"


def _build_skill_pattern(skill):
    escaped = re.escape(skill.lower())
    return re.compile(rf"(?<!{_WORD_EDGE}){escaped}(?!{_WORD_EDGE})")


def _extract_skills(text, skills):
    text_clean = (text or "").lower()
    return {
        skill
        for skill in skills
        if _build_skill_pattern(skill).search(text_clean)
    }


def _tokenize(text):
    return set(re.findall(r"[a-z0-9\.\+#/]+", (text or "").lower()))


def analyze_skills(resume_text, job_text):
    """
    A simple overlap-based scorer for quick debugging and CLI experiments.
    """
    resume_skills = _extract_skills(resume_text, MASTER_SKILLS)
    job_skills = _extract_skills(job_text, MASTER_SKILLS)

    matched = sorted(job_skills.intersection(resume_skills))
    gap = sorted(job_skills - resume_skills)
    extra = sorted(resume_skills - job_skills)

    resume_tokens = _tokenize(resume_text)
    job_tokens = _tokenize(job_text)
    token_overlap = (
        len(resume_tokens.intersection(job_tokens)) / len(job_tokens)
        if job_tokens
        else 1.0
    )
    skill_overlap = len(matched) / len(job_skills) if job_skills else token_overlap

    final_score = round(((skill_overlap * 0.7) + (token_overlap * 0.3)) * 100, 1)
    return final_score, matched, gap, extra


def clean_for_nlp(text):
    hard_skills = _extract_skills(text, HARD_SKILL_METADATA.keys())
    soft_skills = _extract_skills(text, SOFT_SKILL_METADATA.keys())
    return hard_skills, soft_skills


def _build_augmented_gap(missing_skills, resume_skills, metadata):
    augmented = []

    for skill in sorted(missing_skills):
        meta = metadata.get(skill, {})
        warning = ""

        implied_skills = meta.get("implied_by", [])
        if implied_skills:
            related_skills = sorted(set(implied_skills).intersection(resume_skills))
            if related_skills:
                known = ", ".join(item.title() for item in related_skills)
                warning = (
                    f"You already mention {known}, so you may know "
                    f"{skill.title()}. Consider naming it explicitly."
                )

        learning_paths = meta.get("learning_paths", [])
        learning_title = learning_paths[0]["title"] if learning_paths else ""

        augmented.append(
            {
                "skill": skill,
                "learning_paths": learning_paths,
                "project": meta.get("project", ""),
                "contextual_warning": warning,
                "warning": warning,
                "learning": learning_title,
            }
        )

    return augmented


def calculate_match_score(
    resume_hard,
    resume_soft,
    job_hard,
    job_soft,
    role_type="technical",
):
    matched_hard = resume_hard.intersection(job_hard)
    matched_soft = resume_soft.intersection(job_soft)

    missing_hard = job_hard - resume_hard
    missing_soft = job_soft - resume_soft

    extra_hard = resume_hard - job_hard
    extra_soft = resume_soft - job_soft

    aug_hard = _build_augmented_gap(
        missing_hard,
        resume_hard,
        HARD_SKILL_METADATA,
    )
    aug_soft = _build_augmented_gap(
        missing_soft,
        resume_soft,
        SOFT_SKILL_METADATA,
    )

    total_required = len(job_hard) + len(job_soft)
    if total_required == 0:
        return (
            100.0,
            sorted(missing_hard),
            sorted(extra_hard),
            aug_hard,
            sorted(missing_soft),
            sorted(extra_soft),
            aug_soft,
        )

    if role_type == "management":
        hard_weight = 0.6
        soft_weight = 0.4
    else:
        hard_weight = 0.8
        soft_weight = 0.2

    matched_weight = (len(matched_hard) * hard_weight) + (
        len(matched_soft) * soft_weight
    )
    total_possible_weight = (len(job_hard) * hard_weight) + (
        len(job_soft) * soft_weight
    )

    score = (
        (matched_weight / total_possible_weight) * 100
        if total_possible_weight > 0
        else 100.0
    )

    return (
        round(score, 1),
        sorted(missing_hard),
        sorted(extra_hard),
        aug_hard,
        sorted(missing_soft),
        sorted(extra_soft),
        aug_soft,
    )
