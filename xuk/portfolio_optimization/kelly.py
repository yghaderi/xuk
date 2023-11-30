import warnings

import pandas as pd
import numpy as np
from numpy.linalg import inv

from sympy import symbols, solve, log, diff
from scipy.optimize import minimize_scalar, newton, minimize
from scipy.integrate import quad
from scipy.stats import norm

warnings.filterwarnings("ignore")


class Kelly:
    def __init__(self, df, time_frame: str, window: int) -> None:
        self.df = df.set_index(
            "date"
        )  # columns = [date,close_ticker_1,close_ticker_2 ...]
        self.time_frame = time_frame
        self.window = window
        self.share, self.odds, self.probability = symbols("share odds probability")
        self.Value = self.probability * log(1 + self.odds * self.share) + (
            1 - self.probability
        ) * log(1 - self.share)
        solve(diff(self.Value, self.share), self.share)

        self.f, self.p = symbols("f p")
        self.y = self.p * log(1 + self.f) + (1 - self.p) * log(1 - self.f)
        solve(diff(self.y, self.f), self.f)

    def calc_return(self):
        return self.df.resample(self.time_frame).last().pct_change().dropna()

    def return_params(self):
        return (
            self.calc_return().TEDPIX.rolling(self.window).agg(["mean", "std"]).dropna()
        )

    def norm_integral(self, f, mean, std):
        val, er = quad(
            lambda s: np.log(1 + f * s) * norm.pdf(s, mean, std),
            mean - 3 * std,
            mean + 3 * std,
        )
        return -val

    def norm_dev_integral(self, f, mean, std):
        val, er = quad(
            lambda s: (s / (1 + f * s)) * norm.pdf(s, mean, std),
            mean - 3 * std,
            mean + 3 * std,
        )
        return val

    def get_kelly_share(self, data):
        solution = minimize_scalar(
            self.norm_integral,
            args=(data["mean"], data["std"]),
            bounds=[0, 2],
            method="bounded",
        )
        return solution.x

    def f_single_asset(self):
        return self.calc_return().assign(
            f=self.return_params().apply(self.get_kelly_share, axis=1)
        )

    # Kelly Rule for Multiple Assets
    def cov_return(self):
        cov = self.calc_return().cov()
        return pd.DataFrame(inv(cov), index=self.df.columns, columns=self.df.columns)

    def kelly_allocation(self):
        return self.calc_return().mean().dot(self.cov_return())

    def kelly_portfolio_return(self, short_selling: bool = False):
        if short_selling:
            kelly_allocation = self.kelly_allocation()
        else:
            kelly_allocation = self.kelly_allocation()
            kelly_allocation[kelly_allocation < 0] = 0
        return (
            self.calc_return()
            .mul(kelly_allocation / kelly_allocation.sum())
            .sum(axis=1)
            .add(1)
            .cumprod()
            .sub(1)
            .to_frame("Kelly")
        )

    def equal_weight_portfolio_return(self):
        kelly_allocation = self.kelly_allocation()
        kelly_allocation[:] = 1 / len(kelly_allocation)
        return (
            self.calc_return()
            .mul(kelly_allocation / kelly_allocation.sum())
            .sum(axis=1)
            .add(1)
            .cumprod()
            .sub(1)
            .to_frame("equal_weight")
        )

    def benchmark_return(self):
        pass
