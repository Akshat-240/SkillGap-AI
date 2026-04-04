"""
core/modules/ai_analyzer.py

Gemini-powered skill extraction and learning roadmap generation.
"""

import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types as genai_types
except Exception:
    genai = None
    genai_types = None

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# .env loading — searches every parent folder, always uses override=True
# override=True ensures we always load even if app.py called load_dotenv first
# ---------------------------------------------------------------------------

def _load_env():
    # Walk from this file's location upward until we find a .env
    search_start = Path(__file__).resolve()
    for parent in [search_start, *search_start.parents]:
        candidate = parent / ".env"
        if candidate.is_file():
            load_dotenv(candidate, override=True)
            logger.info("Loaded .env from: %s", candidate)
            return
    # Final fallback: python-dotenv's built-in upward search from cwd
    load_dotenv(override=True)


_load_env()

# ---------------------------------------------------------------------------
# Client setup
# ---------------------------------------------------------------------------

_client_ready = False
_client = None

_MODELS = [
    "gemini-2.5-flash",       # primary  (thinking disabled)
    "gemini-2.0-flash",       # fallback (stable, same quota pool)
    "gemini-1.5-flash-8b",    # third fallback (lighter model, separate quota)
]


def _setup_client():
    global _client_ready, _client
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if genai is None:
        logger.warning("google-genai not installed — AI disabled.")
        return

    if not api_key:
        # Print a clear actionable message (visible in terminal without log config)
        print(
            "\n[SkillGap-AI] GEMINI_API_KEY is not set.\n"
            "  1. Create a .env file in your project root (SG_AI/.env)\n"
            "  2. Add this line:  GEMINI_API_KEY=your_key_here\n"
            "  3. Get a free key: https://aistudio.google.com/app/apikey\n"
            "  AI roadmap features will be disabled until the key is set.\n"
        )
        logger.warning("GEMINI_API_KEY not set — AI disabled.")
        return

    try:
        _client = genai.Client(api_key=api_key)
        _client_ready = True
        logger.info("Gemini client ready (key: ...%s)", api_key[-4:])
    except Exception as e:
        logger.warning("Gemini client init failed: %s", e)


_setup_client()


def _is_available() -> bool:
    return _client_ready


# ---------------------------------------------------------------------------
# JSON schemas — enforce exact output so parsing never fails
# ---------------------------------------------------------------------------

_ROADMAP_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "skill":         {"type": "string"},
            "order":         {"type": "integer"},
            "week_estimate": {"type": "integer"},
            "why_first":     {"type": "string"},
            "unlocks":       {"type": "array", "items": {"type": "string"}},
            "quick_win":     {"type": "string"},
        },
        "required": ["skill", "order", "week_estimate", "why_first", "unlocks", "quick_win"],
    },
}

_SKILL_SCHEMA = {
    "type": "object",
    "properties": {
        "hard_skills": {"type": "array", "items": {"type": "string"}},
        "soft_skills": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["hard_skills", "soft_skills"],
}

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

_SKILL_EXTRACTION_PROMPT = """\
You are a strict resume parser.

Rules:
- Extract ONLY skills explicitly mentioned in the text.
- DO NOT infer, guess, or add related skills.
- Normalize names (ReactJS -> react, JS -> javascript).
- hard_skills = tools, languages, frameworks.
- soft_skills = communication, leadership, teamwork, etc.

Text:
{text}
"""

_ROADMAP_PROMPT = """\
You are a technical career coach. Generate a sequenced learning roadmap.

Target role type: {role_type}
Candidate already knows: {known_skills}
Skills the candidate is MISSING - include ALL of them: {missing_skills}

Rules:
- Include EVERY skill from the missing list, no exceptions.
- Order from most foundational to most advanced.
- Keep why_first under 20 words.
- Keep quick_win under 25 words.
- unlocks: only skills from the missing list.
- week_estimate: integer 1-8.
"""

_ROADMAP_RETRY_PROMPT = """\
Generate a learning roadmap.
Role: {role_type}
Known: {known_skills}
Missing (include ALL): {missing_skills}
One entry per missing skill. Keep all strings under 25 words.
"""

# ---------------------------------------------------------------------------
# Core Gemini caller
# ---------------------------------------------------------------------------

def _build_config(schema: dict, max_tokens: int):
    """
    Build GenerateContentConfig with:
    - thinking_budget=0  : disables Gemini 2.5-flash thinking mode
                           (thinking mode was the root cause of truncated JSON)
    - response_schema    : forces exact JSON structure every time
    - temperature=0      : deterministic output
    """
    return genai_types.GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=max_tokens,
        response_mime_type="application/json",
        response_schema=schema,
        thinking_config=genai_types.ThinkingConfig(thinking_budget=0),
    )


def _call_gemini(
    prompt: str,
    schema: dict,
    max_tokens: int = 4096,
    max_retries: int = 4,
) -> str | None:
    """
    Call Gemini with schema enforcement, automatic rate-limit retry,
    and multi-model fallback.
    Free tier = 5 req/min. On 429: parse retry-after, wait, retry.
    After max_retries on one model, move to next model.
    """
    import re, time as _time

    if not _client_ready:
        return None

    def build_cfg(model_name: str):
        kwargs = dict(
            temperature=0.0,
            max_output_tokens=max_tokens,
            response_mime_type="application/json",
            response_schema=schema,
        )
        if "2.5" in model_name:
            kwargs["thinking_config"] = genai_types.ThinkingConfig(thinking_budget=0)
        return genai_types.GenerateContentConfig(**kwargs)

    for model in _MODELS:
        config = build_cfg(model)
        for attempt in range(max_retries):
            try:
                response = _client.models.generate_content(
                    model=model,
                    contents=[{"role": "user", "parts": [{"text": prompt}]}],
                    config=config,
                )
                if _is_truncated(response):
                    logger.warning("[%s] Truncated.", model)
                text = _extract_text(response)
                if text:
                    return text
                logger.warning("[%s] Empty response (attempt %d).", model, attempt+1)
                break

            except Exception as exc:
                err = str(exc)
                if "429" in err or "RESOURCE_EXHAUSTED" in err:
                    wait = 65
                    m = re.search(r"retry in\s+([\d.]+)s", err, re.I)
                    if not m:
                        m = re.search(r"retryDelay.*?(\d+)s", err, re.I)
                    if m:
                        wait = int(float(m.group(1))) + 3
                    if attempt < max_retries - 1:
                        logger.warning("[%s] Rate limited. Waiting %ds (attempt %d/%d)...",
                                       model, wait, attempt+2, max_retries)
                        _time.sleep(wait)
                        continue
                    else:
                        logger.warning("[%s] Rate limit persists after %d retries -> next model.", model, max_retries)
                        break
                elif "404" in err or "NOT_FOUND" in err:
                    logger.warning("[%s] Model not found -> next model.", model)
                    break
                else:
                    logger.warning("[%s] Failed: %s -> next model.", model, err[:120])
                    break

    logger.error("All Gemini models failed after retries.")
    return None


def _is_truncated(response) -> bool:
    try:
        for c in (getattr(response, "candidates", None) or []):
            r = str(getattr(c, "finish_reason", "") or "").upper()
            if "MAX_TOKENS" in r or r == "2":
                return True
    except Exception:
        pass
    return False


def _extract_text(response) -> str | None:
    text = getattr(response, "text", None)
    if isinstance(text, str) and text.strip():
        return text.strip()
    for c in (getattr(response, "candidates", None) or []):
        for p in (getattr(getattr(c, "content", None), "parts", None) or []):
            t = getattr(p, "text", None)
            if isinstance(t, str) and t.strip():
                return t.strip()
    return None

# ---------------------------------------------------------------------------
# JSON parsing (safety net — schema should make this trivial)
# ---------------------------------------------------------------------------

def _parse_json(raw: str | None, expected_type: type):
    if not raw:
        return None
    s = raw.strip()
    # Strip markdown fences if present
    if s.startswith("```"):
        lines = s.splitlines()
        lines = lines[1:] if lines[0].startswith("```") else lines
        lines = lines[:-1] if lines and lines[-1].strip() == "```" else lines
        s = "\n".join(lines).strip()
    try:
        parsed = json.loads(s)
        if isinstance(parsed, expected_type):
            return parsed
    except json.JSONDecodeError:
        pass
    # Scan for first [ or {
    dec = json.JSONDecoder()
    for i, ch in enumerate(s):
        if ch not in "[{":
            continue
        try:
            parsed, _ = dec.raw_decode(s[i:])
            if isinstance(parsed, expected_type):
                return parsed
        except json.JSONDecodeError:
            continue
    logger.warning("JSON parse failed. Raw: %r", s[:200])
    return None

# ---------------------------------------------------------------------------
# Sanitizers
# ---------------------------------------------------------------------------

def _sanitize_roadmap(data) -> list[dict]:
    if not isinstance(data, list):
        return []
    clean, seen = [], set()
    for i, step in enumerate(data, start=1):
        if not isinstance(step, dict):
            continue
        skill = str(step.get("skill", "")).lower().strip()
        if not skill or skill in seen:
            continue
        try:
            order = int(step.get("order", i))
        except (TypeError, ValueError):
            order = i
        try:
            weeks = max(1, min(int(step.get("week_estimate", 2)), 12))
        except (TypeError, ValueError):
            weeks = 2
        unlocks = step.get("unlocks", [])
        if not isinstance(unlocks, list):
            unlocks = []
        clean.append({
            "skill":         skill,
            "order":         order,
            "week_estimate": weeks,
            "why_first":     str(step.get("why_first", "")).strip(),
            "unlocks":       [str(u).lower().strip() for u in unlocks if str(u).strip()],
            "quick_win":     str(step.get("quick_win", "")).strip(),
        })
        seen.add(skill)
    clean.sort(key=lambda x: x["order"])
    return clean

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_skills_with_ai(text: str) -> tuple[set, set] | None:
    """Extract hard/soft skills from text. Returns (hard_set, soft_set) or None."""
    if not _is_available():
        return None
    prompt = _SKILL_EXTRACTION_PROMPT.format(text=text[:4000])
    raw    = _call_gemini(prompt, _SKILL_SCHEMA, max_tokens=512)
    data   = _parse_json(raw, dict)
    if not data:
        return None
    hard = set(str(s).lower().strip() for s in data.get("hard_skills", []) if s)
    soft = set(str(s).lower().strip() for s in data.get("soft_skills", []) if s)
    return set(sorted(hard)[:25]), set(sorted(soft)[:10])


def generate_roadmap(
    missing_skills: list[str],
    known_skills: set,
    role_type: str = "technical",
) -> list[dict]:
    """
    Generate a sequenced learning roadmap for missing_skills.
    Returns sorted list of step dicts, or [] on failure.
    """
    if not _is_available() or not missing_skills:
        return []

    capped = missing_skills[:10]
    known_str   = ", ".join(sorted(known_skills)) if known_skills else "none"
    missing_str = ", ".join(capped)

    for attempt, prompt in enumerate([
        _ROADMAP_PROMPT.format(role_type=role_type, known_skills=known_str, missing_skills=missing_str),
        _ROADMAP_RETRY_PROMPT.format(role_type=role_type, known_skills=known_str, missing_skills=missing_str),
    ], start=1):
        raw   = _call_gemini(prompt, _ROADMAP_SCHEMA, max_tokens=4096)
        steps = _sanitize_roadmap(_parse_json(raw, list))
        if steps:
            logger.info("Roadmap ready (attempt %d): %d steps", attempt, len(steps))
            return steps

    logger.error("Roadmap failed for: %s", missing_str)
    return []