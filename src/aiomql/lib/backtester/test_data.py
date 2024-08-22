from typing import Literal, TypedDict
from ...core.models import AccountInfo, SymbolInfo, Tick
from ...core.constants import TimeFrame
from ...core.meta_trader import MetaTrader
from .get_data import Data, GetData


class TestData:

    def __init__(self, data: Data):
        self.data = data
        self.cursor = 0

    def __getitem__(self, item: tuple[Literal['ticks', 'rates'], SymbolInfo, TimeFrame]):
        type_, symbol, time_frame = item
        if type_ == 'ticks':
            return self._data[type_][symbol.name]
        return self._data[type_][symbol.name][time_frame.name]



# res = pd.DataFrame(res)
# res.drop_duplicates(subset=['time'], keep='last', inplace=True)
# res.set_index('time', inplace=True, drop=False)
