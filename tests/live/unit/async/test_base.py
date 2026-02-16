"""Comprehensive tests for the Base and _Base classes.

Tests cover:
- Base class initialization and attribute handling
- Dictionary conversion with include/exclude filtering
- Annotations and class variables
- _Base class MetaTrader and Config integration
- Pickling/serialization support
- Mode switching (async/sync)
"""

import enum
import pytest
from aiomql.core.base import Base, _Base
from aiomql.core.config import Config
from aiomql.core.meta_trader import MetaTrader


class ChildClass(Base):
    attr: int
    attr2: str
    cls_attr: int = 10


class ChildBaseClass(_Base):
    """Test subclass of _Base for testing MT5/Config integration."""
    attr: int
    attr2: str
    cls_attr: int = 20


class TestEnum(enum.Enum):
    """Test enum for repr testing."""
    VALUE_A = 1
    VALUE_B = 2


class EnumChild(Base):
    """Test class with enum attribute."""
    name: str
    status: TestEnum


class TestBaseClass:
    """Tests for the Base class."""

    @pytest.fixture
    def child(self):
        return ChildClass(attr=1, attr2="test")

    def test_repr(self, child):
        repr_str = repr(child)
        assert repr_str.startswith("ChildClass(")
        assert "attr=1" in repr_str
        assert "attr2=test" in repr_str

    def test_repr_with_enum(self):
        """Test repr correctly displays enum values."""
        obj = EnumChild(name="test", status=TestEnum.VALUE_A)
        repr_str = repr(obj)
        assert "name=test" in repr_str
        assert "VALUE_A" in repr_str

    def test_repr_truncates_long_attributes(self):
        """Test repr truncates when there are more than 3 attributes."""
        class ManyAttrs(Base):
            a: int
            b: int
            c: int
            d: int
            e: int

        obj = ManyAttrs(a=1, b=2, c=3, d=4, e=5)
        repr_str = repr(obj)
        assert "..." in repr_str
        assert "a=1" in repr_str
        assert "e=5" in repr_str

    def test_set_attributes(self, child):
        child.set_attributes(attr3=3.14, attr2="str")
        assert child.attr2 == "str"
        assert getattr(child, "attr3", None) is None

    def test_set_attributes_type_conversion(self):
        """Test set_attributes converts types based on annotations."""
        child = ChildClass(attr="42", attr2=123)
        assert child.attr == 42
        assert child.attr2 == "123"

    def test_annotations(self, child):
        annotations = child.annotations
        assert isinstance(annotations, dict)
        assert "attr" in annotations
        assert "attr2" in annotations

    def test_annotations_includes_parent_classes(self):
        """Test annotations includes attributes from parent classes."""
        class GrandChild(ChildClass):
            extra: float

        grandchild = GrandChild(attr=1, attr2="test", extra=3.14)
        annotations = grandchild.annotations
        assert "attr" in annotations
        assert "attr2" in annotations
        assert "extra" in annotations

    def test_get_dict(self, child):
        child.set_attributes(attr2="test")
        result = child.get_dict()
        assert result["attr"] == 1
        assert result["attr2"] == "test"

    def test_get_dict_with_exclude(self, child):
        child.set_attributes(attr2="test")
        result = child.get_dict(exclude={"attr"})
        assert "attr" not in result
        assert result["attr2"] == "test"

    def test_get_dict_with_include(self, child):
        child.set_attributes(attr3=3.14)
        result = child.get_dict(include={"attr"})
        assert result["attr"] == 1
        assert "attr2" not in result

    def test_get_dict_include_takes_precedence(self, child):
        """Test that include takes precedence over exclude."""
        result = child.get_dict(include={"attr"}, exclude={"attr"})
        assert "attr" in result

    def test_class_vars(self, child):
        class_vars = child.class_vars
        assert isinstance(class_vars, dict)
        assert "cls_attr" in class_vars
        assert "attr" not in class_vars

    def test_dict_property(self, child):
        child.set_attributes(attr2="test")
        dict_prop = child.dict
        assert dict_prop["attr"] == 1
        assert dict_prop["attr2"] == "test"
        assert dict_prop["cls_attr"] == 10

    def test_dict_excludes_none_values(self):
        """Test dict property excludes None values."""
        class OptionalAttr(Base):
            required: int
            optional: str = None

        obj = OptionalAttr(required=1)
        assert "optional" not in obj.dict

    def test_dict_excludes_internal_attributes(self, child):
        """Test dict excludes internal attributes like mt5, config."""
        dict_prop = child.dict
        assert "mt5" not in dict_prop
        assert "config" not in dict_prop
        assert "exclude" not in dict_prop
        assert "include" not in dict_prop


class TestUnderscoreBaseClass:
    """Tests for the _Base class with MT5/Config integration."""

    @pytest.fixture
    def base_child(self):
        return ChildBaseClass(attr=1, attr2="test")

    def test_has_mt5_attribute(self, base_child):
        """Test _Base provides mt5 attribute."""
        assert hasattr(base_child, "mt5")

    def test_has_config_attribute(self, base_child):
        """Test _Base provides config attribute."""
        assert hasattr(base_child, "config")
        assert isinstance(base_child.config, Config)

    def test_mt5_is_metatrader_instance(self, base_child):
        """Test mt5 is a MetaTrader instance in async mode."""
        # Default mode is async
        assert isinstance(base_child.mt5, MetaTrader)

    def test_config_is_shared(self):
        """Test config is shared across instances."""
        child1 = ChildBaseClass(attr=1, attr2="test1")
        child2 = ChildBaseClass(attr=2, attr2="test2")
        assert child1.config is child2.config

    def test_mt5_is_shared(self):
        """Test mt5 is shared across instances."""
        child1 = ChildBaseClass(attr=1, attr2="test1")
        child2 = ChildBaseClass(attr=2, attr2="test2")
        assert child1.mt5 is child2.mt5

    def test_getstate_excludes_mt5(self, base_child):
        """Test __getstate__ excludes mt5 for pickling."""
        state = base_child.__getstate__()
        assert "mt5" not in state

    def test_getstate_preserves_other_attributes(self, base_child):
        """Test __getstate__ preserves other instance attributes."""
        state = base_child.__getstate__()
        assert state["attr"] == 1
        assert state["attr2"] == "test"

    def test_inherits_from_base(self, base_child):
        """Test _Base inherits from Base."""
        assert isinstance(base_child, Base)

    def test_dict_property_works(self, base_child):
        """Test dict property works correctly."""
        dict_prop = base_child.dict
        assert dict_prop["attr"] == 1
        assert dict_prop["attr2"] == "test"
        assert dict_prop["cls_attr"] == 20

    def test_mode_attribute(self, base_child):
        """Test default mode is async."""
        assert base_child.mode == "async"

    def test_class_setup_called_on_new(self):
        """Test _setup is called during instance creation."""
        child = ChildBaseClass(attr=1, attr2="test")
        # If _setup was called, mt5 and config should be set
        assert hasattr(ChildBaseClass, "mt5")
        assert hasattr(ChildBaseClass, "config")
