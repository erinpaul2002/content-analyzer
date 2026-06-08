# Approximate token count (1 token ≈ 4 chars) to avoid loading heavy transformers library
def count_tokens(text: str) -> int:
    return max(1, len(text.strip()) // 4)
