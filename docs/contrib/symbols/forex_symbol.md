# ForexSymbol

## Table of Contents
- [ForexSymbol](#forex_symbol.forex_symbol)
- [pip](#forex_symbol.pip)
- [compute_points](#forex_symbol.compute_points)
- [compute_volume_points](#forex_symbol.compute_volume_points)
- [compute_volume_sl](#forex_symbol.compute_volume_sl)


<a id="forex_symbol.forex_symbol"></a>
### ForexSymbol
```python
class ForexSymbol(Symbol)
```
Subclass of Symbol for Forex Symbols. Handles the computation of stop loss, take profit and volume.

<a id="forex_symbol.pip"></a>
### pip
```python
@property
def pip()
```
Returns the pip value of the symbol. This is ten times the point value for forex symbols.

#### Returns:
|Type|Description|
|----|-----------|
|float|The pip value of the symbol.|

<a id="forex_symbol.compute_points"></a>
### compute_points
```python
def compute_points(*, amount: float, volume: float) -> float
```
Compute the number of points required for a trade. Given the amount and the volume of the trade.

#### Parameters:
|Name|Type|Description|
|----|----|-----------|
|amount|float|Amount to trade|
|volume|float|Volume to trade|

#### Returns:
|Type|Description|
|----|-----------|
|float|The number of points required for the trade.|

<a id="forex_symbol.compute_volume_points"></a>
### compute_volume_points
```python
async def compute_volume_points(*,
                                amount: float,
                                points: float,
                                round_down: bool = False) -> float
```
Compute the volume required for a trade. Given the amount and the number of points.

#### Parameters:
|Name|Type|Description|
|----|----|-----------|
|amount|float|Amount to trade|
|points|float|Number of points|
|round_down|bool|round down the computed volume to the nearest step default True|

#### Returns:
|Type|Description|
|----|-----------|
|float|The volume required for the trade.


<a id="forex_symbol.compute_volume_sl"></a>
### compute_volume_sl
```python
async def compute_volume_sl(*, amount: float, price: float, sl: float, round_down: bool = False) -> float
```
Compute the volume required for a trade. Given the amount, the price and the stop loss.

#### Parameters:
|Name|Type|Description|
|----|----|-----------|
|amount|float|Amount to trade|
|price|float|Price of the trade|
|sl|float|Stop loss|
|round_down|bool|round down the computed volume to the nearest step default True|

#### Returns:
|Type|Description|
|----|-----------|
|float|The volume required for the trade.