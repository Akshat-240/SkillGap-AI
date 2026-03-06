import re


def extract_emails(text):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text, flags=0)
    return emails


def extract_phone(text):
    phone_pattern = r"(?:\+91|0)?\s?\d{10}"
    phone_no = re.findall(phone_pattern, text, flags=0)
    return phone_no


def extract_name(text):
    # Process only the first few lines as the name is typically at the very top
    lines = text.split('\n')[:20]
    
    # Common words to ignore that might appear at the top
    ignore_words = {"resume", "cv", "curriculum", "vitae", "profile", "contact", "email", "phone"}
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        # Ignore if it's an email or phone number or contains typical header words
        if "@" in line_clean or sum(c.isdigit() for c in line_clean) > 5:
            continue
            
        words = line_clean.lower().split()
        if any(w in ignore_words for w in words):
            continue
            
        # A good candidate for a name usually has 1-4 words and mostly alphabetical characters
        word_count = len(line_clean.split())
        if 1 <= word_count <= 4 and re.match(r"^[A-Za-z\s\.\-]+$", line_clean):
            return line_clean.title()
            
    return "Candidate"


def cleaner_text(raw_file):

    text = raw_file.lower()

    text = text.replace("\n", " ")

    text = re.sub(r"[^\w\s]", "", text)

    text = re.sub(r"\s+", " ", text)

    return text
