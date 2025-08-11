from pathlib import Path
from typing import Any, Iterable, Sequence, TypeVar, Dict, List, Tuple, TextIO, Union, Optional

from numpy import ndarray, recarray, void
from numpy import bool_ as np_bool_
from numpy import floating as np_floating
from numpy import generic as np_generic
from numpy import integer as np_integer
from numpy import number as np_number
from pandas import DataFrame, Series

# Generic types
T = TypeVar("T")

# Scalars
Scalar = str | float | int | complex | bool | object | np_generic
Number = int | float | complex | np_number | np_bool_
Int = int | np_integer
Float = float | np_floating
IntFloat = Int | Float

# Basic sequences
MaybeTuple = T | tuple[T, ...]
MaybeList = T | list[T]
TupleList = list[T] | tuple[T, ...]
MaybeTupleList = T | list[T] | tuple[T, ...]
MaybeIterable = T | Iterable[T]
MaybeSequence = T | Sequence[T]
ListStr = list[str]

DictLike = None | dict
DictLikeSequence = MaybeSequence[DictLike]
Args = tuple[Any, ...]
ArgsLike = None | Args
Kwargs = dict[str, Any]
KwargsLike = None | Kwargs
KwargsLikeSequence = MaybeSequence[KwargsLike]
FileName = str | Path

DTypeLike = Any
PandasDTypeLike = Any
Shape = tuple[int, ...]
RelaxedShape = int | Shape
Array = ndarray
Array1d = ndarray
Array2d = ndarray
Array3d = ndarray
Record = void
RecordArray = ndarray
RecArray = recarray
MaybeArray = T | Array
SeriesFrame = Series | DataFrame
MaybeSeries = T | Series
MaybeSeriesFrame = T | Series | DataFrame
AnyArray = Array | Series | DataFrame
AnyArray1d = Array1d | Series
AnyArray2d = Array2d | DataFrame
