# Table of Contents

* [aiomql.core.base](#aiomql.core.base)
  * [Base](#aiomql.core.base.Base)
    * [set\_attributes](#aiomql.core.base.Base.set_attributes)
    * [annotations](#aiomql.core.base.Base.annotations)
    * [get\_dict](#aiomql.core.base.Base.get_dict)
    * [class\_vars](#aiomql.core.base.Base.class_vars)
    * [dict](#aiomql.core.base.Base.dict)
    * [Meta](#aiomql.core.base.Base.Meta)

<a id="aiomql.core.base"></a>

# aiomql.core.base

<a id="aiomql.core.base.Base"></a>

## Base Objects

```python
class Base()
```
A base class for all data model classes in the aiomql package.
This class provides a set of common methods and attributes for all data model classes.
For the data model classes attributes are annotated on the class body and are set as object attributes when the
class is instantiated.

**Arguments**:

- `**kwargs` - Object attributes and values as keyword arguments. Only added if they are annotated on the class body.
  
  Class Attributes:
- `mt5` _MetaTrader_ - An instance of the MetaTrader class
- `config` _Config_ - An instance of the Config class
- `Meta` _Type[Meta]_ - The Meta class for configuration of the data model class

<a id="aiomql.core.base.Base.set_attributes"></a>

#### set\_attributes

```python
def set_attributes(**kwargs)
```

Set keyword arguments as object attributes

**Arguments**:

- `**kwargs` - Object attributes and values as keyword arguments
  

**Raises**:

- `AttributeError` - When assigning an attribute that does not belong to the class or any parent class
  

**Notes**:

  Only sets attributes that have been annotated on the class body.

<a id="aiomql.core.base.Base.annotations"></a>

#### annotations

```python
@property
@cache
def annotations() -> dict
```

Class annotations from all ancestor classes and the current class.

**Returns**:

- `dict` - A dictionary of class annotations

<a id="aiomql.core.base.Base.get_dict"></a>

#### get\_dict

```python
def get_dict(exclude: set = None, include: set = None) -> dict
```

Returns class attributes as a dict, with the ability to filter

**Arguments**:

- `exclude` - A set of attributes to be excluded
- `include` - Specific attributes to be returned
  

**Returns**:

- `dict` - A dictionary of specified class attributes
  

**Notes**:

  You can only set either of include or exclude. If you set both, include will take precedence

<a id="aiomql.core.base.Base.class_vars"></a>

#### class\_vars

```python
@property
@cache
def class_vars()
```

Annotated class attributes

**Returns**:

- `dict` - A dictionary of available class attributes in all ancestor classes and the current class.

<a id="aiomql.core.base.Base.dict"></a>

#### dict

```python
@property
def dict() -> dict
```

All instance and class attributes as a dictionary, except those excluded in the Meta class.

**Returns**:

- `dict` - A dictionary of instance and class attributes

<a id="aiomql.core.base.Base.Meta"></a>

## Meta Objects

```python
class Meta()
```

A class for defining class attributes to be excluded or included in the dict property

**Attributes**:

- `exclude` _set_ - A set of attributes to be excluded
- `include` _set_ - Specific attributes to be returned. Include supercedes exclude.

<a id="aiomql.core.base.Base.Meta.filter"></a>

#### filter

```python
@classmethod
@property
def filter(cls) -> set
```

Combine the exclude and include attributes to return a set of attributes to be excluded.

**Returns**:

- `set` - A set of attributes to be excluded

