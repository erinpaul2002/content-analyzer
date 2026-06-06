import os
os.environ["HF_HOME"] = "/tmp"

from functools import lru_cache
from transformers import AutoTokenizer
from config.settings import settings

MODEL_NAME = settings.tokenizer_model

@lru_cache(maxsize=1)
def get_tokenizer():
    return AutoTokenizer.from_pretrained(MODEL_NAME)

def count_tokens(text: str) -> int:
    cleaned_text = text.strip()
    tokenizer = get_tokenizer()
    tokens = tokenizer.encode(cleaned_text, add_special_tokens=False)
    return len(tokens)
