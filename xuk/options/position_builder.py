from typing import List, TypedDict
from xuk.options.position_profit import OptionPositionProfit, AssetPositionProfit


class OptionParam(TypedDict):
    k: int
    premium: int
    qty: int


class UAParam(TypedDict):
    splot_price: int
    qty: int


class StParam(TypedDict):
    min: int
    max: int
    step: int


class PositionBuilder:
    """Build any position and get simulate profit.

    Parameters
    ----------
    long_call
        List[OptionParam] long call position params e.g. [{'k':22_000, 'premium':2_000, 'qty':2}]
    short_call
        List[OptionParam] short call position params e.g. [{'k':22_000, 'premium':2_000, 'qty':2}]
    long_put
        List[OptionParam] long put position params e.g. [{'k':22_000, 'premium':2_000, 'qty':2}]
    short_put
        List[OptionParam] short put position params e.g. [{'k':22_000, 'premium':2_000, 'qty':2}]
    long_ua
        List[UAParam] long underlying asset position params e.g. [{'splot_price':18_000, 'qty':1}]
    short_ua
        List[UAParam] short underlying asset position params e.g. [{'splot_price':18_000, 'qty':1}]
    st_range
        StParam to create range of price of assets at maturity,
            e.g. {'min':2000, 'max':5000,'step':10}
    """

    def __init__(
        self,
        long_call: List[OptionParam],
        short_call: List[OptionParam],
        long_put: List[OptionParam],
        short_put: List[OptionParam],
        long_ua: List[UAParam],
        short_ua: List[UAParam],
        st_range: StParam,
    ) -> None:
        self.lc = long_call
        self.sc = short_call
        self.lp = long_put
        self.sp = short_put
        self.lua = long_ua
        self.sua = short_ua
        self.st_range = range(
            st_range.get("min"), st_range.get("max"), st_range.get("step")
        )

    def simulate_profit(self) -> List[int]:
        """
        The simulation of profit for all given position within the specified range.

        Returns
        -------
        List[int]

        Examples
        --------
        >>> from xuk.options import PositionBuilder
        >>> positions = {
        ...    "long_call": [],
        ...    "short_call": [
        ...        {"k": 22_000, "premium": 2_000, "qty": 2},
        ...        {"k": 24_000, "premium": 1_000, "qty": 1},
        ...    ],
        ...    "long_put": [],
        ...    "short_put": [],
        ...    "long_ua": [{"spot_price": 20_000, "qty": 3}],
        ...    "short_ua": [],
        ...}
        >>> pb = PositionBuilder(**positions, st_range={"min": 15_000, "max": 30_000, "step": 10})
        >>> print(pb.simulate_profit())
          [-10000, -9970, ...]
             >>>
        """
        sim_profit = []
        for i in self.st_range:
            profit = 0
            profit += sum(
                [OptionPositionProfit(st=i, **items).long_call() for items in self.lc]
            )
            profit += sum(
                [OptionPositionProfit(st=i, **items).short_call() for items in self.sc]
            )
            profit += sum(
                [OptionPositionProfit(st=i, **items).long_put() for items in self.lp]
            )
            profit += sum(
                [OptionPositionProfit(st=i, **items).short_put() for items in self.sp]
            )
            profit += sum(
                [AssetPositionProfit(st=i, **items).long() for items in self.lua]
            )
            profit += sum(
                [AssetPositionProfit(st=i, **items).short() for items in self.sua]
            )
            sim_profit.append(profit)
        return sim_profit
