"""Comprehensive tests for the base module.

Tests cover:
- Base class initialization, set_attributes, repr, annotations, dict, get_dict, class_vars
- BaseMeta metaclass lazy setup behavior
- _Base class with MetaTrader/Config integration and pickling support
- Subclassing and annotation/exclude/include merging
"""

import enum
import pickle
from unittest.mock import patch, MagicMock

import pytest

from aiomql.core.base import Base, _Base, BaseMeta
from aiomql.core.config import Config
from aiomql.core.meta_trader import MetaTrader
from aiomql.core.sync.meta_trader import MetaTrader as MetaTraderSync


# ---------------------------------------------------------------------------
# Helper subclasses for testing
# ---------------------------------------------------------------------------

class SimpleModel(Base):
    """A simple Base subclass with typed annotations."""
    name: str
    value: int
    score: float


class ExtendedModel(SimpleModel):
    """A child of SimpleModel adding more annotations."""
    extra: str
    value: float  # override parent's int annotation with float


class CustomExcludeModel(Base):
    """A model with a custom exclude set."""
    exclude: set[str] = {"mt5", "config", "exclude", "include", "annotations", "class_vars", "dict", "_instance",
                         "mode", "secret"}
    name: str
    secret: str
    visible: int


class CustomIncludeModel(Base):
    """A model with a custom include set that overrides exclude."""
    include: set[str] = {"config"}
    name: str
    config: str


class ModelWithClassVar(Base):
    """A model with annotated class-level defaults."""
    name: str
    kind: str = "default_kind"


class EnumColor(enum.Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


class ModelWithEnum(Base):
    """A model containing an enum attribute."""
    name: str
    color: EnumColor
    score: float


class ManyAttrsModel(Base):
    """A model with > 3 simple-typed attributes."""
    a: int
    b: int
    c: int
    d: int
    e: int


class ModelWithComplexAttr(Base):
    """A model with complex (non-simple) attributes."""
    name: str
    data: list
    meta: dict


class SyncBaseModel(_Base):
    """A _Base subclass operating in sync mode."""
    mode = "sync"
    name: str


class AsyncBaseModel(_Base):
    """A _Base subclass operating in async (default) mode."""
    name: str


# ===========================================================================
# TestBaseInit
# ===========================================================================


class TestBaseInit:
    """Tests for Base.__init__ and set_attributes."""

    def test_init_sets_annotated_attributes(self):
        """Init with valid annotated kwargs sets attributes."""
        obj = SimpleModel(name="hello", value=42, score=3.14)
        assert obj.name == "hello"
        assert obj.value == 42
        assert obj.score == 3.14

    def test_init_ignores_non_annotated_kwargs(self):
        """Non-annotated kwargs are silently ignored."""
        obj = SimpleModel(name="hello", value=1, score=0.0, unknown="ignored")
        assert not hasattr(obj, "unknown")

    def test_init_coerces_types(self):
        """Annotation callables are used to coerce values."""
        obj = SimpleModel(name="hello", value="99", score="2.5")
        assert obj.value == 99
        assert isinstance(obj.value, int)
        assert obj.score == 2.5
        assert isinstance(obj.score, float)

    def test_init_fallback_on_conversion_error(self):
        """When coercion raises ValueError/TypeError, raw value is kept."""
        obj = SimpleModel(name="hello", value="not_a_number", score=1.0)
        # value should be set as the raw string since int("not_a_number") raises ValueError
        assert obj.value == "not_a_number"

    def test_init_no_args(self):
        """Init with no args creates an instance with no instance attributes."""
        obj = SimpleModel()
        assert isinstance(obj, SimpleModel)
        # No instance attributes should be set
        assert "name" not in obj.__dict__
        assert "value" not in obj.__dict__

    def test_set_attributes_updates_existing(self):
        """set_attributes can update existing attributes."""
        obj = SimpleModel(name="original", value=1, score=0.0)
        obj.set_attributes(name="updated", value=100)
        assert obj.name == "updated"
        assert obj.value == 100

    def test_set_attributes_ignores_unannotated(self):
        """set_attributes ignores keys not in annotations."""
        obj = SimpleModel(name="test", value=1, score=0.0)
        obj.set_attributes(phantom="ghost")
        assert not hasattr(obj, "phantom")


# ===========================================================================
# TestBaseRepr
# ===========================================================================


class TestBaseRepr:
    """Tests for Base.__repr__."""

    def test_repr_with_few_attrs(self):
        """Repr with ≤3 simple-type attrs shows all."""
        obj = SimpleModel(name="test", value=42, score=1.5)
        r = repr(obj)
        assert r.startswith("SimpleModel(")
        assert "name=test" in r
        assert "value=42" in r
        assert "score=1.5" in r

    def test_repr_with_many_attrs_truncates(self):
        """Repr with > 3 attrs shows first 3 + ... + last 1."""
        obj = ManyAttrsModel(a=1, b=2, c=3, d=4, e=5)
        r = repr(obj)
        assert "..." in r
        assert "a=1" in r
        assert "e=5" in r

    def test_repr_excludes_private_attrs(self):
        """Repr excludes attributes starting with _."""
        obj = SimpleModel(name="test", value=1, score=0.0)
        obj._private = "hidden"
        r = repr(obj)
        assert "_private" not in r

    def test_repr_excludes_complex_types(self):
        """Repr excludes list and dict attrs."""
        obj = ModelWithComplexAttr(name="test", data=[1, 2, 3], meta={"k": "v"})
        r = repr(obj)
        assert "data=" not in r
        assert "meta=" not in r
        assert "name=test" in r

    def test_repr_includes_enum_values(self):
        """Repr includes enum attributes."""
        obj = ModelWithEnum(name="test", color=EnumColor.RED, score=1.0)
        r = repr(obj)
        assert "color=" in r

    def test_repr_empty_instance(self):
        """Repr of instance with no attributes."""
        obj = SimpleModel()
        r = repr(obj)
        assert r == "SimpleModel()"


# ===========================================================================
# TestBaseAnnotations
# ===========================================================================


class TestBaseAnnotations:
    """Tests for the annotations property."""

    def test_annotations_returns_own_annotations(self):
        """annotations includes annotations from the class itself."""
        obj = SimpleModel(name="x", value=1, score=0.0)
        annots = obj.annotations
        assert "name" in annots
        assert "value" in annots
        assert "score" in annots

    def test_annotations_merges_parent(self):
        """annotations includes parent class annotations."""
        obj = ExtendedModel(name="x", value=1, score=0.0, extra="e")
        annots = obj.annotations
        assert "name" in annots  # from SimpleModel
        assert "score" in annots  # from SimpleModel
        assert "extra" in annots  # from ExtendedModel

    def test_annotations_child_overrides_parent(self):
        """Child annotations override parent annotations."""
        obj = ExtendedModel(name="x", value=1, score=0.0, extra="e")
        annots = obj.annotations
        # ExtendedModel annotates value as float, overriding SimpleModel's int
        assert annots["value"] is float

    def test_annotations_returns_dict(self):
        """annotations property returns a dict."""
        obj = SimpleModel(name="x", value=1, score=0.0)
        assert isinstance(obj.annotations, dict)


# ===========================================================================
# TestBaseClassVars
# ===========================================================================


class TestBaseClassVars:
    """Tests for the class_vars property."""

    def test_class_vars_includes_annotated_defaults(self):
        """class_vars includes annotated class-level variables with defaults."""
        obj = ModelWithClassVar(name="test")
        cv = obj.class_vars
        assert "kind" in cv
        assert cv["kind"] == "default_kind"

    def test_class_vars_excludes_non_annotated(self):
        """class_vars excludes class variables that are not annotated."""
        obj = SimpleModel(name="x", value=1, score=0.0)
        cv = obj.class_vars
        # 'exclude' and 'include' are defined on Base but not annotated on SimpleModel
        # However they ARE annotated on Base itself, so they will appear in class_vars
        # The key point is that non-annotated attrs are excluded
        for key in cv:
            assert key in obj.annotations


# ===========================================================================
# TestBaseDict
# ===========================================================================


class TestBaseDict:
    """Tests for the dict property."""

    def test_dict_returns_instance_and_class_attrs(self):
        """dict combines instance attributes and class_vars."""
        obj = ModelWithClassVar(name="test")
        d = obj.dict
        assert "name" in d
        assert d["name"] == "test"
        assert "kind" in d
        assert d["kind"] == "default_kind"

    def test_dict_excludes_default_excluded_keys(self):
        """dict excludes keys in the exclude set."""
        obj = SimpleModel(name="test", value=1, score=0.0)
        d = obj.dict
        assert "mt5" not in d
        assert "config" not in d
        assert "exclude" not in d
        assert "include" not in d
        assert "annotations" not in d
        assert "class_vars" not in d

    def test_dict_excludes_none_values(self):
        """dict excludes attributes with None values."""
        obj = SimpleModel(name="test", value=1, score=0.0)
        obj.name = None  # Manually set to None
        d = obj.dict
        assert "name" not in d

    def test_dict_include_overrides_exclude(self):
        """include set can override exclude behavior."""
        obj = CustomIncludeModel(name="test", config="my_config")
        d = obj.dict
        # 'config' is normally excluded, but CustomIncludeModel includes it
        assert "config" in d

    def test_dict_custom_exclude(self):
        """Custom exclude set hides specific attrs."""
        obj = CustomExcludeModel(name="visible_name", secret="hidden", visible=42)
        d = obj.dict
        assert "name" in d
        assert "visible" in d
        assert "secret" not in d


# ===========================================================================
# TestBaseGetDict
# ===========================================================================


class TestBaseGetDict:
    """Tests for the get_dict method."""

    def test_get_dict_no_args(self):
        """get_dict with no args returns all non-None dict items."""
        obj = SimpleModel(name="test", value=1, score=2.5)
        d = obj.get_dict()
        assert "name" in d
        assert "value" in d
        assert "score" in d

    def test_get_dict_include(self):
        """get_dict with include filters to specific keys."""
        obj = SimpleModel(name="test", value=1, score=2.5)
        d = obj.get_dict(include={"name", "score"})
        assert "name" in d
        assert "score" in d
        assert "value" not in d

    def test_get_dict_exclude(self):
        """get_dict with exclude filters out specific keys."""
        obj = SimpleModel(name="test", value=1, score=2.5)
        d = obj.get_dict(exclude={"value"})
        assert "value" not in d
        assert "name" in d
        assert "score" in d

    def test_get_dict_include_overrides_exclude(self):
        """When both include and exclude are set, include takes precedence."""
        obj = SimpleModel(name="test", value=1, score=2.5)
        d = obj.get_dict(include={"name"}, exclude={"name"})
        assert "name" in d
        assert "value" not in d

    def test_get_dict_excludes_none_values(self):
        """get_dict always excludes None values regardless of filters."""
        obj = SimpleModel(name="test", value=1, score=2.5)
        obj.score = None
        d = obj.get_dict(include={"name", "score"})
        assert "name" in d
        assert "score" not in d


# ===========================================================================
# TestBaseMeta
# ===========================================================================


class TestBaseMeta:
    """Tests for the BaseMeta metaclass behavior."""

    def test_instantiation_triggers_setup(self):
        """Instantiating a _Base subclass triggers _setup."""
        obj = AsyncBaseModel(name="test")
        assert hasattr(AsyncBaseModel, "config")
        assert hasattr(AsyncBaseModel, "mt5")

    def test_accessing_config_on_class_triggers_setup(self):
        """Accessing 'config' on a _Base subclass class triggers _setup."""
        # Create a fresh class to test lazy setup
        class FreshModel(_Base):
            name: str

        _ = FreshModel.config
        assert isinstance(FreshModel.__dict__["config"], Config)

    def test_accessing_mt5_on_class_triggers_setup(self):
        """Accessing 'mt5' on a _Base subclass class triggers _setup."""
        class FreshModel2(_Base):
            name: str

        _ = FreshModel2.mt5
        assert isinstance(FreshModel2.__dict__["mt5"], MetaTrader)

    def test_setup_creates_config_instance(self):
        """_setup sets config as a Config instance."""
        class TestSetupConfig(_Base):
            name: str

        TestSetupConfig._setup()
        assert isinstance(TestSetupConfig.__dict__["config"], Config)

    def test_setup_creates_async_meta_trader_by_default(self):
        """_setup creates MetaTrader (async) when mode is not 'sync'."""
        class TestAsyncMT(_Base):
            name: str

        TestAsyncMT._setup()
        assert isinstance(TestAsyncMT.__dict__["mt5"], MetaTrader)

    def test_setup_creates_sync_meta_trader_for_sync_mode(self):
        """_setup creates MetaTraderSync when mode is 'sync'."""
        class TestSyncMT(_Base):
            mode = "sync"
            name: str

        TestSyncMT._setup()
        assert isinstance(TestSyncMT.__dict__["mt5"], MetaTraderSync)

    def test_setup_is_idempotent(self):
        """Calling _setup twice doesn't recreate config/mt5."""
        class IdempotentModel(_Base):
            name: str

        IdempotentModel._setup()
        config1 = IdempotentModel.__dict__["config"]
        mt5_1 = IdempotentModel.__dict__["mt5"]

        IdempotentModel._setup()
        config2 = IdempotentModel.__dict__["config"]
        mt5_2 = IdempotentModel.__dict__["mt5"]

        assert config1 is config2
        assert mt5_1 is mt5_2


# ===========================================================================
# TestBasePrivateBase
# ===========================================================================


class TestBasePrivateBase:
    """Tests for the _Base class."""

    def test_inherits_from_base(self):
        """_Base inherits from Base."""
        assert issubclass(_Base, Base)

    def test_has_base_meta_metaclass(self):
        """_Base uses BaseMeta as its metaclass."""
        assert type(_Base) is BaseMeta

    def test_default_mode_is_async(self):
        """Default mode for _Base is 'async'."""
        assert _Base.mode == "async"

    def test_getstate_removes_mt5(self):
        """__getstate__ removes mt5 from instance state."""
        obj = AsyncBaseModel(name="test")
        obj.mt5_attr = "should_stay"  # custom attr
        state = obj.__getstate__()
        assert "mt5" not in state

    def test_getstate_preserves_other_attrs(self):
        """__getstate__ keeps all attributes except mt5."""
        obj = AsyncBaseModel(name="test_name")
        state = obj.__getstate__()
        assert state.get("name") == "test_name"

    def test_config_accessible_after_instantiation(self):
        """config is accessible as a class attribute after instantiation."""
        obj = AsyncBaseModel(name="test")
        assert isinstance(obj.config, Config)

    def test_mt5_accessible_after_instantiation(self):
        """mt5 is accessible as a class attribute after instantiation."""
        obj = AsyncBaseModel(name="test")
        assert isinstance(obj.mt5, MetaTrader)

    def test_sync_mode_creates_sync_meta_trader(self):
        """Sync mode subclass gets MetaTraderSync."""
        obj = SyncBaseModel(name="sync_test")
        assert isinstance(SyncBaseModel.__dict__["mt5"], MetaTraderSync)

    def test_async_mode_creates_async_meta_trader(self):
        """Async mode subclass gets MetaTrader."""
        obj = AsyncBaseModel(name="async_test")
        assert isinstance(AsyncBaseModel.__dict__["mt5"], MetaTrader)

    def test_getstate_does_not_modify_original_dict(self):
        """__getstate__ returns a copy, not modifying __dict__."""
        obj = AsyncBaseModel(name="test")
        original_dict = obj.__dict__.copy()
        _ = obj.__getstate__()
        assert obj.__dict__ == original_dict


# ===========================================================================
# TestBaseSubclassing
# ===========================================================================


class TestBaseSubclassing:
    """Tests for subclassing Base with annotation and exclude/include merging."""

    def test_subclass_annotations_merge(self):
        """Subclass annotations include parent annotations."""
        obj = ExtendedModel(name="x", value=1.5, score=0.0, extra="e")
        annots = obj.annotations
        assert "name" in annots
        assert "score" in annots
        assert "extra" in annots

    def test_subclass_override_exclude(self):
        """Subclass can define its own exclude set."""
        obj = CustomExcludeModel(name="n", secret="s", visible=1)
        d = obj.dict
        assert "secret" not in d
        assert "name" in d

    def test_subclass_override_include(self):
        """Subclass include set overrides parent exclude."""
        obj = CustomIncludeModel(name="n", config="cfg")
        d = obj.dict
        assert "config" in d

    def test_multiple_levels_of_inheritance(self):
        """Annotations from deeply nested inheritance chain are merged."""
        class GrandChild(ExtendedModel):
            level: int

        obj = GrandChild(name="gc", value=1.0, score=2.0, extra="e", level=3)
        annots = obj.annotations
        assert "name" in annots
        assert "extra" in annots
        assert "level" in annots
        assert annots["value"] is float  # ExtendedModel override

    def test_subclass_class_vars_include_parent_defaults(self):
        """Subclass class_vars include annotated defaults from parent."""
        class ChildWithDefault(ModelWithClassVar):
            extra: str = "extra_default"

        obj = ChildWithDefault(name="test")
        cv = obj.class_vars
        assert "kind" in cv
        assert cv["kind"] == "default_kind"
        assert "extra" in cv
        assert cv["extra"] == "extra_default"

    def test_isinstance_checks(self):
        """Subclass instances pass isinstance checks for parent."""
        obj = ExtendedModel(name="x", value=1, score=0.0, extra="e")
        assert isinstance(obj, Base)
        assert isinstance(obj, SimpleModel)
        assert isinstance(obj, ExtendedModel)
