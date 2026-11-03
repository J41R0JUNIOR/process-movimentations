import re
import unicodedata


INSTALLMENT_PATTERN = re.compile(r"\s*-\s*parcela\s+\d+\s*/\s*\d+\s*$", re.IGNORECASE)
PREFIX_PATTERN = re.compile(r"^(?:pag|dm|ifd|amazon\s+br)\s*[*.\s]+", re.IGNORECASE)


def normalize_merchant(description: str) -> str:
    value = INSTALLMENT_PATTERN.sub("", description.strip())
    value = PREFIX_PATTERN.sub("", value)
    value = unicodedata.normalize("NFKD", value)
    value = "".join(character for character in value if not unicodedata.combining(character))
    value = re.sub(r"[^a-zA-Z0-9]+", " ", value).strip().lower()
    return value


def is_installment(description: str) -> bool:
    return bool(INSTALLMENT_PATTERN.search(description))
