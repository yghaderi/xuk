from typing import Optional
import polars as pl

from itertools import combinations
from operator import add


class Strategy:
    def __init__(self, call: Optional[pl.DataFrame] = None, put: Optional[pl.DataFrame] = None,
                 call_put: Optional[pl.DataFrame] = None) -> None:
        """

        :param call: polars.DataFrame with (ua:str, ua_sell_price:int, ua_buy_price:int, symbol:str, strike_price:int,
                t:int, bs:int, buy_price:int, sell_price:int) columns. Where ua: Underlying Asset, bs : Black-Scholes
                price, t: Days to expiration date
        :param put: polars.DataFrame with (ua:str, ua_sell_price:int, ua_buy_price:int, symbol:str, strike_price:int,
                t:int, bs:int, buy_price:int, sell_price:int) columns. Where ua: Underlying Asset, bs : Black-Scholes
                price, t: Days to expiration date
        :param call_put:
        """
        self.call = call
        self.put = put
        self.call_put = call_put

    def covered_call(self):
        """Is the purchase of a share of stock coupled with a sale of a call option on that stock.
        :return: polars.DataFrame contain (writing:int, writing_at_int, buy_ua:int, buy_ua_at:int,strike_price:int,
                 t:int, bs:int, pct_status:float, break_even:int, pct_break_even:float, max_pot_loss:int,
                 max_pot_profit:int, pct_mpp:float, pct_monthly_cp:float, current_profit:int, pct_cp:float,
                 pct_monthly_cp:float) columns.
        """
        df = self.call[(self.call.buy_price > 0) & (self.call.t > 0)].copy()

        df = df.assign(max_pot_profit=df.strike_price - df.ua_sell_price + df.buy_price,
                       max_pot_loss=df.buy_price - df.ua_sell_price,
                       break_even=df.ua_sell_price - df.buy_price,
                       )
        df["current_profit"] = df.apply(
            lambda x: self.short_call(st=x["ua_sell_price"], k=x["strike_price"], premium=x["buy_price"]), axis=1)
        df = df.assign(pct_break_even=(df.break_even / df.ua_sell_price - 1) * 100,
                       pct_mpp=df.max_pot_profit / df.break_even * 100,
                       pct_cp=df.current_profit / df.break_even * 100).round(1)
        df = df.assign(pct_monthly_mpp=df.pct_mpp / df.t * 30,
                       pct_monthly_cp=df.pct_cp / df.t * 30,
                       pct_status=(df.strike_price / df.ua_final - 1) * 100).round(1)
        return df[df.columns.intersection(set(covered_call_["rep"]))].rename(columns=covered_call_["dict"])
