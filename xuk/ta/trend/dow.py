from scipy.signal import argrelextrema
import numpy as np
import polars as pl


def _peak_trough_index(price: np.array, length: int):
    """
    .. raw:: html

        <div dir="rtl">
            کمینه-بیشنه‌هایِ محلی رو پیدا می‌کنه و اندیسِ اون رو برمی‌گردونه.
        </div>

    Parameters
    ---------
    price: np.array
        آرایه‌یِ قیمت
    order: int
        طولِ دوره‌هایِ محلی

    Returns
    -------
    peak_idx: list
        اندیسِ قله‌ها
    trough_idx
        اندیسِ درَه‌ها
    """
    peak_idx = argrelextrema(price, np.greater_equal, order=length)[0]
    trough_idx = argrelextrema(price, np.less_equal, order=length)[0]
    return peak_idx, trough_idx


def _separation_peak_trough(df):
    """
    It compares the position of the peak and trough compared to the previous one.
    In hh_lh where True indicate Higher High and False indicate Lower High.
    In ll_hl where True indicate Lower Low and False indicate Higher Low.
    :return: hh_lh and ll_hl columns.
    """
    df_peak = df.filter(pl.col("peak").eq(1))
    df_trough = df.filter(pl.col("trough").eq(1))
    df_peak = df_peak.with_columns(
        hh_lh=pl.col("price") > pl.col("price").shift(1)
    ).select(["date", "symbol", "hh_lh"])
    df_trough = df_trough.with_columns(
        ll_hl=pl.col("price") < pl.col("price").shift(1)
    ).select(["date", "symbol", "ll_hl"])
    df = df.join(df_peak, on=["date", "symbol"], how="left")
    df = df.join(df_trough, on=["date", "symbol"], how="left")
    return df


def _recognize_trend(hh_lh, ll_hl):
    if hh_lh:
        if not ll_hl:
            return 1
        return 0
    elif ll_hl:
        if not hh_lh:
            return -1
        return 0
    return 0


def dow_trend(df: pl.DataFrame, length: int):
    """
    An uptrend is defined primarily as successively higher peaks and troughs.
    A downtrend is defined as successively lower peaks and troughs.
    :return: The trend column, where 1 indicates an uptrend, -1 a downtrend, and 0 a trend-less.
    """
    df_ = pl.DataFrame()
    for name, data in df.group_by("symbol"):
        data = data.with_row_count()
        data = data.with_columns(
            pl.lit(0).alias("peak"),
            pl.lit(0).alias("trough"),
        )
        peak_idx, trough_idx = _peak_trough_index(
            price=data["price"].to_numpy(), length=length
        )
        for i in peak_idx:
            data[int(i), "peak"] = 1
        for i in trough_idx:
            data[int(i), "trough"] = 1
        df_ = pl.concat([df_, data])

    df = _separation_peak_trough(df_)
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
