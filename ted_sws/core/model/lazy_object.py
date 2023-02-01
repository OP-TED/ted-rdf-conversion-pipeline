import abc
from typing import Optional, Any


class LazyObjectFieldsLoaderABC(abc.ABC):

    @abc.abstractmethod
    def load_lazy_field(self, source_object: Any, property_field: property) -> Any:
        """

        :param source_object:
        :param property_field:
        :return:
        """


class LazyObject:
    _lazy_object_fields_loader: LazyObjectFieldsLoaderABC = None

    def set_lazy_object_fields_loader(self, lazy_object_fields_loader: LazyObjectFieldsLoaderABC):
        """

        :param lazy_object_fields_loader:
        :return:
        """
        self._lazy_object_fields_loader = lazy_object_fields_loader

    def get_lazy_object_fields_loader(self) -> Optional[LazyObjectFieldsLoaderABC]:
        """

        :return:
        """
        return self._lazy_object_fields_loader

    def load_lazy_field(self, property_field: property):
        """

        :param property_field:
        :return:
        """
        if self._lazy_object_fields_loader:
            return self._lazy_object_fields_loader.load_lazy_field(source_object=self, property_field=property_field)
        return None
