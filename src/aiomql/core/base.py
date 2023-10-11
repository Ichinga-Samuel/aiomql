from functools import cache
import reprlib
from logging import getLogger

from .config import Config
from .meta_trader import MetaTrader

logger = getLogger(__name__)


class Base:
    """A base class for all data model classes in the aiomql package.
    This class provides a set of common methods and attributes for all data model classes.
    For the data model classes attributes are annotated on the class body and are set as object attributes when the
    class is instantiated.

    Keyword Args:
        **kwargs: Object attributes and values as keyword arguments. Only added if they are annotated on the class body.

    Class Attributes:
        mt5 (MetaTrader): An instance of the MetaTrader class
        config (Config): An instance of the Config class
        Meta (Type[Meta]): The Meta class for configuration of the data model class
    """
    mt5: MetaTrader = MetaTrader()
    config = Config()

    def __init__(self, **kwargs):
        self.set_attributes(**kwargs)

    def __repr__(self):
        keys = reprlib.repr(', '.join('%s=%s' % (i, j) for i, j in self.__dict__.items()))[1:-1]
        return '%(class)s(%(args)s)' % {'class': self.__class__.__name__, 'args': keys}

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
                logger.warning(f"Attribute {i} does not belong to class {self.__class__.__name__}")
                continue

            except ValueError:
                logger.warning(f'Cannot covert object of type {type(j)} to type {self.annotations[i]}')
                continue

            except Exception as exe:
                logger.warning(f'Did not set attribute {i} on class {self.__class__.__name__} due to {exe}')
                continue

    @property
    @cache
    def annotations(self) -> dict:
        """Class annotations from all ancestor classes and the current class.

        Returns:
            dict: A dictionary of class annotations
        """
        annots = {}
        for base in self.__class__.__mro__[-3::-1]:
            annots |= getattr(base, '__annotations__', {})
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
        return {key: value for key, value in self.dict.items() if key in filter_}

    @property
    @cache
    def class_vars(self):
        """Annotated class attributes

        Returns:
            dict: A dictionary of available class attributes in all ancestor classes and the current class.
        """
        clss = self.__class__.__mro__[-3::-1]
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
            return {key: value for key, value in (self.class_vars | self.__dict__).items() if key not in self.Meta.filter}
        except Exception as err:
            logger.warning(err)

    class Meta:
        """A class for defining class attributes to be excluded or included in the dict property

        Attributes:
            exclude (set): A set of attributes to be excluded
            include (set): Specific attributes to be returned. Include supercedes exclude.
        """
        exclude = {'mt5', "Config"}
        include = set()

        @classmethod
        @property
        def filter(cls) -> set:
            """Combine the exclude and include attributes to return a set of attributes to be excluded.

            Returns:
                set: A set of attributes to be excluded
            """
            return cls.exclude.difference(cls.include)
        