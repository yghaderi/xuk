:py:mod:`xuk.options`
=====================

.. py:module:: xuk.options


Submodules
----------
.. toctree::
   :titlesonly:
   :maxdepth: 1

   position_builder/index.rst
   position_profit/index.rst
   strategy/index.rst


Package Contents
----------------

Classes
~~~~~~~

.. autoapisummary::

   xuk.options.Strategy
   xuk.options.PositionBuilder
   xuk.options.OptionPositionProfit
   xuk.options.AssetPositionProfit




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



.. py:class:: PositionBuilder(long_call: List[OptionParam], short_call: List[OptionParam], long_put: List[OptionParam], short_put: List[OptionParam], long_ua: List[UAParam], short_ua: List[UAParam], st_range: StParam)


   Build any position and get simulate profit.

   :param long_call: List[OptionParam] long call position params e.g. [{'k':22_000, 'premium':2_000, 'qty':2}]
   :param short_call: List[OptionParam] short call position params e.g. [{'k':22_000, 'premium':2_000, 'qty':2}]
   :param long_put: List[OptionParam] long put position params e.g. [{'k':22_000, 'premium':2_000, 'qty':2}]
   :param short_put: List[OptionParam] short put position params e.g. [{'k':22_000, 'premium':2_000, 'qty':2}]
   :param long_ua: List[UAParam] long underlying asset position params e.g. [{'splot_price':18_000, 'qty':1}]
   :param short_ua: List[UAParam] short underlying asset position params e.g. [{'splot_price':18_000, 'qty':1}]
   :param st_range:
                    StParam to create range of price of assets at maturity,
                        e.g. {'min':2000, 'max':5000,'step':10}

   .. py:method:: simulate_profit() -> List[int]

      The simulation of profit for all given position within the specified range.

      :rtype: List[int]

      .. rubric:: Examples

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



.. py:class:: OptionPositionProfit(st: int, k: int, premium: int, qty: int = 1)


   Calculate option position profit.

   :param st: int, underlying asset price at time of t
   :param k: int, strike price
   :param premium: int, premium
   :param qty: int, quantity

   .. py:method:: long_call() -> int

      Calculate long call position profit.

      :rtype: int


   .. py:method:: short_call() -> int

      Calculate short call position profit.

      :rtype: int


   .. py:method:: long_put() -> int

      Calculate long put position profit.

      :rtype: int


   .. py:method:: short_put() -> int

      Calculate short call position profit.

      :rtype: int



.. py:class:: AssetPositionProfit(price: int, st: int, qty: int = 1)


   Calculate asset position profit.

   :param price: int, asset price at time of 0
   :param st: int, asset price at time of t
   :param qty: int, quantity

   .. py:method:: long() -> int

      Calculate long UA position profit.

      :rtype: int


   .. py:method:: short() -> int

      Calculate short UA position profit.

      :rtype: int



