# Table of Contents

* [aiomql.core.exceptions](#aiomql.core.exceptions)
  * [LoginError](#aiomql.core.exceptions.LoginError)
  * [VolumeError](#aiomql.core.exceptions.VolumeError)
  * [SymbolError](#aiomql.core.exceptions.SymbolError)
  * [OrderError](#aiomql.core.exceptions.OrderError)

<a id="aiomql.core.exceptions"></a>

# aiomql.core.exceptions

Exceptions for the aiomql package.

<a id="aiomql.core.exceptions.LoginError"></a>

## LoginError Objects

```python
class LoginError(Exception)
```

Raised when an error occurs when logging in.

<a id="aiomql.core.exceptions.VolumeError"></a>

## VolumeError Objects

```python
class VolumeError(Exception)
```

Raised when a volume is not valid or out of range for a symbol.

<a id="aiomql.core.exceptions.SymbolError"></a>

## SymbolError Objects

```python
class SymbolError(Exception)
```

Raised when a symbol is not provided where required or not available in the Market Watch.

<a id="aiomql.core.exceptions.OrderError"></a>

## OrderError Objects

```python
class OrderError(Exception)
```

Raised when an error occurs when working with the order class.

