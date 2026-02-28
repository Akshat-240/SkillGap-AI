import re


def extract_emails(text):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text, flags=0)
    return emails


def extract_phone(text):
    phone_pattern = r"(?:\+91|0)?\s?\d{10}"
    phone_no = re.findall(phone_pattern, text, flags=0)
    return phone_no


def cleaner_text(raw_file):

    text = raw_file.lower()

    text = text.replace("\n", " ")

    text = re.sub(r"[^\w\s]", "", text)

    text = re.sub(r"\s+", " ", text)

    return text
