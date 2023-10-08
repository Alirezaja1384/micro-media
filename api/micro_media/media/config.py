from pydantic import BaseModel


# <Base>
class BaseMediaTypeConfig(BaseModel):
    max_file_size: int | None = None
    allowed_formats: list[str] | None = None


# </Base>


# <Image>
class ImageMediaResizeConfig(BaseModel):
    max_width: int
    max_height: int


class ImageMediaForceFormatConfig(BaseModel):
    pil_format: str
    file_extension: str
    convert_mode: str


class ImageMediaConfig(BaseMediaTypeConfig):
    force_format: ImageMediaForceFormatConfig | None = None
    resize: ImageMediaResizeConfig | None = None


# <Image>


# <Bundle>
class MediaConfig(BaseModel):
    image: ImageMediaConfig
    video: BaseMediaTypeConfig
    document: BaseMediaTypeConfig


# </Bundle>
