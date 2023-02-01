import abc
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from deepdiff import DeepDiff
from pydantic import BaseModel, Field, PositiveInt

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


class WorkExpression(PropertyBaseModel, abc.ABC):
    """
        A Merger of Work and Expression FRBR classes.

        :param created_at
            creation timestamp
        :param version_number
            Compares the current version of the object with a known version.
            This is a simple solution in the case of parallel processes which
            are updating the same object in concomitant transactions.

            Version increase can be done only by the transaction maager.
            See: https://www.cosmicpython.com/book/chapter_11_external_events.html
    """

    class Config:
        underscore_attrs_are_private = True
        validate_assignment = True
        orm_mode = True
        allow_population_by_field_name = True

    created_at: str = datetime.now().replace(microsecond=0).isoformat()
    version_number: int = 0

    # @property
    # def status(self):
    #     return self._status

    # @abc.abstractmethod
    # def update_status_to(self, new_status):
    #     """
    #         This solution of non-standard setters on controlled fields is adopted until
    #         the https://github.com/samuelcolvin/pydantic/issues/935 is solved.
    #
    #         Meanwhile we can adopt a transition logic (which is not the same as validation logic).
    #     :param new_status:
    #     :return:
    #     """


class BigString(str):
    gridfs_id: str = None


class LazyWorkExpression(WorkExpression):

    _test_field :str = None

class NoticeModel(LazyWorkExpression):
    """

    """

    _x: Optional[int] = 10

    object_data : BigString = None

    def __init__(self, *args, **kvargs):
        super().__init__(**kvargs)

    @property
    def x(self):
        print("HELLO")
        return 4

    @property
    def y(self):
        print("HEY")
        return 5

    def set_x(self, value):
        self._x = value

def print_property_name(property_field: property):
    print(property_field.fget.__name__)


def test_new_notice_model():
    notice  = NoticeModel(x=10)
    notice._test_field = "ha"
    print(notice)

