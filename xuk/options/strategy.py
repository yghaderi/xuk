from collections import namedtuple
from itertools import combinations
from operator import add
from typing import Optional
import polars as pl
import numpy as np

from xuk.options.position_profit import OptionPositionProfit
from xuk.options.utils import cols, manipulation_cols


class Strategy:
    """
    .. raw:: html

        <div dir="rtl">
            پارامترهایِ مهمِ مربوط به استراتژی‌هایِ اختیارِ-معامله رو حساب می‌کنه.
        </div>

    Parameters
    ----------
    call
        polars.DataFrame with (ua:str, ua_ask_price:int, ua_bid_price:int, symbol:str, k:int,
        t:int, bs:int, bid_price:int, ask_price:int) columns. Where ua: Underlying Asset, bs : Black-Scholes
        price, t: Days to expiration date
    put
        polars.DataFrame with (ua:str, ua_ask_price:int, ua_bid_price:int, symbol:str, k:int,
        t:int, bs:int, bid_price:int, ask_price:int) columns. Where ua: Underlying Asset, bs : Black-Scholes
        price, t: Days to expiration date
    call_put

    Examples
    --------
    Import libraries

    >>> from oxtapus import TSETMC
    >>> from xuk.options import Strategy
    >>> import polars as pl

    Get option data and create object

    >>> data = TSETMC().options_mw()
    >>> stg = Strategy(call=data.filter(pl.col("type")=="call"), put=data.filter(pl.col("type")=="put")

    Call strategies

    >>> stg.covered_call()
    shape: (928, 16)
    ┌───────────┬────────────┬───┬────────────┬────────────────┐
    │  writing  ┆ writing_at ┆ … ┆   pct_cp   ┆ pct_monthly_cp │
    │    ---    ┆     ---    ┆   ┆     ---    ┆       ---      │
    │    str    ┆     f64    ┆   ┆     f64    ┆       f64      │
    ╞═══════════╪════════════╪═══╪════════════╪════════════════╡
    │ xxxx 8001 ┆   1961.0   ┆ … ┆  -0.128406 ┆    -0.226599   │
    │     …     ┆      …     ┆ … ┆      …     ┆        …       │
    │ zzzz 1100 ┆    600.0   ┆ … ┆ -16.666667 ┆      -4.0      │
    └───────────┴────────────┴───┴────────────┴────────────────┘

    """

    def __init__(
            self,
            call: Optional[pl.DataFrame] = pl.DataFrame(),
            put: Optional[pl.DataFrame] = pl.DataFrame(),
            call_put: Optional[pl.DataFrame] = pl.DataFrame(),
    ) -> None:
        self.call = call if call.is_empty() else call.filter(pl.col("t") > 0)
        self.put = put if put.is_empty() else put.filter(pl.col("t") > 0)
        self.call_put = call_put

    def covered_call(self) -> pl.DataFrame:
        """
        .. raw:: html

            <div dir="rtl">
                در این استراتژی داراییِ پایه خریداری می‌شه و اختیارِ خرید فروخته می‌شه.
            </div>

        Returns
        -------
        polars.DataFrame contain (writing, writing_at, buy_ua, buy_ua_at,k,t, pct_status,
        break_even, pct_break_even, max_pot_loss, max_pot_profit, pct_mpp, pct_monthly_cp, current_profit, pct_cp,
        pct_monthly_cp) columns.
        """
        df = self.call.filter((pl.col("bid_price") > 0) & (pl.col("ua_ask_price") > 0))

        df = df.with_columns(
            max_pot_profit=pl.col("k") - pl.col("ua_ask_price") + pl.col("bid_price"),
            max_pot_loss=pl.col("bid_price") - pl.col("ua_ask_price"),
            break_even=pl.col("ua_ask_price") - pl.col("bid_price"),
        )

        df = df.with_columns(
            (
                pl.struct(["ua_ask_price", "k", "bid_price"]).map_elements(
                    lambda x: OptionPositionProfit(
                        st=x["ua_ask_price"],
                        k=x["k"],
                        premium=x["bid_price"],
                    ).short_call()
                )
            ).alias("current_profit")
        )
        df = df.with_columns(
            pct_break_even=(pl.col("break_even") / pl.col("ua_ask_price") - 1) * 100,
            pct_mpp=pl.col("max_pot_profit") / pl.col("break_even") * 100,
            pct_cp=pl.col("current_profit") / pl.col("break_even") * 100,
        )
        df = df.with_columns(
            pct_monthly_mpp=pl.col("pct_mpp") / pl.col("t") * 30,
            pct_monthly_cp=pl.col("pct_cp") / pl.col("t") * 30,
            pct_status=(pl.col("k") / pl.col("ua_final") - 1) * 100,
        )
        df = manipulation_cols(df=df, columns=cols.strategy.covered_call)
        return df

    def married_put(self) -> pl.DataFrame:
        """
        .. raw:: html

            <div dir="rtl">
                در این استراتژی داراییِ پایه و اختیارِ فروش خریداری می‌شه.
            </div>

        Returns
        -------
        polars.DataFrame
        """
        df = self.put.filter((pl.col("ask_price") > 0) & (pl.col("ua_ask_price") > 0))

        df = df.with_columns(
            max_pot_profit=pl.lit(np.inf),
            max_pot_loss=pl.col("k") - pl.col("ua_ask_price") - pl.col("ask_price"),
            break_even=pl.col("ua_ask_price") + pl.col("ask_price"),
        )

        df = df.with_columns(
            (
                pl.struct(["ua_ask_price", "k", "ask_price"]).map_elements(
                    lambda x: OptionPositionProfit(
                        st=x["ua_ask_price"],
                        k=x["k"],
                        premium=x["ask_price"],
                    ).long_put()
                )
            ).alias("current_profit")
        )

        df = df.with_columns(
            pct_break_even=(pl.col("break_even") / pl.col("ua_ask_price") - 1) * 100,
            pct_mpp=pl.lit(np.inf),
            pct_cp=pl.col("current_profit") / pl.col("break_even") * 100,
        )
        df = df.with_columns(
            pct_monthly_mpp=pl.lit(np.inf),
            pct_monthly_cp=pl.col("pct_cp") / pl.col("t") * 30,
            pct_status=-(pl.col("k") / pl.col("ua_final") - 1) * 100,
        )
        df = manipulation_cols(df=df, columns=cols.strategy.married_put)
        return df

    def _spread_base(self, stg: str) -> pl.DataFrame:
        """
        <div dir="rtl">
                پایه‌یِ استراتژی‌هایِ spread هست.
            </div>

        Returns
        -------
        polars.DataFrame
        """

        Strategy_ = namedtuple("Strategy", "sell buy")

        df_main = self.call if "put" in stg else self.put
        df_main = df_main.filter(
            (pl.col("bid_price") > 0)
            & (pl.col("ask_price") > 0)
            & (pl.col("ob_level") == 1)
        )
        df_pairs = df_main.group_by(["ua_symbol", "t"]).agg(
            pl.col("bid_price").count().alias("count")
        )
        df = df_main.join(df_pairs.filter(pl.col("count") > 1), on=["ua_symbol", "t"], how="inner")
        groups = df.group_by(["ua_symbol", "t"])

        descending = True if stg.startswith("bull") else False
        df_ = pl.DataFrame()
        for _, data in groups:
            data = data.sort(["k"], descending=descending)
            combo_option = list(
                Strategy_(sell=s, buy=b) for s, b in combinations(data["symbol"], 2)
            )
            combo_k = list(
                Strategy_(sell=s, buy=b) for s, b in combinations(data["k"], 2)
            )
            combo_orderbook_price = list(
                Strategy_(sell=s[0], buy=b[1])
                for s, b in combinations(
                    data.select(["bid_price", "ask_price"]).rows(), 2
                )
            )

            ua_final = data["ua_final"][0]
            max_pot_loss = 0
            max_pot_profit = 0
            current_profit = 0
            match stg:
                case "bull_call_spread":
                    max_pot_loss = [i.sell - i.buy for i in combo_orderbook_price]
                    max_pot_profit = list(
                        map(add, [i.sell - i.buy for i in combo_k], max_pot_loss)
                    )
                    current_profit = []
                    for i in range(len(combo_k)):
                        if all(s <= ua_final for s in combo_k[i]):
                            current_profit.append(max_pot_profit[i])
                        elif all(s >= ua_final for s in combo_k[i]):
                            current_profit.append(max_pot_loss[i])
                        else:
                            current_profit.append(
                                ua_final - combo_k[i].buy + max_pot_loss[i]
                            )
                case "bear_call_spread":
                    max_pot_profit = [i.sell - i.buy for i in combo_orderbook_price]
                    max_pot_loss = list(
                        map(add, [i.sell - i.buy for i in combo_k], max_pot_profit)
                    )
                    current_profit = []
                    for i in range(len(combo_k)):
                        if all(s >= ua_final for s in combo_k[i]):
                            current_profit.append(max_pot_profit[i])
                        elif all(s <= ua_final for s in combo_k[i]):
                            current_profit.append(max_pot_loss[i])
                        else:
                            current_profit.append(
                                -ua_final + combo_k[i].sell + max_pot_profit[i]
                            )
                case "bull_put_spread":
                    max_pot_profit = [i.sell - i.buy for i in combo_orderbook_price]
                    max_pot_loss = list(
                        map(add, [-i.sell + i.buy for i in combo_k], max_pot_profit)
                    )
                    current_profit = []
                    for i in range(len(combo_k)):
                        if all(s <= ua_final for s in combo_k[i]):
                            current_profit.append(max_pot_profit[i])
                        elif all(s >= ua_final for s in combo_k[i]):
                            current_profit.append(max_pot_loss[i])
                        else:
                            current_profit.append(
                                ua_final - combo_k[i].sell + max_pot_profit[i]
                            )
                case "bear_put_spread":
                    max_pot_loss = [i.sell - i.buy for i in combo_orderbook_price]
                    max_pot_profit = list(
                        map(add, [i.buy - i.sell for i in combo_k], max_pot_loss)
                    )

                    current_profit = []
                    for i in range(len(combo_k)):
                        if all(s >= ua_final for s in combo_k[i]):
                            current_profit.append(max_pot_profit[i])
                        elif all(s <= ua_final for s in combo_k[i]):
                            current_profit.append(max_pot_loss[i])
                        else:
                            current_profit.append(
                                -ua_final + combo_k[i].buy + max_pot_loss[i]
                            )

            df_ = pl.concat(
                [
                    df_,
                    pl.DataFrame(
                        {
                            "symbol": combo_option,
                            "k": combo_k,
                            "t": data["t"][0],
                            "ua_symbol": data["ua_symbol"][0],
                            "ua_final": data["ua_final"][0],
                            "orderbook_price": combo_orderbook_price,
                            "max_pot_loss": max_pot_loss,
                            "max_pot_profit": max_pot_profit,
                            "current_profit": current_profit,
                        }
                    ),
                ]
            )
        df_ = df_.with_columns(
            writing=pl.col("symbol").map_elements(lambda x: x["sell"]),
            writing_at=pl.col("orderbook_price").map_elements(lambda x: x["sell"]),
            buy=pl.col("symbol").map_elements(lambda x: x["buy"]),
            buy_at=pl.col("orderbook_price").map_elements(lambda x: x["buy"]),
        ).drop(["symbol", "k", "orderbook_price"])
        df_k = df_main.select(["symbol", "k"]).unique()
        df_ = df_.join(df_k, left_on=["buy"], right_on=["symbol"], how="inner").rename({"k": "k_b"})
        df_ = df_.join(df_k, left_on=["writing"], right_on=["symbol"], how="inner").rename({"k": "k_w"})
        return df_

    def bull_call_spread(self):
        """
        .. raw:: html

            <div dir="rtl">
                در این استراتژی یِ اختیارِ خرید با قیمتِ اعمالِ پایین‌تر خریداری می‌شه و همزمان اختیارِ خریدِ دیگه‌ای با
                تارخِ اعمالِ و داراییِ پایه‌یِ همسان، اما قیمتِ اعمالِ بالاتر فروخته می‌شه.
            </div>

        A bull call spread involves two call options with the same expiration date:

        #. Buy a call option at a lower strike price (gives you the right to buy at that price).
        #. Sell a call option at a higher strike price (obligates you to sell at that price).

        This strategy:

        * **Requires an upfront cost:** You pay a premium for the call option you buy.
        * **Reduces the cost by selling a call option:** You receive a premium from selling the higher strike call.
        * **Limits potential losses:** Your maximum loss is capped at the difference in strike prices minus the net \
        premium paid.

        Caps potential profits: Profit is limited to the difference in strike prices minus the net premium paid.
        It's used when you're moderately bullish on the underlying asset, expecting its price to stay above the lower
        strike price by expiration. However, like any options strategy, it's crucial to assess risks and ensure it
        aligns with your investment goals and risk tolerance.

        Returns
        -------
        polars.DataFrame
        """

        df = self._spread_base(stg="bull_call_spread")
        df = manipulation_cols(df=df, columns=cols.strategy.bull_call_spread)
        return df

    def bear_call_spread(self):
        """
        .. raw:: html

            <div dir="rtl">
                در این استراتژی یِ اختیارِ خرید با قیمتِ اعمالِ بالاتر خریداری می‌شه و همزمان اختیارِ خریدِ دیگه‌ای با
                تارخِ اعمالِ و داراییِ پایه‌یِ همسان، اما قیمتِ اعمالِ پایین‌تر فروخته می‌شه.
            </div>


        A bear call spread involves two call options with the same expiration date:

        #. Sell a call option at a lower strike price (obligates you to sell at that price).
        #. Buy a call option at a higher strike price (gives you the right to buy at that price).

        This strategy:

        * **Generates income:** You receive a premium by selling the call option.
        * **Limits risk:** Your maximum loss is capped, and it's reduced by the premium received.
        * **Caps potential profits:** Profit is limited to the premium received.

        It's used when you're moderately bearish on the underlying asset, expecting its price to stay below the lower
        strike price by expiration. However, it's important to assess risks and ensure this strategy aligns with your
        investment goals and risk tolerance before implementing it.

        Returns
        -------
        polars.DataFrame
        """
        df = self._spread_base(stg="bear_call_spread")
        df = manipulation_cols(df=df, columns=cols.strategy.bear_call_spread)
        return df

    def bull_put_spread(self):
        """
        .. raw:: html

            <div dir="rtl">
                در این استراتژی یِ اختیارِ فروش با قیمتِ اعمالِ پایین‌تر خریداری می‌شه و همزمان اختیارِ فروشِ دیگه‌ای با
                تارخِ اعمالِ و داراییِ پایه‌یِ همسان، اما قیمتِ اعمالِ بالاتر فروخته می‌شه.
            </div>

        A bull put spread is an options trading strategy used when an investor expects a moderate increase in the price
        of the underlying asset. It involves two put options: selling one put option and buying another put option with
        the same expiration date but at a lower strike price. Here’s how it works:

        #. Sell a Put Option: You sell a put option with a higher strike price, usually out-of-the-money (OTM), to
        receive a premium.

        #. Buy a Put Option: Simultaneously, you buy a put option with a lower strike price, usually in-the-money (ITM),
        paying a smaller premium.

        The idea behind a bull put spread is to benefit from a bullish market while limiting potential losses. The
        maximum profit is the difference between the premiums received and paid, and it occurs if the underlying asset’s
        price remains above the higher strike price at expiration. The maximum loss is limited to the difference between
        the strike prices minus the net premium received.

        This strategy allows you to capitalize on a moderate rise in the underlying asset's price, and by using options,
        it provides a defined risk-reward scenario.

        Returns
        -------
        polars.DataFrame
        """
        df = self._spread_base(stg="bull_put_spread")
        df = manipulation_cols(df=df, columns=cols.strategy.bull_put_spread)
        return df

    def bear_put_spread(self):
        """
        .. raw:: html

            <div dir="rtl">
                در این استراتژی یِ اختیارِ فروش با قیمتِ اعمالِ پایین‌تر خریداری می‌شه و همزمان اختیارِ فروشِ دیگه‌ای با
                تارخِ اعمالِ و داراییِ پایه‌یِ همسان، اما قیمتِ اعمالِ بالاتر فروخته می‌شه.
            </div>


        A bear put spread, also known as a put debit spread or a bear put credit spread, is an options trading strategy
        used when an investor expects a moderate decrease in the price of the underlying asset. It involves buying one
        put option and simultaneously selling another put option with the same expiration date but at a lower strike
        price. Here's how it works:

        #. Buy a Put Option: You buy a put option with a higher strike price, usually in-the-money (ITM), paying a
        higher premium.

        #. Sell a Put Option: Simultaneously, you sell a put option with a lower strike price, usually out-of-the-money
        (OTM), to receive a premium.

        The goal of a bear put spread is to profit from a declining market while limiting potential losses. The maximum
        profit is the difference between the strike prices minus the net premium paid, and it occurs if the underlying
        asset's price is below the lower strike price at expiration. The maximum loss is limited to the net premium paid
        for the spread.

        This strategy allows you to benefit from a moderate decline in the underlying asset's price, and by using
        options, it provides a defined risk-reward scenario.

        Here's a brief summary of the key points:

        * **Maximum Profit:** The difference between the strike prices minus the net premium paid.
        * **Maximum Loss:** Limited to the net premium paid for the spread.
        * **Break-even Point:** The underlying asset's price at which the total gains equal the total losses, and it is
        calculated as the higher strike price minus the net premium paid.

        Returns
        -------
        polars.DataFrame
        """
        df = self._spread_base(stg="bear_put_spread")
        df = manipulation_cols(df=df, columns=cols.strategy.bear_put_spread)
        return df
