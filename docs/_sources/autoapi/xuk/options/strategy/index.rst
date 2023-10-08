:py:mod:`xuk.options.strategy`
==============================

.. py:module:: xuk.options.strategy


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   xuk.options.strategy.Strategy




.. py:class:: Strategy(call: Optional[polars.DataFrame] = pl.DataFrame(), put: Optional[polars.DataFrame] = pl.DataFrame(), call_put: Optional[polars.DataFrame] = pl.DataFrame())


   It calculates the necessary parameters related to the well-known option trading strategies.

   :param call: polars.DataFrame with (ua:str, ua_sell_price:int, ua_buy_price:int, symbol:str, strike_price:int,
                t:int, bs:int, buy_price:int, sell_price:int) columns. Where ua: Underlying Asset, bs : Black-Scholes
                price, t: Days to expiration date
   :param put: polars.DataFrame with (ua:str, ua_sell_price:int, ua_buy_price:int, symbol:str, strike_price:int,
               t:int, bs:int, buy_price:int, sell_price:int) columns. Where ua: Underlying Asset, bs : Black-Scholes
               price, t: Days to expiration date
   :param call_put:

   .. py:method:: covered_call() -> polars.DataFrame

      Is the purchase of a share of stock coupled with a sale of a call option on that stock.

      :returns: * *polars.DataFrame contain (writing, writing_at, buy_ua, buy_ua_at,strike_price,t, pct_status,*
                * *break_even, pct_break_even, max_pot_loss, max_pot_profit, pct_mpp, pct_monthly_cp, current_profit, pct_cp,*
                * *pct_monthly_cp) columns.*


   .. py:method:: married_put() -> polars.DataFrame

      Is the purchase of a share of stock coupled with a purchase of a put option on that stock.

      :returns: * *polars.DataFrame contain (writing, writing_at, buy_ua, buy_ua_at,strike_price,t, pct_status,*
                * *break_even, pct_break_even, max_pot_loss, max_pot_profit, pct_mpp, pct_monthly_cp, current_profit, pct_cp,*
                * *pct_monthly_cp) columns.*


   .. py:method:: bull_call_spread()

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

      6. **Breakeven Point**: The breakeven point for this strategy is the sum of the lower strike price and the net premium paid for the spread. In other words, it's the point at which your gains equal your initial cost.

      7. **Risk-Reward Ratio**: A bull call spread provides a limited potential profit and a limited potential loss. The risk-reward ratio is typically skewed in favor of limited profit potential.

      8. **Time Decay**: Time decay (theta) can impact the value of both the long and short call options. Generally, the impact of time decay is smaller on the long call than on the short call. This can affect the profitability of the strategy.

      In summary, a bull call spread is a strategy that allows investors to benefit from a moderate bullish view on an underlying asset while controlling their risk. It's a defined-risk strategy with limited profit potential and is often used when an investor expects a moderate price increase but wants to reduce the cost of buying a call option outright. Traders should carefully consider the strike prices, expiration date, and market conditions when implementing this strategy.

      :rtype: polars.DataFrame



