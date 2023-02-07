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

    @abc.abstractmethod
    def remove_lazy_field(self, source_object: Any, property_field: property):
        """

        :param source_object:
        :param property_field:
        :return:
        """


class LazyObjectABC(abc.ABC):

    @abc.abstractmethod
    def set_lazy_object_fields_loader(self, lazy_object_fields_loader: LazyObjectFieldsLoaderABC):
        """

        :param lazy_object_fields_loader:
        :return:
        """

    @abc.abstractmethod
    def get_lazy_object_fields_loader(self) -> Optional[LazyObjectFieldsLoaderABC]:
        """

        :return:
        """

    def load_lazy_field(self, property_field: property):
        """

        :param property_field:
        :return:
        """
        if self.get_lazy_object_fields_loader():
            return self.get_lazy_object_fields_loader().load_lazy_field(source_object=self,
                                                                        property_field=property_field)
        return None

    def remove_lazy_field(self, property_field: property):
        """

        :param property_field:
        :return:
        """
        if self.get_lazy_object_fields_loader():
            self.get_lazy_object_fields_loader().remove_lazy_field(source_object=self,
                                                                   property_field=property_field)
