from pydantic import BaseModel


def snake_to_camel(snake: str) -> str:
    first, *rest = snake.split("_")
    return "".join([first, *map(str.title, rest)])


class APIModel(BaseModel):
    model_config = {
        "alias_generator": snake_to_camel,
        "populate_by_name": True,
    }
