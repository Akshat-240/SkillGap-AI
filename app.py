import hashlib
import json
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from core.modules.cleaner import extract_name
from core.modules.database_manager import (
    get_all_jobs,
    get_database_status,
    get_job_by_id,
)
from core.modules.extractor import PDFExtractionError, extract_text_from_pdf
from core.modules.matcher import calculate_match_score, clean_for_nlp
from core.modules.skill_metadata import HARD_SKILLS, SKILL_METADATA, SOFT_SKILLS

# Walk upward from app.py's location to find .env (works regardless of cwd)
_here = Path(__file__).resolve()
for _p in [_here, *_here.parents]:
    if (_p / ".env").is_file():
        load_dotenv(_p / ".env", override=True)
        break
else:
    load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AI analyzer import
try:
    from core.modules.ai_analyzer import extract_skills_with_ai, generate_roadmap
    logger.info("AI features: ENABLED (Gemini)")
    _AI_AVAILABLE = True
except Exception as e:
    logger.warning("AI features: DISABLED (%s)", e)
    _AI_AVAILABLE = False


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
DB_PATH = BASE_DIR / "history.db"
ALLOWED_EXTENSIONS = {".pdf"}
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024
MAX_JOB_TITLE_LENGTH = 120
MAX_JOB_DESC_LENGTH = 8000

app = Flask(__name__)
# FIX: Secret key from env — never hardcode
app.secret_key = os.getenv("SECRET_KEY", os.urandom(32))

app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE_BYTES
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)

UPLOAD_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# SQLite history store
# ---------------------------------------------------------------------------

def _init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  TEXT NOT NULL,
                created_at  TEXT NOT NULL,
                user_name   TEXT,
                job_title   TEXT,
                role_type   TEXT,
                score       REAL,
                missing_count INTEGER,
                known_count   INTEGER,
                roadmap_mode  TEXT
            )
        """)
        conn.commit()

_init_db()


def _save_history(session_id, context):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT INTO analysis_history
                  (session_id, created_at, user_name, job_title, role_type,
                   score, missing_count, known_count, roadmap_mode)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                datetime.utcnow().isoformat(timespec="seconds"),
                context.get("user_name", ""),
                context.get("job_title", ""),
                context.get("role_type", ""),
                context.get("score", 0),
                context.get("raw_hard_gap_len", 0) + context.get("raw_soft_gap_len", 0),
                len(context.get("resume_hard", [])) + len(context.get("resume_soft", [])),
                context.get("ai_roadmap_status", {}).get("mode", "unknown"),
            ))
            conn.commit()
    except Exception as exc:
        logger.warning("Failed to save history: %s", exc)


def _get_history(limit=20):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM analysis_history ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(r) for r in rows]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# In-memory roadmap cache  {cache_key: list[dict]}
# ---------------------------------------------------------------------------
_roadmap_cache: dict[str, list] = {}


def _roadmap_cache_key(missing_skills: list[str], role_type: str) -> str:
    normalised = sorted(s.lower().strip() for s in missing_skills)
    raw = json.dumps(normalised) + "|" + role_type
    return hashlib.md5(raw.encode()).hexdigest()


def _get_cached_roadmap(missing_skills, role_type):
    key = _roadmap_cache_key(missing_skills, role_type)
    return _roadmap_cache.get(key)


def _set_cached_roadmap(missing_skills, role_type, roadmap):
    key = _roadmap_cache_key(missing_skills, role_type)
    _roadmap_cache[key] = roadmap
    # Keep cache size reasonable
    if len(_roadmap_cache) > 200:
        oldest = next(iter(_roadmap_cache))
        del _roadmap_cache[oldest]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _allowed_file(filename):
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def _normalize_role_type(raw_role_type):
    return "management" if raw_role_type == "management" else "technical"


def _validate_inputs(job_title, job_text):
    """Return error string or None."""
    if not job_text:
        return "Please enter a job description."
    if len(job_title) > MAX_JOB_TITLE_LENGTH:
        return f"Job title must be under {MAX_JOB_TITLE_LENGTH} characters."
    if len(job_text) > MAX_JOB_DESC_LENGTH:
        return f"Job description must be under {MAX_JOB_DESC_LENGTH} characters."
    if len(job_text) < 30:
        return "Job description is too short — please add more detail."
    return None


def _save_uploaded_resume(pdf_file):
    filename = secure_filename(pdf_file.filename or "")
    if not filename:
        raise ValueError("Please choose a PDF resume before analyzing.")
    if not _allowed_file(filename):
        raise ValueError("Only PDF resumes are supported right now.")
    stored_name = f"{uuid4().hex}_{filename}"
    saved_path = UPLOAD_DIR / stored_name
    pdf_file.save(saved_path)
    return saved_path


# ---------------------------------------------------------------------------
# Hybrid Skill Extraction
# ---------------------------------------------------------------------------

def _extract_skills_hybrid(text: str):
    kw_hard, kw_soft = clean_for_nlp(text)
    if not _AI_AVAILABLE:
        return kw_hard, kw_soft
    try:
        result = extract_skills_with_ai(text)
        if result:
            ai_hard, ai_soft = result
            final_hard = kw_hard | (ai_hard & kw_hard)
            final_soft = kw_soft | (ai_soft & kw_soft)
            return final_hard, final_soft
    except Exception:
        pass
    return kw_hard, kw_soft


# ---------------------------------------------------------------------------
# Learning path builders
# ---------------------------------------------------------------------------

def _build_learning_path_entries(roadmap, aug_hard, aug_soft):
    entries = []
    augmented_lookup = {
        item.get("skill", "").strip().lower(): item
        for item in (aug_hard + aug_soft)
        if item.get("skill")
    }

    if roadmap:
        for index, step in enumerate(roadmap, start=1):
            skill = str(step.get("skill", "")).strip().lower()
            if not skill:
                continue
            skill_metadata = SKILL_METADATA.get(skill, {})
            augmented_item = augmented_lookup.get(skill, {})
            if skill in HARD_SKILLS:
                category = "technical"
            elif skill in SOFT_SKILLS:
                category = "soft skill"
            else:
                category = augmented_item.get("category", "skill")
            entries.append({
                "skill": skill,
                "order": int(step.get("order", index)),
                "week_estimate": step.get("week_estimate"),
                "why_first": step.get("why_first", ""),
                "quick_win": step.get("quick_win", "") or skill_metadata.get("project", ""),
                "unlocks": step.get("unlocks", []),
                "learning_paths": skill_metadata.get("learning_paths") or augmented_item.get("learning_paths", []),
                "project": skill_metadata.get("project", "") or augmented_item.get("project", ""),
                "category": category,
                "source": "ai",
                "done": False,
            })
        return entries

    combined_missing = [("technical", item) for item in aug_hard] + [("soft skill", item) for item in aug_soft]
    for index, (category, item) in enumerate(combined_missing, start=1):
        entries.append({
            "skill": item.get("skill", ""),
            "order": index,
            "week_estimate": None,
            "why_first": item.get("contextual_warning") or "This skill is missing from your current resume for the target role.",
            "quick_win": item.get("project", ""),
            "unlocks": [],
            "learning_paths": item.get("learning_paths", []),
            "project": item.get("project", ""),
            "category": category,
            "source": "metadata",
            "done": False,
        })
    return entries


def _build_ai_roadmap_status(ai_enabled, all_missing, roadmap, error_message=None):
    if not ai_enabled:
        return {"mode": "fallback", "title": "AI roadmap unavailable",
                "message": "Gemini is not configured, showing curated learning paths instead."}
    if not all_missing:
        return {"mode": "not_needed", "title": "No roadmap needed",
                "message": "No missing skills were found — nothing for AI to sequence."}
    if error_message:
        return {"mode": "fallback", "title": "AI roadmap failed",
                "message": f"Gemini could not generate a roadmap. Showing curated paths instead. ({error_message})"}
    if roadmap:
        return {"mode": "ai", "title": "AI roadmap active",
                "message": "Gemini generated and sequenced this learning plan."}
    return {"mode": "fallback", "title": "AI roadmap empty",
            "message": "Gemini was available but returned no roadmap. Showing curated paths instead."}


def _persist_learning_path_session(candidate_name, job_title, role_type, roadmap,
                                   learning_path_entries, ai_roadmap_status, all_known, all_missing):
    session["roadmap"] = roadmap
    session["learning_path_entries"] = learning_path_entries
    session["learning_path_context"] = {
        "user_name": candidate_name,
        "job_title": job_title,
        "role_type": role_type,
        "ai_enabled": _AI_AVAILABLE,
        "has_ai_roadmap": bool(roadmap),
        "ai_roadmap_status": ai_roadmap_status,
    }
    session["learning_path_inputs"] = {
        "known_skills": sorted(all_known),
        "missing_skills": list(all_missing),
        "role_type": role_type,
        "job_title": job_title,
        "user_name": candidate_name,
    }


def _retry_ai_learning_paths_from_session():
    lpi = session.get("learning_path_inputs", {})
    missing_skills = lpi.get("missing_skills", [])
    known_skills = set(lpi.get("known_skills", []))
    role_type = lpi.get("role_type", "technical")
    if not _AI_AVAILABLE or not missing_skills:
        return
    cached = _get_cached_roadmap(missing_skills, role_type)
    if cached:
        roadmap = cached
    else:
        try:
            roadmap = generate_roadmap(missing_skills, known_skills, role_type)
            if not roadmap:
                return
            _set_cached_roadmap(missing_skills, role_type, roadmap)
        except Exception as exc:
            logger.warning("Learning paths AI retry failed: %s", exc)
            return
    existing_entries = session.get("learning_path_entries", [])
    aug_hard = [i for i in existing_entries if i.get("category") == "technical"]
    aug_soft = [i for i in existing_entries if i.get("category") == "soft skill"]
    learning_path_entries = _build_learning_path_entries(roadmap, aug_hard, aug_soft)
    ai_roadmap_status = _build_ai_roadmap_status(_AI_AVAILABLE, missing_skills, roadmap)
    _persist_learning_path_session(
        lpi.get("user_name", "Candidate"), lpi.get("job_title", "Target Role"),
        role_type, roadmap, learning_path_entries, ai_roadmap_status, known_skills, missing_skills,
    )


# ---------------------------------------------------------------------------
# Core Analysis
# ---------------------------------------------------------------------------

def _analyze_resume(saved_path, job_title, job_text, role_type):
    raw_resume_text = extract_text_from_pdf(saved_path)
    resume_hard, resume_soft = _extract_skills_hybrid(raw_resume_text)
    job_hard, job_soft = _extract_skills_hybrid(job_text)

    score, missing_hard, extra_hard, aug_hard, missing_soft, extra_soft, aug_soft = calculate_match_score(
        resume_hard, resume_soft, job_hard, job_soft, role_type=role_type,
    )

    all_known = resume_hard | resume_soft
    all_missing = list(missing_hard) + list(missing_soft)

    # FIX: log when skills are being dropped
    if len(all_missing) > 10:
        logger.info(
            "Capping missing skills from %d to 10 for roadmap generation (dropped: %s)",
            len(all_missing), all_missing[10:],
        )
    all_missing = all_missing[:10]

    roadmap = []
    roadmap_error = None

    if _AI_AVAILABLE and all_missing:
        # Check cache first — saves Gemini calls on repeated analyses
        cached = _get_cached_roadmap(all_missing, role_type)
        if cached:
            logger.info("Using cached roadmap (%d steps)", len(cached))
            roadmap = cached
        else:
            try:
                roadmap = generate_roadmap(all_missing, all_known, role_type)
                if roadmap:
                    _set_cached_roadmap(all_missing, role_type, roadmap)
            except Exception as exc:
                roadmap_error = str(exc)
                logger.warning("AI roadmap generation failed: %s", exc)

    candidate_name = extract_name(raw_resume_text)
    learning_path_entries = _build_learning_path_entries(roadmap, aug_hard, aug_soft)
    ai_roadmap_status = _build_ai_roadmap_status(_AI_AVAILABLE, all_missing, roadmap, roadmap_error)

    _persist_learning_path_session(
        candidate_name, job_title, role_type, roadmap,
        learning_path_entries, ai_roadmap_status, all_known, all_missing,
    )

    context = {
        "score": score,
        "aug_hard": aug_hard,
        "aug_soft": aug_soft,
        "raw_hard_gap_len": len(missing_hard),
        "raw_soft_gap_len": len(missing_soft),
        "extra_hard": extra_hard,
        "extra_soft": extra_soft,
        "job_title": job_title,
        "job_description": job_text,
        "job_hard": sorted(job_hard),
        "job_soft": sorted(job_soft),
        "resume_hard": sorted(resume_hard),
        "resume_soft": sorted(resume_soft),
        "resume_text": raw_resume_text,
        "user_name": candidate_name,
        "role_type": role_type,
        "roadmap": roadmap,
        "ai_enabled": _AI_AVAILABLE,
        "ai_roadmap_status": ai_roadmap_status,
    }

    _save_history(session.get("_id", "anon"), context)
    return context


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/explore")
def explore():
    return render_template(
        "explore.html",
        jobs=get_all_jobs(),
        database_status=get_database_status(),
    )


@app.route("/learning_paths")
def learning_paths():
    learning_path_context = session.get("learning_path_context", {})
    if _AI_AVAILABLE and not learning_path_context.get("has_ai_roadmap"):
        _retry_ai_learning_paths_from_session()
    # Merge any "done" state the user toggled
    entries = session.get("learning_path_entries", [])
    done_set = set(session.get("skills_done", []))
    for e in entries:
        e["done"] = e["skill"] in done_set
    return render_template(
        "learning_paths.html",
        paths=entries,
        context=session.get("learning_path_context", {}),
    )


@app.route("/history")
def history():
    return render_template("history.html", records=_get_history())


@app.route("/health")
def health():
    return jsonify({"status": "ok", "ai_enabled": _AI_AVAILABLE})


# ---- AJAX: toggle a skill as done / not done ----
@app.route("/api/skill_done", methods=["POST"])
def api_skill_done():
    data = request.get_json(silent=True) or {}
    skill = str(data.get("skill", "")).lower().strip()
    done = bool(data.get("done", True))
    if not skill:
        return jsonify({"ok": False}), 400
    done_set = set(session.get("skills_done", []))
    if done:
        done_set.add(skill)
    else:
        done_set.discard(skill)
    session["skills_done"] = list(done_set)
    return jsonify({"ok": True, "skills_done": list(done_set)})


# ---- Loading page — shown immediately, JS polls until result is ready ----
@app.route("/analyzing")
def analyzing():
    return render_template("analyzing.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    pdf_file = request.files.get("resume")
    job_text = request.form.get("job_desc", "").strip()
    job_title = request.form.get("job_title", "Target Role").strip() or "Target Role"
    role_type = _normalize_role_type(request.form.get("role_type", "technical"))

    if not pdf_file or not pdf_file.filename:
        return render_template("index.html", error="Please upload a PDF resume.")

    err = _validate_inputs(job_title, job_text)
    if err:
        return render_template("index.html", error=err)

    saved_path = None
    try:
        saved_path = _save_uploaded_resume(pdf_file)
        context = _analyze_resume(saved_path, job_title, job_text, role_type)
        return render_template("result.html", **context)
    except PDFExtractionError as e:
        return render_template("index.html", error=f"Could not read PDF: {e}")
    except Exception as e:
        logger.exception("Analyze error")
        return render_template("index.html", error=str(e))
    finally:
        if saved_path and saved_path.exists():
            saved_path.unlink()


@app.route("/analyze_predefined", methods=["POST"])
def analyze_predefined():
    pdf_file = request.files.get("resume")
    job_id = request.form.get("job_id")
    role_type = _normalize_role_type(request.form.get("role_type", "technical"))

    if not pdf_file or not pdf_file.filename:
        return render_template("explore.html", error="Please upload a PDF resume.", jobs=get_all_jobs(), database_status=get_database_status())
    if not job_id:
        return render_template("explore.html", error="Please select a job.", jobs=get_all_jobs(), database_status=get_database_status())

    job_data = get_job_by_id(job_id)
    if not job_data:
        return render_template("explore.html", error="Job not found.", jobs=get_all_jobs(), database_status=get_database_status())

    saved_path = None
    try:
        saved_path = _save_uploaded_resume(pdf_file)
        context = _analyze_resume(saved_path, job_data["title"], job_data["description_text"], role_type)
        return render_template("result.html", **context)
    except PDFExtractionError as e:
        return render_template("explore.html", error=f"Could not read PDF: {e}", jobs=get_all_jobs(), database_status=get_database_status())
    except Exception as e:
        logger.exception("Analyze predefined error")
        return render_template("explore.html", error=str(e), jobs=get_all_jobs(), database_status=get_database_status())
    finally:
        if saved_path and saved_path.exists():
            saved_path.unlink()


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Starting SkillGap-AI Web Server...")
    print("AI features:", "ENABLED" if _AI_AVAILABLE else "DISABLED")
    app.run(debug=True, port=5001)