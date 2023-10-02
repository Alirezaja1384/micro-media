from sqlalchemy.ext.declarative import declarative_base


class UpdateMixin:
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class BaseMixin(UpdateMixin):
    pass


Base = declarative_base(cls=BaseMixin)

__all__ = ["Base"]
