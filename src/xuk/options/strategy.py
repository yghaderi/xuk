from collections import namedtuple
from itertools import combinations
from typing import Optional
from operator import add
import polars as pl
import numpy as np

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
        self.call = call.filter(pl.col("t") > 0) if call else None
        self.put = put.filter(pl.col("t") > 0) if put else None
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

    def married_put(self):
        df = self.call.filter(pl.col("sell_price") > 0)

        df = df.with_columns(
            [
                pl.lit(np.inf).alias("max_pot_profit"),
                (pl.col("strike_price") - pl.col("ua_sell_price") - pl.col("sell_price")).alias("max_pot_loss"),
                (pl.col("ua_sell_price") - pl.col("sell_price")).alias("break_even")
            ]
        )

        df = df.with_columns(
            (
                pl.struct(["ua_sell_price", "strike_price", "buy_price"]).map_batches(
                    lambda x: position_profit.long_put(st=x.struct.field("ua_sell_price"),
                                                       k=x.struct.field("strike_price"),
                                                       premium=x.struct.field("sell_price")))
            ).alias("current_profit")
        )

        df = df.with_columns(
            [
                ((pl.col("break_even") / pl.col("ua_sell_price") - 1) * 100).alias("pct_break_even"),
                pl.lit(np.inf).alias("pct_mpp"),
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

        return df.select(cols.married_put.rep).rename(cols.married_put.rename)

    def bull_call_spread(self):
        """
        خرید اختیارِ خرید با قیمتِ اعمالِ پایین و فروشِ اختیارِ خرید با قیمتِ اعمالِ بالا در زمانِ اعمالِ همسان
        بیشینه سود برابر است با تفاوتِ بینِ دو قیمتِ اعمال منهایِ پرمیوم پرداختی
        بیشینه ضرر هم برابر است با پرمیوم پرداختی
        """
        stg = namedtuple("BullCallSpread", "sell_hsp buy_lsp")
        df = self.call.filter((pl.col("buy_price") > 0) & (pl.col("sell_price") > 0))
        df_pairs = df.group_by(["ua", "t"]).agg(pl.col("buy_price").count().alias("count"))
        df = df.join(df_pairs.filter(pl.col("count") > 1), on=["ua", "t"], how="inner")
        groups = df.group_by(["ua", "t"]).count()

        records = []
        for name, group in groups:
            group.reset_index(inplace=True)
            group = group.sort_values(by=["strike_price"], ascending=False)
            combo_option = list(
                stg(sell=s, buy=b) for s, b in combinations(group.option, 2)
            )
            combo_strike_price = list(
                stg(sell=s, buy=b) for s, b in combinations(group.strike_price, 2)
            )
            combo_ob_price = list(
                stg(sell=s, buy=b)
                for s, b in combinations(
                    group[["sell_price", "buy_price"]].itertuples(index=False), 2
                )
            )
            combo_bs = list(
                stg(sell=s, buy=b) for s, b in combinations(group.bs, 2)
            )
            max_pot_loss = [
                ps.buy_price - pb.sell_price for ps, pb in combo_ob_price
            ]
            max_pot_profit = list(
                map(add, [ss - sb for ss, sb in combo_strike_price], max_pot_loss)
            )

            current_profit = []
            for i in range(len(combo_strike_price)):
                if all(
                        s <= group.ua_final.values[0] for s in combo_strike_price[i]
                ):
                    current_profit.append(max_pot_profit[i])
                elif all(
                        s >= group.ua_final.values[0] for s in combo_strike_price[i]
                ):
                    current_profit.append(max_pot_loss[i])
                else:
                    current_profit.append(
                        group.ua_final.values[0]
                        - combo_strike_price[i].buy
                        + max_pot_loss[i]
                    )

            records.append(
                {
                    "option": combo_option,
                    "strike_price": combo_strike_price,
                    "t": group.t.values[0],
                    "bs": combo_bs,
                    "ua": group.ua.values[0],
                    "ua_final": group.ua_final.values[0],
                    "ob_price": combo_ob_price,
                    "max_pot_loss": max_pot_loss,
                    "max_pot_profit": max_pot_profit,
                    "current_profit": current_profit,
                }
            )
        return df
