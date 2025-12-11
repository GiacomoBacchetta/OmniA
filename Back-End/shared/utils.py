"""
Common utility functions
"""
import uuid
from datetime import datetime
from typing import Optional


def generate_id() -> str:
    """Generate unique ID"""
    return str(uuid.uuid4())


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format timestamp in ISO format"""
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat()


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_shortcode(instagram_url: str) -> str:
    """Extract shortcode from Instagram URL"""
    # Example: https://www.instagram.com/p/ABC123/ -> ABC123
    parts = instagram_url.rstrip('/').split('/')
    return parts[-1]


def validate_field_name(field: str) -> bool:
    """Validate field name format"""
    # Field names should be lowercase alphanumeric with underscores
    import re
    pattern = r'^[a-z0-9_]+$'
    return bool(re.match(pattern, field))
