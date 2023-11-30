import polars as pl


def pct_min_max_last(df: pl.DataFrame):
    """
    .. raw::html

        <div dir="rtl">
            بر اساسِ الویتِ کمینه-بیشنه، تغییراتِ قیمت رو در بازه‌یِ داده-شده محاسبه می‌کنه.
             و سپس نسبت به کمینه-بیشنه‌یِ پسین، سطحِ آخرین قیمت رو محاسبه می‌کنه.
        </div>

    Parameters
    ----------
    df polars.DataFrame

    Returns
    -------
    {"pct_mm": float, "pct_last": float}
    """

    mm = (
        df.with_columns(
            max_price=pl.col("close").max(),
            max_date=pl.when(pl.col("close").eq(pl.col("close").max()))
            .then(pl.col("date"))
            .max(),
            min_price=pl.col("close").min(),
            min_date=pl.when(pl.col("close").eq(pl.col("close").min()))
            .then(pl.col("date"))
            .max(),
            last_price=pl.col("close").last(),
        )
        .select(["max_price", "max_date", "min_price", "min_date", "last_price"])
        .row(0, named=True)
    )

    def _round(v: float):
        return round(v * 100, 2)

    if mm["max_date"] > mm["min_date"]:
        pct_mm = _round(mm["max_price"] / mm["min_price"] - 1)
        pct_last = _round(mm["last_price"] / mm["max_price"] - 1)
    else:
        pct_mm = _round(mm["min_price"] / mm["max_price"] - 1)
        pct_last = _round(mm["last_price"] / mm["min_price"] - 1)
    return {"pct_mm": pct_mm, "pct_last": pct_last}
