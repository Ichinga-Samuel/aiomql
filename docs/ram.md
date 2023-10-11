<a id="aiomql.ram"></a>

# aiomql.ram

Risk Assessment and Management

<a id="aiomql.ram.RAM"></a>

## RAM Objects

```python
class RAM()
```

<a id="aiomql.ram.RAM.__init__"></a>

#### \_\_init\_\_

```python
def __init__(**kwargs)
```

Risk Assessment and Management. All provided keyword arguments are set as attributes.

**Arguments**:

- `kwargs` _Dict_ - Keyword arguments.
  
  Defaults:
- `risk_to_reward` _float_ - Risk to reward ratio 1
- `risk` _float_ - Percentage of account balance to risk per trade 0.01 # 1%
- `amount` _float_ - Amount to risk per trade in terms of account currency 0
- `pips` _float_ - Target pips 0
- `volume` _float_ - Volume to trade 0

<a id="aiomql.ram.RAM.get_amount"></a>

#### get\_amount

```python
async def get_amount(risk: float = 0) -> float
```

Calculate the amount to risk per trade as a percentage of free margin.

**Arguments**:

- `risk` _float_ - Percentage of account balance to risk per trade. Defaults to zero.
  

**Returns**:

- `float` - Amount to risk per trade

<a id="aiomql.ram.RAM.get_volume"></a>

#### get\_volume

```python
async def get_volume(*,
                     symbol: Symbol,
                     pips: float = 0,
                     amount: float = 0) -> float
```

Calculate the volume to trade. if pips is not provided, the pips attribute is used.
If the amount attribute or amount argument is zero, the amount is calculated using the get_amount method based on the risk.

**Arguments**:

- `symbol` _Symbol_ - Financial instrument
  

**Arguments**:

- `pips` _float_ - Target pips. Defaults to zero.
- `amount` _float_ - Amount to risk per trade. Defaults to zero.
  

**Returns**:

- `float` - Volume to trade

