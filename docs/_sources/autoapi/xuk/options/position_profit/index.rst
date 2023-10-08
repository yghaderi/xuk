:py:mod:`xuk.options.position_profit`
=====================================

.. py:module:: xuk.options.position_profit


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   xuk.options.position_profit.OptionPositionProfit
   xuk.options.position_profit.AssetPositionProfit




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



