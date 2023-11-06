:py:mod:`xuk.fixed_incom`
=========================

.. py:module:: xuk.fixed_incom


Submodules
----------
.. toctree::
   :titlesonly:
   :maxdepth: 1

   ytm/index.rst


Package Contents
----------------

Classes
~~~~~~~

.. autoapisummary::

   xuk.fixed_incom.YTM




.. py:class:: YTM


   .. py:method:: coupon_bond(fv: int | float, pv: int | float, coupon_rate: float, maturity_date: datetime.date, period: int, adjust_pv: bool = True)

      Calculates yield to maturity for coupon bonds.

      بازده-تا-سررسید را برای اوراقِ کپن-دار محاسبه می‌کند.

      .. note::
          Note that the output amount is based on the coupon payment period. For example, if the cap period is 3
          months, the ``yield-to-maturity`` is 3 months (!) which should be converted to annual.

      .. note::
       توجه شود که مقدار خروجیِ بر اساسِ دوره‌یِ پرداختِ کپن است.
        برای نمونه اگر دوره‌یِ کپن 3 ماهه باشد، ``بازده-تا-سررسید`` 3 ماهه است(!) که باید به سالانه تبدیل شود.


      :param fv: future value paid at maturity, or the par value of the bond
      :type fv: int
      :param pv: present value, or the price of the bond
      :type pv: int or float
      :param coupon_rate: nominal yield
      :type coupon_rate: float
      :param maturity_date: bond maturity date
      :type maturity_date: datetime.date
      :param period: coupon period (***number of months***)
      :type period: int
      :param adjust_pv: It depends on the market. If the yield of the coupon due to the days that have passed until the day of the
                        transaction is paid separately, it should be entered ``True``, otherwise it should be entered ``False``.
                        Default: ``True``
      :type adjust_pv: bool

      :returns: **yield-to-maturity**
      :rtype: float

      .. rubric:: Examples

      Import libraries

      >>> import datetime
      >>> from xuk.fixed_incom import YTM

      >>> datetime.date.today()
      datetime.date(2023, 10, 13)
      >>> YTM().coupon_bond(fv=100, pv=98, coupon_rate=0.09,maturity_date= datetime.date(2024,6,2), period=6)
      0.10675403744515967


   .. py:method:: zero_coupon_bond(fv: int | float, pv: int | float, n: int)

      Calculates yield to maturity for zero-coupon bonds.

      بازده-تا-سررسید را برای اوراقِ بدونِ-کپن محاسبه می‌کند.

      .. note::
          ``بازده-تا-سررسید`` سالانه است!

      .. note::
          ``yield-to-maturity`` is annum!

      :param fv: future value paid at maturity, or the par value of the bond
      :type fv: int or float
      :param pv: present value, or the price of the bond
      :type pv: int or float
      :param n: number of days to maturity
      :type n: int

      :returns: **yield-to-maturity**
      :rtype: float

      .. rubric:: Examples

      Import libraries

      >>> from xuk.fixed_incom import YTM

      >>> YTM().zero_coupon_bond(fv=100, pv=73, n=543)
      0.23558667358353835



