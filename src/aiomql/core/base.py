"""Base classes for data structure handling in the aiomql package.

This module provides the foundational base classes that other data structure
classes inherit from. These classes provide common functionality for attribute
management, dictionary conversion, and integration with the MetaTrader terminal.

Classes:
    Base: A base class providing attribute handling and dictionary conversion.
    _Base: Extended base class with MetaTrader and Config integration.

Example:
    Creating a custom data class::

        from aiomql.core.base import Base

        class MyData(Base):
            name: str
            value: float

        data = MyData(name='example', value=42.0)
        print(data.dict)  # {'name': 'example', 'value': 42.0}
"""

import enum
from typing import Literal
from logging import getLogger
from functools import cache

from .config import Config
from .meta_trader import MetaTrader
from .sync.meta_trader import MetaTrader as MetaTraderSync

logger = getLogger(__name__)

class BaseMeta(type):
    def __getattr__(cls, item):
        if item in ("config", "mt5"):
            cls._setup()
        return super().__getattribute__(item)

    def __call__(cls, *args, **kwargs):
        inst = super().__call__(*args, **kwargs)
        inst.__class__._setup()
        return inst

    def _setup(cls):
        if 'config' not in cls.__dict__:
            cls.config = Config()
        if 'mt5' not in cls.__dict__:
            cls.mt5 = MetaTrader() if cls.__dict__.get("mode", "") != "sync" else MetaTraderSync()


class Base:
    """A base class for all data structure classes in the aiomql package.

    This class provides a set of common methods and attributes for handling
    data, including automatic attribute setting, dictionary conversion, and
    attribute filtering capabilities.

    Attributes:
        exclude (set[str]): Attributes to exclude when converting to dict.
            Defaults to internal attributes like 'mt5', 'config', etc.
        include (set[str]): Attributes to always include when converting to dict.
            Takes precedence over exclude.

    Example:
        >>> class MyClass(Base):
        ...     name: str
        ...     value: int
        >>> obj = MyClass(name='test', value=100)
        >>> obj.dict
        {'name': 'test', 'value': 100}
    """
    exclude: set[str] = {"mt5", "config", "exclude", "include", "annotations", "class_vars", "dict", "_instance", "mode"}
    include: set[str] = {}

    def __init__(self, **kwargs):
        """Initializes a new instance of the Base class.

        Args:
            **kwargs: Keyword arguments to set as instance attributes.
                Only attributes that are annotated on the class body
                will be set.
        """
        self.set_attributes(**kwargs)

    def __repr__(self):
        """Returns a string representation of the instance.

        Shows up to 3 attributes at the start and 1 at the end if there
        are more than 3 attributes. Only includes simple types (int, float,
        str) and enums.

        Returns:
            str: A formatted string representation of the instance.
        """
        kv = [
            (k, v)
            for k, v in self.__dict__.items()
            if not k.startswith("_") and (type(v) in (int, float, str) or isinstance(v, enum.Enum))
        ]
        args = ", ".join("%s=%s" % (i, j) for i, j in kv[:3])
        args = args if len(kv) <= 3 else args + " ... " + ", ".join("%s=%s" % (i, j) for i, j in kv[-1:])
        return "%(class)s(%(args)s)" % {"class": self.__class__.__name__, "args": args}

    def set_attributes(self, **kwargs):
        """Set keyword arguments as object attributes

        Keyword Args:
            **kwargs: Object attributes and values as keyword arguments

        Raises:
            AttributeError: When assigning an attribute that does not belong to the class or any parent class

        Notes:
            Only sets attributes that have been annotated on the class body.
        """
        for i, j in kwargs.items():
            try:
                setattr(self, i, self.annotations[i](j))
            except KeyError:
                logger.debug(f"Attribute {i} does not belong to class {self.__class__.__name__}")
                continue

            except (ValueError, TypeError):
                logger.debug(f"Cannot covert object of type {type(j)} to type {self.annotations[i]}")
                setattr(self, i, j)

            except Exception as exe:
                logger.debug(f"Did not set attribute {i} on class {self.__class__.__name__} due to {exe}")
                continue

    @property
    @cache
    def annotations(self) -> dict:
        """Class annotations from all ancestor classes and the current class.

        Returns:
            dict: A dictionary of class annotations
        """
        annots = {}
        for base in self.__class__.__mro__[::-1]:
            annots |= getattr(base, "__annotations__", {})
        return annots

    def get_dict(self, exclude: set[str] = None, include: set[str] = None) -> dict:
        """Returns class attributes as a dict, with the ability to filter out specific attributes

        Args:
            exclude (set[str]): A set of attributes to be excluded
            include (set[str]): Specific attributes to be returned

        Returns:
             dict: A dictionary of specified class attributes

        Notes:
            You can only set either of include or exclude. If you set both, include will take precedence
        """
        exclude, include = exclude or set(), include or set()
        filter_ = include or set(self.dict.keys()).difference(exclude)
        return {key: value for key, value in self.dict.items() if key in filter_ and value is not None}

    @property
    @cache
    def class_vars(self):
        """Annotated class attributes

        Returns:
            dict: A dictionary of available class attributes in all ancestor classes and the current class.
        """
        clss = self.__class__.__mro__[::-1]
        cls_dict = {}
        for cls in clss:
            cls_dict |= cls.__dict__
        return {key: value for key, value in cls_dict.items() if key in self.annotations}

    @property
    def dict(self) -> dict:
        """All instance and class attributes as a dictionary, except those excluded in the Meta class.

        Returns:
            dict: A dictionary of instance and class attributes
        """
        _filter = self.exclude.difference(self.include)
        return {
            key: value
            for key, value in (self.class_vars | self.__dict__).items()
            if key not in _filter and value is not None
        }


class _Base(Base, metaclass=BaseMeta):
    """Extended base class with MetaTrader and Config integration.

    Provides automatic access to the MetaTrader terminal and configuration
    settings.

    Attributes:
        mt5 (MetaTrader): The MetaTrader interface.
        config (Config): The global configuration instance.

    Note:
        The mt5 attribute is excluded from serialization via __getstate__
        to prevent issues when pickling instances.
    """
    mt5: MetaTrader | MetaTraderSync
    config: Config
    mode: Literal["async", "sync"] = "async"

    def __getstate__(self):
        """Prepares instance state for pickling.

        Removes the mt5 attribute to avoid serialization issues with
        the MetaTrader connection.

        Returns:
            dict: The instance state without the mt5 attribute.
        """
        state = self.__dict__.copy()
        state.pop("mt5", None)
        return state
