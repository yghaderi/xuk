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



