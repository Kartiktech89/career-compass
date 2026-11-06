def is_valid_full_name(value: str) -> bool:
    """Return whether a full name contains only letters and spaces."""
    name = value.strip()
    return bool(name) and all(character.isalpha() or character == " " for character in name)


def is_valid_technical_domain(value: str) -> bool:
    """Return whether a custom academic domain appears technical or engineering-related."""
    domain = " ".join(value.strip().lower().split())
    technical_terms = (
        "engineering", "technology", "computer", "software", "information",
        "data", "artificial", "intelligence", "electronics", "electrical",
        "mechanical", "civil", "robotics", "cyber", "security", "network",
        "embedded", "telecommunication", "instrumentation", "aerospace",
        "biomedical", "chemical", "automation", "cloud", "web", "mobile",
        "mathematics", "physics",
    )
    return bool(domain) and any(term in domain for term in technical_terms)
