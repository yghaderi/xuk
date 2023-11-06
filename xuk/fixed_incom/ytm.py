import datetime
from dateutil.relativedelta import relativedelta
from sympy import nsolve, solve, symbols, Sum
from scipy.optimize import fsolve


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
            n: int,
            adjust_pv: bool = True,
    ):
        """
        .. raw:: html

            <div dir="rtl">
                بازده-تا-سررسید رو برای اوراقِ کوپن-دار محاسبه می‌کنه.
            </div>


        .. note::
            .. raw:: html

                <div dir="rtl">
                     دقت کن که مقدار خروجیِ بر اساسِ دوره‌یِ پرداختِ کوپن به صورتِ مؤثر سالانه می‌شه.
                </div>


        Parameters
        ----------
        fv: int
            قیمتِ اسمیِ اوراق
        pv: int or float
            قیمتِ فعلی
        coupon_rate: float
            نرخِ بازدهِ اسمیِ هر کوپن
        maturity_date: datetime.date
            تاریخِ سررسید
        n: int
            دوره‌یِ پرداخت سود (بر حسب ماه)
        adjust_pv: bool, default True
            این مورد بسته به نوعِ بازاره. اگه بازدهِ اسمیِ روزهایِ سپری-شده از کوپن جاری در قیمتِ معامله لحاظ نمیشه و
            جداگانه در کارگزاری تسوه می‌شه-معمولن در بورسِ ایران اینجوریه- ``ترو`` رو وارد کنید در غیرِ این ``فالس``.

        Returns
        -------
        yield-to-maturity: float

        Examples
        --------
        Import libraries

        >>> import datetime
        >>> from xuk.fixed_incom import YTM

        >>> datetime.date.today()
        datetime.date(2023, 11, 6)
        >>> YTM().coupon_bond(fv=100, pv=98, coupon_rate=0.09,maturity_date= datetime.date(2024,6,2), n=6)
        0.229779371206994
        """
        floor_division, modulo = self._evenly_spaced_periods(
            date=maturity_date, period=n
        )
        if adjust_pv:
            if modulo != 0:
                pv = pv + fv * (1 - modulo) * coupon_rate

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
            return (1 + float(nsolve(eq, 0))) ** (12 / n) - 1
        return (1 + float(solve(eq, r)[0])) ** (12 / n) - 1

    def zero_coupon_bond(self, fv: int | float, pv: int | float, n: int):
        """
        .. raw:: html

            <div dir="rtl">
                بازده-تا-سررسید را برای اوراقِ بدونِ-کوپن محاسبه می‌کند.
            </div>

        .. note::
            .. raw:: html

                <div dir="rtl">
                    بازده-تا-سررسید سالانه است!
                </div>

        Parameters
        ----------
        fv: int or float
            قیمتِ اسمیِ اوراق
        pv: int or float
            قیمتِ فعلی
        n: int
            تعدادِ روزهایِ مانده تا سررسید

        Returns
        -------
        yield-to-maturity: float

        Examples
        --------
        >>> from xuk.fixed_incom import YTM
        >>> YTM().zero_coupon_bond(fv=100, pv=73, n=543)
        0.23558667358353835
        """
        n = n / self.year_days

        def eq(val):
            r = val
            return fv / (1 + r) ** n - pv

        return fsolve(eq, 0)[0]
