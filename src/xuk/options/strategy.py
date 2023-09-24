from typing import Optional
import polars as pl

from .position_builder import position_profit
from .utils import cols


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
        df = self.call.filter((pl.col("buy_price") > 0) & (pl.col("t") > 0))

        df = df.with_columns(
            [
                (pl.col("strike_price") - pl.col("ua_sell_price") + pl.col("buy_price")).alias("max_pot_profit"),
                (pl.col("buy_price") - pl.col("ua_sell_price")).alias("max_pot_loss"),
                (pl.col("ua_sell_price") - pl.col("buy_price")).alias("break_even")
            ]
        )
        df = df.with_columns(
            (
                pl.struct(["ua_sell_price", "strike_price", "buy_price"]).map_batches(
                    lambda x: position_profit.short_call(st=x.struct.field("ua_sell_price"),
                                                         k=x.struct.field("strike_price"),
                                                         premium=x.struct.field("buy_price")))
            ).alias("current_profit")
        )
        df = df.with_columns(
            [
                ((pl.col("break_even") / pl.col("ua_sell_price") - 1) * 100).alias("pct_break_even"),
                (pl.col("max_pot_profit") / pl.col("break_even") * 100).alias("pct_mpp"),
                (pl.col("current_profit") / pl.col("break_even") * 100).alias("pct_cp")
            ]
        )
        df = df.with_columns(
            [
                (pl.col("pct_mpp") / pl.col("t") * 30).alias("pct_monthly_mpp"),
                (pl.col("pct_cp") / pl.col("t") * 30).alias("pct_monthly_cp"),
                ((pl.col("strike_price") / pl.col("ua_final") - 1) * 100).alias("pct_status")
            ]
        )
        return df.select(cols.covered_call.rep).rename(cols.covered_call.rename)
