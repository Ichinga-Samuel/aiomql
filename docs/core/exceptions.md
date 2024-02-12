# Exceptions
Exceptions for the aiomql package.

## Table of Contents
- [LoginError](#exceptions.LoginError)
- [VolumeError](#exceptions.VolumeError)
- [SymbolError](#exceptions.SymbolError)
- [OrderError](#exceptions.OrderError)

    
<a id="exceptions.LoginError"></a>
### LoginError
```python
class LoginError(Exception)
```
Raised when an error occurs when logging in.

<a id="exceptions.VolumeError"></a>
### VolumeError
```python
class VolumeError(Exception)
```
Raised when a volume is not valid or out of range for a symbol.

<a id="exceptions.SymbolError"></a>
### SymbolError
```python
class SymbolError(Exception)
```
Raised when a symbol is not provided where required or not available in the Market Watch.

<a id="exceptions.OrderError"></a>
### OrderError
```python
class OrderError(Exception)
```
Raised when an error occurs when working with the order class.