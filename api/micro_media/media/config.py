from pydantic import BaseModel, model_validator


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


class ImageMediaThumbnailSizeConfig(BaseModel):
    width: int
    height: int


class ImageMediaThumbnailConfig(BaseModel):
    default_size: str
    sizes: dict[str, ImageMediaThumbnailSizeConfig] = {}

    @model_validator(mode="after")
    def validate_default_size(self):
        valid_sizes = list((self.sizes or {}).keys())

        # Take first thumbnail as default if it's not manually set
        if not self.default_size and valid_sizes:
            self.default_size = valid_sizes[0]

        # Check if default_size is valid
        if self.default_size and self.default_size not in valid_sizes:
            raise ValueError("`default_size` must be present in `sizes`")

        return self


class ImageMediaConfig(BaseMediaTypeConfig):
    force_format: ImageMediaForceFormatConfig | None = None
    resize: ImageMediaResizeConfig | None = None
    thumbnails: ImageMediaThumbnailConfig | None = None


# <Image>


# <Bundle>
class MediaConfig(BaseModel):
    image: ImageMediaConfig
    video: BaseMediaTypeConfig
    document: BaseMediaTypeConfig


# </Bundle>
