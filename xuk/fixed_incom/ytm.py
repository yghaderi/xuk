import datetime
import logging
from dateutil.relativedelta import relativedelta
from sympy import nsolve, solve, symbols, Sum
from scipy.optimize import fsolve
import numpy as np


class YTM:
    def __init__(self):
        self.month_days = 30
        self.year_days = 365

    def _evenly_spaced_periods(self, date: datetime.date, period: int):
        """
        Calculation of the number of evenly periods of **n** months until today

        محاسبه‌یِ تعداد‌ِ دوره‌هایِ **اِن** ماهه تا امروز

        Parameters
        ----------
        date: datetime.date
            bond maturity date
        period: int
            coupon period
        Returns
        -------
        floor_division: int
            number of period
            [تعدادِ دوره‌ها]

        modulo: float
            the ratio of the remaining days to the period days
            [تعدادِ روزهایِ باقیمانده به تعدادِ روزهایِ دوره]
        """
        today = datetime.date.today()
        floor_division = 0
        while today <= date + relativedelta(months=-period):
            date += relativedelta(months=-period)
            floor_division += 1
        modulo = (date - today).days / (period * self.month_days) if date > today else 0
        return int(floor_division), modulo

    def coupon_bond(
        self,
        fv: int | float,
        pv: int | float,
        coupon_rate: float,
        maturity_date: datetime.date,
        period: int,
        adjust_pv: bool = True,
    ):
        """
        Calculates yield to maturity for coupon bonds.

        بازده-تا-سررسید را برای اوراقِ کپن-دار محاسبه می‌کند.

        .. note::
            Note that the output amount is based on the coupon payment period. For example, if the cap period is 3
            months, the ``yield-to-maturity`` is 3 months (!) which should be converted to annual.

        .. note::
         توجه شود که مقدار خروجیِ بر اساسِ دوره‌یِ پرداختِ کپن است.
          برای نمونه اگر دوره‌یِ کپن 3 ماهه باشد، ``بازده-تا-سررسید`` 3 ماهه است(!) که باید به سالانه تبدیل شود.


        Parameters
        ----------
        fv: int
            future value paid at maturity, or the par value of the bond
        pv: int or float
            present value, or the price of the bond
        coupon_rate: float
            nominal yield
        maturity_date: datetime.date
            bond maturity date
        period: int
            coupon period (***number of months***)
        adjust_pv: bool
            It depends on the market. If the yield of the coupon due to the days that have passed until the day of the
            transaction is paid separately, it should be entered ``True``, otherwise it should be entered ``False``.
            Default: ``True``


        Returns
        -------
        yield-to-maturity: float

        Examples
        --------
        Import libraries

        >>> import datetime
        >>> from xuk.fixed_incom import YTM

        >>> datetime.date.today()
        datetime.date(2023, 10, 13)
        >>> YTM().coupon_bond(fv=100, pv=98, coupon_rate=0.09,maturity_date= datetime.date(2024,6,2), period=6)
        0.10675403744515967
        """
        floor_division, modulo = self._evenly_spaced_periods(
            date=maturity_date, period=period
        )
        if adjust_pv:
            if modulo != 0:
                pv = pv + fv * (1 - modulo) * coupon_rate

        try:
            r, i = symbols("r i")
            pmt = fv * coupon_rate  # coupon payment per period
            fd_event = (
                Sum(pmt / (1 + r) ** (i + modulo), (i, 1, floor_division))
                if floor_division > 0
                else 0
            )
            m_event = pmt / (1 + r) ** modulo if modulo > 0 else 0
            eq = fd_event + m_event + fv / (1 + r) ** (floor_division + modulo) - pv
            if floor_division:
                return float(nsolve(eq, 0))
            return float(solve(eq, r)[0])
        except Exception as e:
            logging.warning(f"Have a problem! {e}")
            return np.nan

    def zero_coupon_bond(self, fv: int | float, pv: int | float, n: int):
        """
        Calculates yield to maturity for zero-coupon bonds.

        بازده-تا-سررسید را برای اوراقِ بدونِ-کپن محاسبه می‌کند.

        .. note::
            ``بازده-تا-سررسید`` سالانه است!

        .. note::
            ``yield-to-maturity`` is annum!

        Parameters
        ----------
        fv: int or float
            future value paid at maturity, or the par value of the bond
        pv: int or float
            present value, or the price of the bond
        n: int
            number of days to maturity

        Returns
        -------
        yield-to-maturity: float

        Examples
        --------
        Import libraries

        >>> from xuk.fixed_incom import YTM

        >>> YTM().zero_coupon_bond(fv=100, pv=73, n=543)
        0.23558667358353835
        """
        try:
            n = n / self.year_days

            def eq(val):
                r = val
                return fv / (1 + r) ** n - pv

            return fsolve(eq, 0)[0]
        except Exception as e:
            logging.warning(f"Have a problem! {e}")
            return np.nan
