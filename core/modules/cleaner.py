import re


IGNORE_WORDS = {
    "resume",
    "cv",
    "curriculum",
    "vitae",
    "profile",
    "contact",
    "email",
    "phone",
    "mobile",
    "linkedin",
    "github",
    "portfolio",
    "address",
    "location",
    "summary",
    "experience",
    "education",
    "skills",
}

LOCATION_WORDS = {
    "india",
    "remote",
    "bangalore",
    "bengaluru",
    "mumbai",
    "delhi",
    "new delhi",
    "pune",
    "hyderabad",
    "chennai",
    "kolkata",
    "noida",
    "gurgaon",
    "ghaziabad",
    "jaipur",
    "ahmedabad",
    "lucknow",
    "kochi",
}


def extract_emails(text):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    return re.findall(email_pattern, text, flags=0)


def extract_phone(text):
    phone_pattern = r"(?:\+91|0)?\s?\d{10}"
    return re.findall(phone_pattern, text, flags=0)


def _normalize_person_name(value):
    parts = re.split(r"\s+", value.strip())
    normalized_parts = []

    for part in parts:
        if not part:
            continue
        if part.isupper():
            normalized_parts.append(part.title())
        else:
            normalized_parts.append(part[0].upper() + part[1:])

    return " ".join(normalized_parts)


def _looks_like_location(value):
    lower_value = value.lower().strip()
    if lower_value in LOCATION_WORDS:
        return True

    tokens = lower_value.split()
    if not tokens:
        return False

    if all(token in LOCATION_WORDS for token in tokens):
        return True

    return False


def extract_name(text):
    lines = text.split("\n")[:25]
    strong_candidates = []
    weak_candidates = []

    for index, line in enumerate(lines):
        line_clean = re.sub(r"\s+", " ", line.strip(" -|\t"))
        if not line_clean:
            continue

        lower_line = line_clean.lower()
        if "@" in line_clean or sum(char.isdigit() for char in line_clean) > 3:
            continue
        if any(word in IGNORE_WORDS for word in lower_line.split()):
            continue
        if _looks_like_location(line_clean):
            continue
        if "," in line_clean or "|" in line_clean or "/" in line_clean:
            continue
        if not re.fullmatch(r"[A-Za-z][A-Za-z\s\.\-']*", line_clean):
            continue

        words = [word for word in line_clean.split() if word]
        word_count = len(words)
        if word_count == 0 or word_count > 4:
            continue

        candidate = _normalize_person_name(line_clean)

        # Prefer typical full-name patterns near the top of the resume.
        if 2 <= word_count <= 4:
            strong_candidates.append((index, candidate))
        elif word_count == 1 and index <= 2:
            weak_candidates.append((index, candidate))

    if strong_candidates:
        return strong_candidates[0][1]
    if weak_candidates:
        return weak_candidates[0][1]
    return "Candidate"


def cleaner_text(raw_file):
    text = raw_file.lower()
    text = text.replace("\n", " ")
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text
