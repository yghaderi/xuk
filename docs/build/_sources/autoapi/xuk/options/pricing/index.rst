:py:mod:`xuk.options.pricing`
=============================

.. py:module:: xuk.options.pricing


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   xuk.options.pricing.Pricing




.. py:class:: Pricing


   .. py:method:: black_scholes_merton(s0: float | str, k: float | str, t: int, sigma: float, type_: Literal[call, put], r: float, div: float | int = 0) -> int

      Black and Scholes and Merton formula for European option-pricing.

      :math:`C = N(d_1)S_T-N(d_2)K_e^{-rT}`

      where

      .. line-block::
          :math:`d_1 = \frac {ln\frac{S_T}{K}+(r+\frac {\sigma^2}{2})T}{\sigma\sqrt{T}}`
          :math:`d_2 = d_1 - \sigma\sqrt{T}`
          :math:`C`: call option value
          :math:`S_t`: underlying asset price
          :math:`N`: CDF of the normal distribution
          :math:`K`: strike-price
          :math:`e`: the base of the natural log function, approximately 2.71828
          :math:`r`: risk-free interest rate
          :math:`T`: time to expiration of option, in years
          :math:`ln`: natural logarithm function
          :math:`\sigma`: standard deviation of the annualized continuously compounded rate of return of the underlying asset.

      :param s0: current underlying asset price
      :param k: strike-price
      :param t: day to expiration of option, > 0
      :param sigma: standard deviation of the daily underlying asset return
      :param type\_:
                     * "call": call option
                     * "put": put option
      :param r: risk-free interest rate
      :param div: dividends before option expiration. Default: ``0``

      :returns: **option value**
      :rtype: int



