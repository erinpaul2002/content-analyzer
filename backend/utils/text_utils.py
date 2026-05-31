import re


def clean_text(text: str) -> str:
    text = re.sub(r"^\s*(>>|--)+\s*", "", text)
    return re.sub(r"\s+", " ", text).strip()
