from functools import cache
import enum
from logging import getLogger

from .config import Config
from .meta_trader import MetaTrader
from .meta_backtester import MetaBackTester

logger = getLogger(__name__)


class Base:
    """A base class for all data structure classes in the aiomql package. This class provides a set of common methods
    and attributes for handling data.
    """

    exclude: set
    include: set

    def __init__(self, **kwargs):
        """
        Initialize a new instance of the Base class

        Args:
            **kwargs: Set instance attributes with keyword arguments. Only if they are annotated on the class body.
        """
        self.exclude = {"mt5", "config", "exclude", "include", "annotations", "class_vars", "dict", "_instance"}
        self.include = set()
        self.set_attributes(**kwargs)

    def __repr__(self):
        kv = [(k, v) for k, v in self.__dict__.items() if not k.startswith("_") and (type(v) in (int, float, str) or isinstance(v, enum.Enum))]
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

    def get_dict(self, exclude: set = None, include: set = None) -> dict:
        """Returns class attributes as a dict, with the ability to filter

        Keyword Args:
            exclude: A set of attributes to be excluded
            include: Specific attributes to be returned

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
        try:
            _filter = self.exclude.difference(self.include)
            return {key: value for key, value in (self.class_vars | self.__dict__).items() if key not in _filter and value is not None}
        except Exception as err:
            logger.warning(err)


class _Base(Base):
    def __init__(self, **kwargs):
        self.config = Config()
        self.mt5 = MetaTrader() if self.config.mode != "backtest" else MetaBackTester()
        super().__init__(**kwargs)
