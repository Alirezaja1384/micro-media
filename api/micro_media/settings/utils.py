def to_list(txt: str):
    return [item.strip() for item in txt.split(",")]


__all__ = ["to_list"]
