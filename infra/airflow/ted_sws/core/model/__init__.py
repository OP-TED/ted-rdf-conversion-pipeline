#!/usr/bin/python3

# __init__.py
# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """

from typing import TYPE_CHECKING

from deepdiff import DeepDiff
from pydantic import BaseModel

if TYPE_CHECKING:
    from pydantic.typing import DictStrAny


class PropertyBaseModel(BaseModel):
    """
    Workaround for serializing properties with pydantic until
    https://github.com/samuelcolvin/pydantic/issues/935
    is solved
    """

    @classmethod
    def get_properties(cls):
        return [
            prop for prop in dir(cls)
            if isinstance(getattr(cls, prop), property) and prop not in ("__values__", "fields")
        ]

    def dict(self, *args, **kwargs) -> 'DictStrAny':
        self.__dict__.update({prop: getattr(self, prop) for prop in self.get_properties()})

        return super().dict(*args, **kwargs)

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__) or not other:
            return False
            # raise ValueError(f"Must compare objects of the same class {self.__class__}")
        difference = DeepDiff(self.dict(), other.dict())
        return not difference

    def __ne__(self, other):
        return not self.__eq__(other)
