from typing import Optional
import polars as pl
import numpy as np

from .position_builder import position_profit
from .utils import cols


class Strategy:
    def __init__(self, call: Optional[pl.DataFrame] = pl.DataFrame(), put: Optional[pl.DataFrame] = pl.DataFrame(),
                 call_put: Optional[pl.DataFrame] = pl.DataFrame()) -> None:
        """
        :param call: polars.DataFrame with (ua:str, ua_sell_price:int, ua_buy_price:int, symbol:str, strike_price:int,
                t:int, bs:int, buy_price:int, sell_price:int) columns. Where ua: Underlying Asset, bs : Black-Scholes
                price, t: Days to expiration date
        :param put: polars.DataFrame with (ua:str, ua_sell_price:int, ua_buy_price:int, symbol:str, strike_price:int,
                t:int, bs:int, buy_price:int, sell_price:int) columns. Where ua: Underlying Asset, bs : Black-Scholes
                price, t: Days to expiration date
        :param call_put:
        """
        self.call = call if call.is_empty() else call.filter(pl.col("t") > 0)
        self.put = put if put.is_empty() else put.filter(pl.col("t") > 0)
        self.call_put = call_put

    def covered_call(self):
        """Is the purchase of a share of stock coupled with a sale of a call option on that stock.
        :return: polars.DataFrame contain (writing:int, writing_at_int, buy_ua:int, buy_ua_at:int,strike_price:int,
                 t:int, bs:int, pct_status:float, break_even:int, pct_break_even:float, max_pot_loss:int,
                 max_pot_profit:int, pct_mpp:float, pct_monthly_cp:float, current_profit:int, pct_cp:float,
                 pct_monthly_cp:float) columns.
        """
        df = self.call.filter(pl.col("buy_price") > 0)

        df = df.with_columns(
            max_pot_profit=pl.col("strike_price") - pl.col("ua_sell_price") + pl.col("buy_price"),
            max_pot_loss=pl.col("buy_price") - pl.col("ua_sell_price"),
            break_even=pl.col("ua_sell_price") - pl.col("buy_price")
        )

        df = df.with_columns(
            (
                pl.struct(["ua_sell_price", "strike_price", "buy_price"]).map_elements(
                    lambda x: position_profit.short_call(st=x["ua_sell_price"],
                                                         k=x["strike_price"],
                                                         premium=x["buy_price"]))
            ).alias("current_profit")
        )
        df = df.with_columns(
            pct_break_even=(pl.col("break_even") / pl.col("ua_sell_price") - 1) * 100,
            pct_mpp=pl.col("max_pot_profit") / pl.col("break_even") * 100,
            pct_cp=pl.col("current_profit") / pl.col("break_even") * 100
        )
        df = df.with_columns(
            pct_monthly_mpp=pl.col("pct_mpp") / pl.col("t") * 30,
            pct_monthly_cp=pl.col("pct_cp") / pl.col("t") * 30,
            pct_status=(pl.col("strike_price") / pl.col("ua_final") - 1) * 100
        )
        return df.select(cols.covered_call.rep).rename(cols.covered_call.rename)

    def married_put(self):
        df = self.call.filter(pl.col("sell_price") > 0)

        df = df.with_columns(
            max_pot_profit=pl.lit(np.inf),
            max_pot_loss=pl.col("strike_price") - pl.col("ua_sell_price") - pl.col("sell_price"),
            break_even=pl.col("ua_sell_price") - pl.col("sell_price")
        )

        df = df.with_columns(
            (
                pl.struct(["ua_sell_price", "strike_price", "sell_price"]).map_elements(
                    lambda x: position_profit.long_put(st=x["ua_sell_price"],
                                                       k=x["strike_price"],
                                                       premium=x["sell_price"]))
            ).alias("current_profit")
        )

        df = df.with_columns(
            pct_break_even=(pl.col("break_even") / pl.col("ua_sell_price") - 1) * 100,
            pct_mpp=pl.lit(np.inf),
            pct_cp=pl.col("current_profit") / pl.col("break_even") * 100
        )
        df = df.with_columns(
            pct_monthly_mpp=pl.col("pct_mpp") / pl.col("t") * 30,
            pct_monthly_cp=pl.col("pct_cp") / pl.col("t") * 30,
            pct_status=(pl.col("strike_price") / pl.col("ua_final") - 1) * 100
        )

        return df.select(cols.married_put.rep).rename(cols.married_put.rename)
