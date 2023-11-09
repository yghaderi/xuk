from collections import namedtuple
from itertools import combinations
from operator import add
from typing import Optional
import polars as pl
import numpy as np

from xuk.options.position_profit import OptionPositionProfit
from xuk.options.utils import cols


class Strategy:
    """
    It calculates the necessary parameters related to the well-known option trading strategies.

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

    >>> from oxtapus.ise import TSETMC
    >>> from xuk.options import Strategy
    >>> import polars as pl

    Get option data and create object

    >>> data = pl.from_pandas(TSETMC().option_market_watch())
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
        A covered call position is the purchase of a share of stock coupled with a sale of a call option on that stock.

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
        return df.select(cols.covered_call.rep).rename(cols.covered_call.rename)

    def married_put(self) -> pl.DataFrame:
        """
        Is the purchase of a share of stock coupled with a purchase of a put option on that stock.

        Returns
        -------
        polars.DataFrame contain (writing, writing_at, buy_ua, buy_ua_at,k,t, pct_status,
        break_even, pct_break_even, max_pot_loss, max_pot_profit, pct_mpp, pct_monthly_cp, current_profit, pct_cp,
        pct_monthly_cp) columns.
        """
        df = self.put.filter((pl.col("ask_price") > 0) & (pl.col("ua_ask_price") > 0))

        df = df.with_columns(
            max_pot_profit=pl.lit(np.inf),
            max_pot_loss=pl.col("k") - pl.col("ua_ask_price") - pl.col("ask_price"),
            break_even=pl.col("ua_ask_price") - pl.col("ask_price"),
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
            pct_monthly_mpp=pl.col("pct_mpp") / pl.col("t") * 30,
            pct_monthly_cp=pl.col("pct_cp") / pl.col("t") * 30,
            pct_status=(pl.col("k") / pl.col("ua_final") - 1) * 100,
        )

        return df.select(cols.married_put.rep).rename(cols.married_put.rename)

    def bull_call_spread(self):
        """
        A bull call spread is an options trading strategy that's used when an investor is moderately bullish on the underlying asset (e.g., a stock, index, or commodity) and wants to profit from an anticipated upward price movement while also limiting their potential downside risk. It involves buying one call option and simultaneously selling another call option with the same expiration date but at a higher strike price. This strategy is also known as a "debit call spread" because it typically requires an upfront payment (debit) to establish the position.

        Here are the key components and characteristics of a bull call spread:

        1. **Components**:
           - **Buy a Call Option**: You start by buying a call option with a lower strike price (the strike price at which you have the right to buy the underlying asset).
           - **Sell a Call Option**: Simultaneously, you sell a call option with a higher strike price than the one you bought. This is often referred to as the "short call" or "written call."

        2. **Expiration Date**: Both the long and short call options should have the same expiration date.

        3. **Strike Prices**:
           - The strike price of the long call option is typically below the current market price of the underlying asset.
           - The strike price of the short call option is higher than the strike price of the long call.

        4. **Profit Potential**: A bull call spread profits from a rising price of the underlying asset. The maximum profit is limited and occurs when the price of the underlying asset is above the higher strike price at expiration.

        5. **Risk and Losses**: The maximum loss for a bull call spread is limited to the initial cost (debit) of establishing the position. This loss occurs if the price of the underlying asset is below the lower strike price at expiration.

        6. **Break-even Point**: The break-even point for this strategy is the sum of the lower strike price and the net premium paid for the spread. In other words, it's the point at which your gains equal your initial cost.

        7. **Risk-Reward Ratio**: A bull call spread provides a limited potential profit and a limited potential loss. The risk-reward ratio is typically skewed in favor of limited profit potential.

        8. **Time Decay**: Time decay (theta) can impact the value of both the long and short call options. Generally, the impact of time decay is smaller on the long call than on the short call. This can affect the profitability of the strategy.

        In summary, a bull call spread is a strategy that allows investors to benefit from a moderate bullish view on an underlying asset while controlling their risk. It's a defined-risk strategy with limited profit potential and is often used when an investor expects a moderate price increase but wants to reduce the cost of buying a call option outright. Traders should carefully consider the strike prices, expiration date, and market conditions when implementing this strategy.

        Returns
        -------
        polars.DataFrame
        """
        Strategy_ = namedtuple("Strategy", "sell buy")
        df = self.call.filter(
            (pl.col("bid_price") > 0)
            & (pl.col("ask_price") > 0)
            & (pl.col("quote") == 1)
        )
        df_pairs = df.group_by(["ua", "t"]).agg(
            pl.col("bid_price").count().alias("count")
        )
        df = df.join(df_pairs.filter(pl.col("count") > 1), on=["ua", "t"], how="inner")
        groups = df.group_by(["ua", "t"])

        df_ = pl.DataFrame()
        for _, data in groups:
            data = data.sort(["k"], descending=True)
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
            max_pot_loss = [i.sell - i.buy for i in combo_orderbook_price]
            max_pot_profit = list(
                map(add, [i.sell - i.buy for i in combo_k], max_pot_loss)
            )

            current_profit = []
            for i in range(len(combo_k)):
                if all(s <= data["ua_final"][0] for s in combo_k[i]):
                    current_profit.append(max_pot_profit[i])
                elif all(s >= data["ua_final"][0] for s in combo_k[i]):
                    current_profit.append(max_pot_loss[i])
                else:
                    current_profit.append(
                        data["ua_final"][0] - combo_k[i].buy + max_pot_loss[i]
                    )

            df_ = pl.concat(
                [
                    df_,
                    pl.DataFrame(
                        {
                            "symbol": combo_option,
                            "k": combo_k,
                            "t": data["t"][0],
                            "ua": data["ua"][0],
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
            writing=pl.col("symbol").map_elements(lambda x: x[0]),
            buy=pl.col("symbol").map_elements(lambda x: x[1]),
            writing_at=pl.col("orderbook_price").map_elements(lambda x: x[0]),
            buy_at=pl.col("orderbook_price").map_elements(lambda x: x[0]),
        ).drop(["symbol", "k", "orderbook_price"])
        return df_.select(cols.bull_call_spread.rep)

    def bear_call_spread(self):
        """
        A bear call spread is an options trading strategy that involves two call options with the same expiration date but different strike prices. This strategy is used by investors who are moderately bearish on the underlying asset's price and want to profit from a potential decrease in the asset's price. Here's how a bear call spread works:

        1. **Select the Underlying Asset:** You start by choosing an underlying asset, such as a stock, index, or commodity.

        2. **Sell a Call Option:** You sell (write) a call option with a strike price that's closer to the current market price of the underlying asset. This is called the "short call" or "short leg" of the spread. By selling this option, you collect a premium.

        3. **Buy a Call Option:** Simultaneously, you buy a call option with a higher strike price than the one you sold. This is called the "long call" or "long leg" of the spread. This purchase also involves paying a premium.

        4. **Limited Risk:** The primary advantage of the bear call spread is that it has limited risk. The premium received from selling the short call partially offsets the premium paid for the long call. Your maximum loss is capped at the difference between the strike prices minus the net premium received.

        5. **Profit Potential:** Your maximum profit is limited to the net premium you receive when you enter the trade. This profit occurs if the underlying asset's price remains below the strike price of the short call at expiration.

        6. **Break-even Point:** The strategy's break-even point is the strike price of the short call plus the net premium received. As long as the underlying asset's price remains below this point, you won't incur a loss.

        7. **Expiration:** The strategy typically involves holding both the short and long call options until expiration. If the underlying asset's price is below the short call's strike price at expiration, the short call expires worthless, and you keep the premium. The long call can also expire worthless or be sold for any remaining value.

        A bear call spread can be a useful strategy when you expect a moderate downward price movement in the underlying asset. It allows you to profit from the premium received by selling the short call while limiting your potential losses. However, keep in mind that options trading carries risks and should only be undertaken if you understand the strategy and the potential outcomes.

        Returns
        -------
        polars.DataFrame
        """
        Strategy_ = namedtuple("Strategy", "sell buy")
        df = self.call.filter(
            (pl.col("bid_price") > 0)
            & (pl.col("ask_price") > 0)
            & (pl.col("quote") == 1)
        )
        df_pairs = df.group_by(["ua", "t"]).agg(
            pl.col("bid_price").count().alias("count")
        )
        df = df.join(df_pairs.filter(pl.col("count") > 1), on=["ua", "t"], how="inner")
        groups = df.group_by(["ua", "t"])

        df_ = pl.DataFrame()
        for _, data in groups:
            data = data.sort(["k"], descending=False)
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
            max_pot_profit = [i.buy - i.sell for i in combo_orderbook_price]
            max_pot_loss = list(
                map(add, [i.sell - i.buy for i in combo_k], max_pot_profit)
            )

            current_profit = []
            for i in range(len(combo_k)):
                if all(s >= data["ua_final"][0] for s in combo_k[i]):
                    current_profit.append(max_pot_profit[i])
                elif all(s <= data["ua_final"][0] for s in combo_k[i]):
                    current_profit.append(max_pot_loss[i])
                else:
                    current_profit.append(
                        -data["ua_final"][0] + combo_k[i].sell + max_pot_loss[i]
                    )

            df_ = pl.concat(
                [
                    df_,
                    pl.DataFrame(
                        {
                            "symbol": combo_option,
                            "k": combo_k,
                            "t": data["t"][0],
                            "ua": data["ua"][0],
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
            writing=pl.col("symbol").map_elements(lambda x: x[0]),
            buy=pl.col("symbol").map_elements(lambda x: x[1]),
            writing_at=pl.col("orderbook_price").map_elements(lambda x: x[0]),
            buy_at=pl.col("orderbook_price").map_elements(lambda x: x[0]),
        ).drop(["symbol", "k", "orderbook_price"])
        return df_.select(cols.bear_call_spread.rep)

    def bull_put_spread(self):
        Strategy_ = namedtuple("Strategy", "sell buy")
        df = self.put.filter(
            (pl.col("bid_price") > 0)
            & (pl.col("ask_price") > 0)
            & (pl.col("quote") == 1)
        )
        df_pairs = df.group_by(["ua", "t"]).agg(
            pl.col("bid_price").count().alias("count")
        )
        df = df.join(df_pairs.filter(pl.col("count") > 1), on=["ua", "t"], how="inner")
        groups = df.group_by(["ua", "t"])

        df_ = pl.DataFrame()
        for _, data in groups:
            data = data.sort(["k"], descending=True)
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
            max_pot_profit = [i.sell - i.buy for i in combo_orderbook_price]
            max_pot_loss = list(
                map(add, [i.sell - i.buy for i in combo_k], max_pot_profit)
            )

            current_profit = []
            for i in range(len(combo_k)):
                if all(s <= data["ua_final"][0] for s in combo_k[i]):
                    current_profit.append(max_pot_profit[i])
                elif all(s >= data["ua_final"][0] for s in combo_k[i]):
                    current_profit.append(max_pot_loss[i])
                else:
                    current_profit.append(
                        data["ua_final"][0] - combo_k[i].sell + max_pot_loss[i]
                    )

            df_ = pl.concat(
                [
                    df_,
                    pl.DataFrame(
                        {
                            "symbol": combo_option,
                            "k": combo_k,
                            "t": data["t"][0],
                            "ua": data["ua"][0],
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
            writing=pl.col("symbol").map_elements(lambda x: x[0]),
            buy=pl.col("symbol").map_elements(lambda x: x[1]),
            writing_at=pl.col("orderbook_price").map_elements(lambda x: x[0]),
            buy_at=pl.col("orderbook_price").map_elements(lambda x: x[0]),
        ).drop(["symbol", "k", "orderbook_price"])
        return df_.select(cols.bull_put_spread.rep)

    def bear_put_spread(self):
        Strategy_ = namedtuple("Strategy", "sell buy")
        df = self.put.filter(
            (pl.col("bid_price") > 0)
            & (pl.col("ask_price") > 0)
            & (pl.col("quote") == 1)
        )
        df_pairs = df.group_by(["ua", "t"]).agg(
            pl.col("bid_price").count().alias("count")
        )
        df = df.join(df_pairs.filter(pl.col("count") > 1), on=["ua", "t"], how="inner")
        groups = df.group_by(["ua", "t"])

        df_ = pl.DataFrame()
        for _, data in groups:
            data = data.sort(["k"], descending=False)
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
            max_pot_loss = [i.sell - i.buy for i in combo_orderbook_price]
            max_pot_profit = list(
                map(add, [i.buy - i.sell for i in combo_k], max_pot_loss)
            )

            current_profit = []
            for i in range(len(combo_k)):
                if all(s >= data["ua_final"][0] for s in combo_k[i]):
                    current_profit.append(max_pot_profit[i])
                elif all(s <= data["ua_final"][0] for s in combo_k[i]):
                    current_profit.append(max_pot_loss[i])
                else:
                    current_profit.append(
                        -data["ua_final"][0] + combo_k[i].sell + max_pot_loss[i]
                    )

            df_ = pl.concat(
                [
                    df_,
                    pl.DataFrame(
                        {
                            "symbol": combo_option,
                            "k": combo_k,
                            "t": data["t"][0],
                            "ua": data["ua"][0],
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
            writing=pl.col("symbol").map_elements(lambda x: x[0]),
            buy=pl.col("symbol").map_elements(lambda x: x[1]),
            writing_at=pl.col("orderbook_price").map_elements(lambda x: x[0]),
            buy_at=pl.col("orderbook_price").map_elements(lambda x: x[0]),
        ).drop(["symbol", "k", "orderbook_price"])
        return df_.select(cols.bear_put_spread.rep)
