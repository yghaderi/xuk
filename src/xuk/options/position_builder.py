from collections import namedtuple
from typing import List, TypedDict

PositionProfit = namedtuple("PositionProfit",
                            ["long_call", "short_call", "long_put", "short_put", "long_ua", "short_ua"])


def _long_call(st: int, k: int, premium: int, qty: int = 1) -> int:
    """ Calculate long call position profit.
    :param st: int, underlying asset price at time of t
    :param k: int, strike price
    :param premium: int, premium
    :param qty: int, quantity
    :return: int, position profit
    """
    return (max(st - k, 0) - premium) * qty


def _short_call(st: int, k: int, premium: int, qty: int = 1) -> int:
    """ Calculate short call position profit.
    :param st: int, underlying asset price at time of t
    :param k: int, strike price
    :param premium: int, premium
    :param qty: int, quantity
    :return: int, position profit
    """
    return (-max(st - k, 0) + premium) * qty


def _long_put(st: int, k: int, premium: int, qty: int = 1) -> int:
    """ Calculate long put position profit.
    :param st: int, underlying asset price at time of t
    :param k: int, strike price
    :param premium: int, premium
    :param qty: int, quantity
    :return: int, position profit
    """
    return (max(k - st, 0) - premium) * qty


def _short_put(st: int, k: int, premium: int, qty: int = 1) -> int:
    """ Calculate short call position profit.
    :param st: int, underlying asset price at time of t
    :param k: int, strike price
    :param premium: int, premium
    :param qty: int, quantity
    :return: int, position profit
    """
    return (-max(k - st, 0) + premium) * qty


def _long_ua(spot_price: int, st: int, qty: int = 1) -> int:
    """ Calculate long UA position profit.
    :param spot_price: int, asset price at time of 0
    :param st: int, asset price at time of t
    :param qty: int, quantity
    :return: int, position profit
    """
    return (st - spot_price) * qty


def _short_ua(spot_price: int, st: int, qty: int = 1) -> int:
    """ Calculate short UA position profit.
    :param spot_price: int, asset price at time of 0
    :param st: int, asset price at time of t
    :param qty: int, quantity
    :return: int, position profit
    """
    return (spot_price - st) * qty


position_profit = PositionProfit(long_call=_long_call, short_call=_short_call, long_put=_long_put, short_put=_short_put,
                                 long_ua=_long_ua, short_ua=_short_ua)

OptionParam = TypedDict("OptionParam", {"k": int, "premium": int, "qty": int})
UAParam = TypedDict("UAParam", {"splot_price": int, "qty": int})
StParam = TypedDict("StParam", {"min": int, "max": int, "step": int})


class PositionBuilder:
    def __init__(self, long_call: List[OptionParam], short_call: List[OptionParam], long_put: List[OptionParam],
                 short_put: List[OptionParam], long_ua: List[UAParam], short_ua: List[UAParam], st_range: StParam):
        """
        strike price = k
        :param long_call: List[OptionParam] long call position params e.g. [{"k":22_000, "premium":2_000, "qty":2}, ...]
        :param short_call: List[OptionParam] short call position params e.g. [{"k":22_000, "premium":2_000, "qty":2}, ...]
        :param long_put: List[OptionParam] long put position params e.g. [{"k":22_000, "premium":2_000, "qty":3}, ...]
        :param short_put: List[OptionParam] short put position params e.g. [{"k":22_000, "premium":2_000, "qty":2}, ...]
        :param long_ua: List[UAParam] long underlying asset position params e.g. [{"splot_price":18_000, "qty":1}, ...]
        :param short_ua: List[UAParam] short underlying asset position params e.g. [{"splot_price":18_000, "qty":1}, ...]
        :param st_range: StParam to create range of price of assets at maturity,
                e.g. {"min":2000, "max":5000,"step":10}

        >>>positions = {"long_call":[],
        ..."short_call":[{"k":22_000, "premium":2_000, "qty":2}, {"k":24_000, "premium":1_000, "qty":1}],
        ..."long_put":[],
        ..."short_put":[],
        ..."long_ua":[{"spot_price":20_000, "qty":3}],
        ..."short_ua":[],
        ...}
        >>>pb = PositionBuilder(**positions, st_range = {"min":15_000, "max":30_000, "step":10)})
        >>>print(pb.simulate_profit())
        [-10000, -9970, ...]
        >>>
        """
        self.lc = long_call
        self.sc = short_call
        self.lp = long_put
        self.sp = short_put
        self.lua = long_ua
        self.sua = short_ua
        self.st_range = range(st_range.get("min"), st_range.get("max"), st_range.get("step"))

    def simulate_profit(self) -> List[int]:
        """The simulation of profit for all given position within the specified range.
        :return: List[int]
        """
        sim_profit = []
        for i in self.st_range:
            profit = 0
            profit += sum([position_profit.long_call(st=i, **items) for items in self.lc])
            profit += sum([position_profit.short_call(st=i, **items) for items in self.sc])
            profit += sum([position_profit.long_put(st=i, **items) for items in self.lp])
            profit += sum([position_profit.short_put(st=i, **items) for items in self.sp])
            profit += sum([position_profit.long_ua(st=i, **items) for items in self.lua])
            profit += sum([position_profit.short_ua(st=i, **items) for items in self.sua])
            sim_profit.append(profit)
        return sim_profit
