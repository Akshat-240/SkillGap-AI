import unittest
from unittest.mock import patch

import app as app_module
from app import app
from core.modules import ai_analyzer
from core.modules.cleaner import extract_name
from core.modules.matcher import calculate_match_score, clean_for_nlp


class RuntimeSmokeTests(unittest.TestCase):
    def test_index_page_loads(self):
        client = app.test_client()
        response = client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"SkillGap-AI", response.data)

    def test_learning_paths_page_shows_empty_state_without_session_data(self):
        client = app.test_client()
        response = client.get("/learning_paths")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No learning path yet", response.data)
        self.assertIn(b"Back", response.data)
        self.assertIn(b"Home", response.data)

    def test_learning_paths_page_renders_session_entries(self):
        client = app.test_client()

        with client.session_transaction() as session_state:
            session_state["learning_path_context"] = {
                "user_name": "Akshay",
                "job_title": "Backend Developer",
                "role_type": "technical",
                "has_ai_roadmap": True,
                "ai_roadmap_status": {
                    "mode": "ai",
                    "title": "AI roadmap active",
                    "message": "Gemini generated and sequenced this learning plan.",
                },
            }
            session_state["learning_path_entries"] = [
                {
                    "skill": "python",
                    "order": 1,
                    "week_estimate": 3,
                    "why_first": "Core language for the backend stack.",
                    "quick_win": "Build a small CLI script.",
                    "unlocks": ["flask"],
                    "learning_paths": [],
                    "project": "",
                    "category": "technical",
                    "source": "ai",
                }
            ]

        response = client.get("/learning_paths")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Akshay, here’s your learning path".encode("utf-8"), response.data)
        self.assertIn(b"python", response.data)
        self.assertIn(b"~3 weeks", response.data)
        self.assertIn(b"AI roadmap active", response.data)

    def test_learning_paths_page_retries_ai_when_session_has_fallback(self):
        client = app.test_client()

        with client.session_transaction() as session_state:
            session_state["learning_path_context"] = {
                "user_name": "Akshay",
                "job_title": "Backend Developer",
                "role_type": "technical",
                "has_ai_roadmap": False,
                "ai_roadmap_status": {
                    "mode": "fallback",
                    "title": "AI roadmap empty",
                    "message": "Fallback was shown.",
                },
            }
            session_state["learning_path_inputs"] = {
                "known_skills": ["python", "flask"],
                "missing_skills": ["docker"],
                "role_type": "technical",
                "job_title": "Backend Developer",
                "user_name": "Akshay",
            }
            session_state["learning_path_entries"] = [
                {
                    "skill": "docker",
                    "order": 1,
                    "week_estimate": None,
                    "why_first": "Missing skill.",
                    "quick_win": "",
                    "unlocks": [],
                    "learning_paths": [],
                    "project": "",
                    "category": "technical",
                    "source": "metadata",
                }
            ]

        with patch.object(app_module, "_AI_AVAILABLE", True):
            with patch.object(
                app_module,
                "generate_roadmap",
                return_value=[
                    {
                        "skill": "docker",
                        "order": 1,
                        "week_estimate": 3,
                        "why_first": "Needed for packaging apps.",
                        "unlocks": ["containers"],
                        "quick_win": "Containerize a Flask app.",
                    }
                ],
            ):
                response = client.get("/learning_paths")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AI Sequenced Plan", response.data)
        self.assertIn(b"AI roadmap active", response.data)
        self.assertIn(b"Docker 101 Tutorial", response.data)

    def test_explore_page_contains_navigation_actions(self):
        client = app.test_client()
        response = client.get("/explore")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Home", response.data)
        self.assertIn(b"Back", response.data)
        self.assertIn(b"Learning Paths", response.data)

    def test_clean_for_nlp_handles_punctuation_skills(self):
        sample_text = "Worked with C++, Node.js, CI/CD, problem solving, and Agile."
        hard_skills, soft_skills = clean_for_nlp(sample_text)

        self.assertIn("c++", hard_skills)
        self.assertIn("node.js", hard_skills)
        self.assertIn("problem solving", soft_skills)
        self.assertIn("agile", soft_skills)

    def test_soft_skill_does_not_leak_into_hard_skills(self):
        hard_skills, soft_skills = clean_for_nlp(
            "Strong communication and collaboration with backend teams."
        )

        self.assertNotIn("communication", hard_skills)
        self.assertIn("communication", soft_skills)
        self.assertNotIn("collaboration", hard_skills)
        self.assertIn("collaboration", soft_skills)

    def test_calculate_match_score_uses_configured_weights(self):
        score, missing_hard, _, _, missing_soft, _, _ = calculate_match_score(
            resume_hard={"python"},
            resume_soft=set(),
            job_hard={"python"},
            job_soft={"communication"},
            role_type="technical",
        )

        self.assertEqual(score, 80.0)
        self.assertEqual(missing_hard, [])
        self.assertEqual(missing_soft, ["communication"])

    def test_extract_name_ignores_location_and_finds_person_name(self):
        resume_text = "\n".join(
            [
                "India",
                "Akshay Kumar",
                "Bengaluru",
                "akshay@example.com",
            ]
        )

        self.assertEqual(extract_name(resume_text), "Akshay Kumar")

    def test_safe_parse_json_handles_code_fences_and_extra_text(self):
        raw = """Here is the result:

```json
{"hard_skills": ["Python", "Flask"], "soft_skills": ["Communication"]}
```
"""

        parsed = ai_analyzer._safe_parse_json(raw, dict)

        self.assertEqual(
            parsed,
            {
                "hard_skills": ["Python", "Flask"],
                "soft_skills": ["Communication"],
            },
        )

    def test_generate_roadmap_retries_until_it_gets_valid_json(self):
        responses = [
            "not valid json",
            """[
                {
                    "skill": "docker",
                    "order": 1,
                    "week_estimate": 3,
                    "why_first": "Needed for packaging apps.",
                    "unlocks": ["containers"],
                    "quick_win": "Containerize a Flask app."
                }
            ]""",
        ]

        with patch.object(ai_analyzer, "_is_available", return_value=True):
            with patch.object(ai_analyzer, "_call_gemini", side_effect=responses):
                roadmap = ai_analyzer.generate_roadmap(
                    ["docker"],
                    {"python", "flask"},
                    "technical",
                )

        self.assertEqual(len(roadmap), 1)
        self.assertEqual(roadmap[0]["skill"], "docker")
        self.assertEqual(roadmap[0]["week_estimate"], 3)

    def test_ai_learning_path_entries_include_metadata_resources(self):
        entries = app_module._build_learning_path_entries(
            [
                {
                    "skill": "python",
                    "order": 1,
                    "week_estimate": 3,
                    "why_first": "Start with the core language.",
                    "unlocks": ["flask"],
                    "quick_win": "Write a CLI parser.",
                }
            ],
            [],
            [],
        )

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["source"], "ai")
        self.assertTrue(entries[0]["learning_paths"])
        self.assertEqual(entries[0]["learning_paths"][0]["title"], "Python for Everybody (edX)")


if __name__ == "__main__":
    unittest.main()
