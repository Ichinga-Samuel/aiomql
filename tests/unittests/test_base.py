import pytest
from aiomql.core.base import Base


class ChildClass(Base):
    attr: int
    attr2: str
    cls_attr: int = 10


class TestBaseClass:
    @pytest.fixture
    def child(self):
        return ChildClass(attr=1, attr2="test")

    def test_repr(self, child):
        repr_str = repr(child)
        assert repr_str.startswith("ChildClass(")
        assert "attr=1" in repr_str
        assert "attr2=test" in repr_str

    def test_set_attributes(self, child):
        child.set_attributes(attr3=3.14, attr2='str')
        assert child.attr2 == 'str'
        assert getattr(child, 'attr3', None) is None

    def test_annotations(self, child):
        annotations = child.annotations
        assert isinstance(annotations, dict)

    def test_get_dict(self, child):
        child.set_attributes(attr2='test')
        result = child.get_dict()
        assert result["attr"] == 1
        assert result["attr2"] == "test"

    def test_get_dict_with_exclude(self, child):
        child.set_attributes(attr2='test')
        result = child.get_dict(exclude={"attr"})
        assert "attr" not in result
        assert result["attr2"] == "test"

    def test_get_dict_with_include(self, child):
        child.set_attributes(attr3=3.14)
        result = child.get_dict(include={"attr"})
        assert result["attr"] == 1
        assert "attr2" not in result

    def test_class_vars(self, child):
        class_vars = child.class_vars
        assert isinstance(class_vars, dict)
        assert 'cls_attr' in class_vars
        assert 'attr' not in class_vars

    def test_dict_property(self, child):
        child.set_attributes(attr2="test")
        dict_prop = child.dict
        assert dict_prop["attr"] == 1
        assert dict_prop["attr2"] == "test"
        assert dict_prop["cls_attr"] == 10
