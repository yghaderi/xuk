from pydantic import BaseModel
import numpy as np
from scipy.stats import norm


class OptionType(BaseModel):
    call: "call"
    put: "put"


class Pricing:
    def __init__(self):
        self.N = 250
        self.Y = 365

    def black_scholes_merton(
        self,
        s0: float | str,
        k: float | str,
        t: int,
        sigma: float,
        type_: OptionType,
        r: float,
        div: float | int = 0,
    ) -> int:
        """
        .. raw:: html
            <div>
                مدلِ قیمت-گذاریِ بلک-شولز-مرتون برای اختارِ-معامله‌هایِ اروپایی.
            </div>

        :math:`C = N(d_1)S_T-N(d_2)K_e^{-rT}`

        where

        .. line-block::
            :math:`d_1 = \\frac {ln\\frac{S_T}{K}+(r+\\frac {\sigma^2}{2})T}{\sigma\sqrt{T}}`
            :math:`d_2 = d_1 - \sigma\sqrt{T}`
            :math:`C`: call option value
            :math:`S_t`: underlying asset price
            :math:`N`: CDF of the normal distribution
            :math:`K`: strike-price
            :math:`e`: the base of the natural log function, approximately 2.71828
            :math:`r`: risk-free interest rate
            :math:`T`: time to expiration of option, in years
            :math:`ln`: natural logarithm function
            :math:`\sigma`: standard deviation of the annualized continuously compounded rate of return of the underlying asset.

        Parameters
        ----------
        s0: str
            قیمتِ داراییِ پایه
        k: str
            قیمتِ اعمال
        t: str
            تعدادِ روزهایِ مانده تا تاریخِ اعمال
        sigma: float
            انحراف-از-معیارِ روزانه‌یِ داراییِ پایه
        type\_ OptionType, {'call', 'put'}
            * "call": اختیارِ خرید
            * "put": اختیارِ فروش
        r
            نرخِ بهره‌یِ بدونِ ریسک- سالانه
        div: int, default 0
            سودِ تقسیمیِ داراییِ پایه قبل از تاریخِ اعمال

        Returns
        -------
        option value: int
        """
        sigma = sigma * np.sqrt(self.N)
        t = t / self.Y
        s0 = s0 - div / pow((1 + r), t) if type_ == "call" else s0
        d1 = (np.log(s0 / k) + (r + pow(sigma, 2) / 2) * t) / (sigma * np.sqrt(t))
        d2 = d1 - sigma * np.sqrt(t)

        match type_:
            case "call":
                n_d1 = norm.cdf(d1, 0, 1)
                n_d2 = norm.cdf(d2, 0, 1)
                val = s0 * n_d1 - k * np.exp(-r * t) * n_d2
                return max(0, val)
            case "put":
                n_d1 = norm.cdf(-d1, 0, 1)
                n_d2 = norm.cdf(-d2, 0, 1)
                val = k * np.exp(-r * t) * n_d2 - s0 * n_d1
                return max(0, val)
