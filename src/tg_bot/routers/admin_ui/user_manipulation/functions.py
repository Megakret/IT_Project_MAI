def validate_username(tag: str) -> bool:
    return (
        tag.startswith("@")
        and tag.isascii()
        and len(set(" ,.:/!\\\"'?") & set(tag)) == 0
    )
