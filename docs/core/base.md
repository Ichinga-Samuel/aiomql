# Base

## Table of Contents
- [Base](#base.base)
  - [set_attributes](#base.set_attributes)
  - [annotations](#base.annotations)
  - [get_dict](#base.get_dict)
  - [class_vars](#base.class_vars)
  - [dict](#base.dict)

- [_Base](#_base._base)


<a id="base.base"></a>    
### Base
```python
class Base
```
A base class for all data model classes in the aiomql package. This class provides a set of common methods
and attributes for all data model classes.

#### Attributes:
| Name      | Type  | Description                                                                                          |
|-----------|-------|------------------------------------------------------------------------------------------------------|
| `exclude` | `set` | A set of attributes to be excluded when retrieving attributes using the *get_dict* and *dict* method |
| `include` | `set` | A set of attributes to be included when retrieving attributes using the *get_dict* and *dict* method |


<a id="base.__init__"></a>
### __init__
```python
def __init__(**kwargs)
```
#### Parameters:
| Name     | Type  | Description                                       |
|----------|-------|---------------------------------------------------|
| `kwargs` | `Any` | Object attributes and values as keyword arguments |


<a id="base.set_attributes"></a>
### set_attributes
```python
def set_attributes(**kwargs)
```
Set keyword arguments as object attributes. Only sets attributes that have been annotated on the class body.

#### Parameters:
| Name     | Type  | Description                                       |
|----------|-------|---------------------------------------------------|
| `kwargs` | `Any` | Object attributes and values as keyword arguments |

#### Raises:
| Exception        | Description                                                                       |
|------------------|-----------------------------------------------------------------------------------|
| `AttributeError` | When assigning an attribute that does not belong to the class or any parent class |

#### Notes:
Only sets attributes that have been annotated on the class body.


<a id="base.annotations"></a>
### annotations
```python
@property
@cache
def annotations() -> dict
```
Class annotations from all ancestor classes and the current class.
#### Returns:
| Type             | Description                       |
|------------------|-----------------------------------|
| `dict[str, Any]` | A dictionary of class annotations |


<a id="base.get_dict"></a>
#### get_dict
```python
def get_dict(exclude: set = None, include: set = None) -> dict
```
Returns class attributes as a dict, with the ability to filter

#### Parameters:
| Name      | Type  | Description                        |
|-----------|-------|------------------------------------|
| `exclude` | `set` | A set of attributes to be excluded |
| `include` | `set` | Specific attributes to be returned |

#### Returns:
| Type   | Description                                |
|--------|--------------------------------------------|
| `dict` | A dictionary of specified class attributes |

#### Notes:
You can only set either of include or exclude. If you set both, include will take precedence


<a id="base.class_vars"></a>
### class_vars
```python
@property
@cache
def class_vars()
```
Annotated class attributes

#### Returns:
| Type   | Description                                                                               |
|--------|-------------------------------------------------------------------------------------------|
| `dict` | A dictionary of available class attributes in all ancestor classes and the current class. |


<a id="base.dict"></a>
### dict
```python
@property
def dict() -> dict
```
All instance and class attributes as a dictionary, except those excluded in the Meta class.

#### Returns:
| Type   | Description                                   |
|--------|-----------------------------------------------|
| `dict` | A dictionary of instance and class attributes |


<a id="_base._base></a>
### _Base(Base)
Base class that provides access to the MetaTrader and Config classes as well as the MetaBackTester class for 
backtesting mode.

#### Attributes:
| Name     | Type         | Description                         | Default |
|----------|--------------|-------------------------------------|---------|
| `mt5`    | `MetaTrader` | An instance of the MetaTrader class |         |
| `config` | `Config`     | An instance of the Config class     |         |
