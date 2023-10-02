from typing import TypeVar

from fastapi import HTTPException

T = TypeVar("T")


def truthy_or_404(obj, message: str | None = None):
    """Raises an HTTPException(404) if val is falsy.

    Args:
        obj (T): The object.
        message (str | None): The 404's message.

    Raises:
        HTTPException: If obj is falsy.

    Returns:
        T: The given object if truthy.
    """
    if not obj:
        raise HTTPException(status_code=404, detail=message or "Not found.")

    return obj
