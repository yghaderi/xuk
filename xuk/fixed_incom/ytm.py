import datetime
from dateutil.relativedelta import relativedelta
from sympy import nsolve, solve, symbols, Sum
from scipy.optimize import fsolve
from tarix import evenly_periods

MONTH_DAYS = 30
YEAR_DAYS = 365


def coupon_bond_ytm(
    fv: int | float,
    pv: int | float,
    coupon_rate: float,
    n: int,
    maturity_date: str,
    start_date: str | None = None,
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
    start_date: str, format "yyyymmdd", "yyyy-mm-dd", "yyyy/mm/dd"
        تاریخِ جلالیِ شروعِ. اگه هیچی پاس داده نشه، پیش-فرض امروزه.
    maturity_date: str, format "yyyymmdd", "yyyy-mm-dd", "yyyy/mm/dd"
        تاریخِ جلالیِ سررسید
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
    >>> from xuk.fixed_incom import coupon_bond_ytm
    >>> coupon_bond_ytm(fv=100, pv=98, coupon_rate=0.09, n=6, maturity_date = "1404-02-18", start_date="1402-08-18")
    0.20562720385247046
    """
    floor_division, modulo = evenly_periods(
        length=n, start=start_date, end=maturity_date
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


def zero_coupon_bond_ytm(fv: int | float, pv: int | float, n: int):
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
    >>> from xuk.fixed_incom import zero_coupon_bond_ytm
    >>> zero_coupon_bond_ytm(fv=100, pv=73, n=543)
    0.23558667358353835
    """
    n = n / YEAR_DAYS

    def eq(val):
        r = val
        return fv / (1 + r) ** n - pv

    return fsolve(eq, 0)[0]
