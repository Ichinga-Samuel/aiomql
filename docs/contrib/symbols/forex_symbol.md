# Table of Contents

* [aiomql.contrib.symbols.forex\_symbol](#aiomql.contrib.symbols.forex_symbol)
  * [ForexSymbol](#aiomql.contrib.symbols.forex_symbol.ForexSymbol)
    * [pip](#aiomql.contrib.symbols.forex_symbol.ForexSymbol.pip)
    * [compute\_points](#aiomql.contrib.symbols.forex_symbol.ForexSymbol.compute_points)
    * [compute\_volume\_points](#aiomql.contrib.symbols.forex_symbol.ForexSymbol.compute_volume_points)

<a id="aiomql.contrib.symbols.forex_symbol"></a>

# aiomql.contrib.symbols.forex\_symbol

<a id="aiomql.contrib.symbols.forex_symbol.ForexSymbol"></a>

## ForexSymbol Objects

```python
class ForexSymbol(Symbol)
```

Subclass of Symbol for Forex Symbols. Handles the conversion of currency and the computation of stop loss,
take profit and volume.

<a id="aiomql.contrib.symbols.forex_symbol.ForexSymbol.pip"></a>

#### pip

```python
@property
def pip()
```

Returns the pip value of the symbol. This is ten times the point value for forex symbols.

**Returns**:

- `float` - The pip value of the symbol.

<a id="aiomql.contrib.symbols.forex_symbol.ForexSymbol.compute_points"></a>

#### compute\_points

```python
def compute_points(*, amount: float, volume: float) -> float
```

Compute the number of points required for a trade. Given the amount and the volume of the trade.

**Arguments**:

- `amount` _float_ - Amount to trade
- `volume` _float_ - Volume to trade

<a id="aiomql.contrib.symbols.forex_symbol.ForexSymbol.compute_volume_points"></a>

#### compute\_volume\_points

```python
async def compute_volume_points(*,
                                amount: float,
                                points: float,
                                round_down: bool = False) -> float
```

Compute the volume required for a trade. Given the amount and the number of points.

**Arguments**:

- `amount` _float_ - Amount to trade
- `points` _float_ - Number of points
- `round_down` - round down the computed volume to the nearest step default True
