from dataclasses import dataclass
import polars as pl

__all__ = ["manipulation_cols", "cols"]


@dataclass
class ManipulationCols:
    rename: dict | None
    prefix: str | None
    suffix: str | None
    select: list[str] | None
    drop: list[str] | None


@dataclass
class Strategy:
    covered_call: ManipulationCols
    married_put: ManipulationCols
    bull_call_spread: ManipulationCols
    bear_call_spread: ManipulationCols
    bull_put_spread: ManipulationCols
    bear_put_spread: ManipulationCols


@dataclass
class Cols:
    strategy: Strategy


def manipulation_cols(df: pl.DataFrame, columns: ManipulationCols):
    if columns.rename:
        df = df.rename(columns.rename)
    if columns.prefix:
        df = df.rename({i: f"{columns.prefix}{i}" for i in df.columns})
    if columns.suffix:
        df = df.rename({i: f"{i}{columns.suffix}" for i in df.columns})
    if columns.select:
        df = df.select(columns.select)
    if columns.drop:
        df = df.drop(columns.drop)
    return df


covered_call = ManipulationCols(
    rename={
        "symbol": "writing",
        "bid_price": "writing_at",
        "ua_symbol": "buy_ua",
        "ua_ask_price": "buy_ua_at",
    },
    prefix=None,
    suffix=None,
    select=[
        "writing",
        "writing_at",
        "buy_ua",
        "buy_ua_at",
        "k",
        "t",
        "pct_status",
        "break_even",
        "pct_break_even",
        "max_pot_loss",
        "max_pot_profit",
        "pct_mpp",
        "pct_monthly_mpp",
        "current_profit",
        "pct_cp",
        "pct_monthly_cp",
    ],
    drop=None)

married_put = ManipulationCols(
    rename={
        "symbol": "buy",
        "ask_price": "buy_at",
        "ua_symbol": "buy_ua",
        "ua_ask_price": "buy_ua_at",
    },
    prefix=None,
    suffix=None,
    select=[
        "buy",
        "buy_at",
        "buy_ua",
        "buy_ua_at",
        "k",
        "t",
        "pct_status",
        "break_even",
        "pct_break_even",
        "max_pot_loss",
        "max_pot_profit",
        "pct_mpp",
        "pct_monthly_mpp",
        "current_profit",
        "pct_cp",
        "pct_monthly_cp",
    ],
    drop=None)

bull_call_spread = ManipulationCols(
    rename=None,
    prefix=None,
    suffix=None,
    select=[
        "writing",
        "writing_at",
        "k_w",
        "buy",
        "buy_at",
        "k_b",
        "t",
        "ua_symbol",
        "ua_final",
        "max_pot_loss",
        "max_pot_profit",
        "current_profit",
    ],
    drop=None)

bear_call_spread = ManipulationCols(
    rename=None,
    prefix=None,
    suffix=None,
    select=bull_call_spread.select,
    drop=None)

bull_put_spread = ManipulationCols(
    rename=None,
    prefix=None,
    suffix=None,
    select=bull_call_spread.select,
    drop=None)

bear_put_spread = ManipulationCols(
    rename=None,
    prefix=None,
    suffix=None,
    select=bull_call_spread.select,
    drop=None)

strategy = Strategy(
    covered_call=covered_call,
    married_put=married_put,
    bull_call_spread=bull_call_spread,
    bear_call_spread=bear_call_spread,
    bull_put_spread=bull_put_spread,
    bear_put_spread=bear_put_spread
)

cols = Cols(
    strategy=strategy
)
