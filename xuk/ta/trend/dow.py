from scipy.signal import argrelextrema
import numpy as np
import polars as pl

__all__ = ["dow"]


def _peak_trough_index(close: np.array, length: int):
    """
    .. raw:: html

        <div dir="rtl">
            کمینه-بیشنه‌هایِ محلی رو پیدا می‌کنه و اندیسِ اون رو برمی‌گردونه.
        </div>

    Parameters
    ---------
    close: np.array
        آرایه‌یِ قیمت
    length: int
        طولِ دوره‌هایِ محلی

    Returns
    -------
    peak_idx: numpy.array
        اندیسِ قله‌ها
    trough_idx: numpy.array
        اندیسِ درَه‌ها
    """
    peak_idx = argrelextrema(close, np.greater_equal, order=length)[0]
    trough_idx = argrelextrema(close, np.less_equal, order=length)[0]
    return peak_idx, trough_idx


def _classification_peak_trough(df: pl.DataFrame):
    """
    .. raw:: html

        <div dir="rtl">
            موقعیتِ قله‌ها و درّه‌ها رو نسبت به هم مقایسه می‌کنه تا به HH, HL, LH, LL نشانه-گذاری بشن.
        </div>

    In hh_lh where True indicate Higher High and False indicate Lower High.
    In ll_hl where True indicate Lower Low and False indicate Higher Low.

    Parameters
    ----------
    df: polars.Dataframe

    Returns
    -------
    polars.DataFrame
    """
    df_peak = df.filter(pl.col("peak").eq(1))
    df_trough = df.filter(pl.col("trough").eq(1))
    df_peak = df_peak.with_columns(
        hh_lh=pl.col("close") > pl.col("close").shift(1)
    ).select(["date", "symbol", "hh_lh"])
    df_trough = df_trough.with_columns(
        ll_hl=pl.col("close") < pl.col("close").shift(1)
    ).select(["date", "symbol", "ll_hl"])
    df = df.join(df_peak, on=["date", "symbol"], how="left")
    df = df.join(df_trough, on=["date", "symbol"], how="left")
    return df


def _recognize_trend(hh_lh: float, ll_hl: float):
    """
    .. raw:: html

        <div dir="rtl">
            بر مبنایِ HH, HL, LH, LL ها و رویکردِ داو، روند نوع روند رو تشخیص میده.
        </div>

    Parameters
    ----------
    hh_lh: float
    ll_hl: float

    Returns
    -------
    trend : int
        1 به معنیِ روندِ صعودی، -1 روندِ نزولی و 0 بی-روند
    """
    if hh_lh:
        if not ll_hl:
            return 1
        return 0
    elif ll_hl:
        if not hh_lh:
            return -1
        return 0
    return 0


def dow(df: pl.DataFrame, length: int):
    """
    .. raw:: html

        <div dir="rtl">
            روند رو بر مبنایِ رویکردِ داو تشخیص میده.
            روندِ صعودی وختیه که HH, HL هایِ متوالی داشته باشیم. روندِ نزولی هم وختیه که LH, LL هایِ متوالی داشته باشیم.
        </div>

    The trend column, where 1 indicates an uptrend, -1 a downtrend, and 0 a trend-less.

    Parameters
    ----------
    df: polars.DataFrame
        شاملِ ستون‌هایِ date, symbol, close
    length: int
        طولِ دوره‌هایِ محلی

    Returns
    -------
    polars.DataFrame
    """
    df_ = pl.DataFrame()
    for name, data in df.group_by("symbol"):
        data = data.with_row_count()
        data = data.with_columns(
            pl.lit(0).alias("peak"),
            pl.lit(0).alias("trough"),
        )
        peak_idx, trough_idx = _peak_trough_index(
            close=data["close"].to_numpy(), length=length
        )
        for i in peak_idx:
            data[int(i), "peak"] = 1
        for i in trough_idx:
            data[int(i), "trough"] = 1
        df_ = pl.concat([df_, data])

    df = _classification_peak_trough(df_)
    df = df.with_columns(
        [
            pl.col("hh_lh")
            .fill_null(strategy="backward")
            .fill_null(strategy="forward"),
            pl.col("ll_hl")
            .fill_null(strategy="backward")
            .fill_null(strategy="forward"),
        ]
    )
    df = df.with_columns(
        pl.struct(["hh_lh", "ll_hl"])
        .map_elements(lambda x: _recognize_trend(hh_lh=x["hh_lh"], ll_hl=x["ll_hl"]))
        .alias("trend")
    )
    return df