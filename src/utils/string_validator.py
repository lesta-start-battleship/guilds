import re

from settings import settings

pattern = fr'^[A-Za-z0-9_]{{{settings.tag_min_length},{settings.tag_max_length}}}$'

def validate_str(string: str, pattern: str = pattern) -> bool:
    return re.fullmatch(pattern, string) is not None