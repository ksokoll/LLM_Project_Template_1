# src/utils.py
import re
from typing import Optional

def sanitize_input(text: str) -> str:
    """
    Remove potentially dangerous characters from user input.
    
    Args:
        text: Raw user input
    
    Returns:
        Sanitized text
    """
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    
    # Remove excessive whitespace
    text = " ".join(text.split())
    
    return text.strip()


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
    
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def extract_json_from_markdown(text: str) -> Optional[str]:
    """
    Extract JSON content from markdown code blocks.
    
    Args:
        text: Text potentially containing ```json blocks
    
    Returns:
        Extracted JSON string or None
    """
    import re
    pattern = r"```json\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        return match.group(1)
    return None
