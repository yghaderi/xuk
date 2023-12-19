
import numpy as np
from numpy.linalg import inv
import polars as pl

from sympy import symbols, solve, log, diff
from scipy.optimize import minimize_scalar
from scipy.integrate import quad
from scipy.stats import norm


share, odds, probability = symbols("share odds probability")
Value = probability * log(1 + odds * share) + (1 - probability) * log(1 - share)
solve(diff(Value, share), share)

f, p = symbols("f p")
y = p * log(1 + f) + (1 - p) * log(1 - f)
solve(diff(y, f), f)


def calc_return(df: pl.DataFrame, time_frame: str):
    return (
        df.group_by_dynamic("date", every=time_frame)
        .agg(pl.exclude("date").last())
        .with_columns(pl.exclude("date").pct_change())
        .drop_nulls()
    )


def return_params(df: pl.DataFrame, window: str):
    return df.rolling("date", period=window).agg(
        pl.exclude("date").mean().name.suffix("_mean"),
        pl.exclude("date").std().name.suffix("_std"),
    )


def norm_integral(f, mean, std):
    val, er = quad(
        lambda s: np.log(1 + f * s) * norm.pdf(s, mean, std),
        mean - 3 * std,
        mean + 3 * std,
    )
    return -val


def norm_dev_integral(f, mean, std):
    val, er = quad(
        lambda s: (s / (1 + f * s)) * norm.pdf(s, mean, std),
        mean - 3 * std,
        mean + 3 * std,
    )
    return val


def get_kelly_share(mean: float, std: float, leverage: float):
    solution = minimize_scalar(
        norm_integral,
        args=(mean, std),
        bounds=[0, leverage],
        method="bounded",
    )
    return solution.x


def f_single_asset(df: pl.DataFrame, leverage: float):
    return df.with_columns(
        f=pl.struct(["mean", "std"]).map_elements(
            lambda x: get_kelly_share(x["mean"], x["std"], leverage)
        )
    )


# Kelly Rule for Multiple Assets
def cov_return(df: pl.DataFrame) -> pl.DataFrame:
    cov = df.to_pandas().cov()
    return pl.from_numpy(inv(cov), schema=df.columns).with_columns(
        pl.Series(df.columns).alias("idx")
    )


def kelly_allocation(df, cr_df):
    cols = df.columns
    cols.remove("date")
    mr = df.select(pl.mean(cols))
    k_alloc = mr.to_numpy().dot(cr_df.drop("idx").to_numpy())
    return pl.from_numpy(k_alloc, schema=cols)


def normalize_kelly_allocation(df: pl.DataFrame):
    return df.with_columns(pl.all() / pl.sum_horizontal(pl.all()))
