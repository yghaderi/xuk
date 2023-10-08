class OptionPositionProfit:
    """
    Calculate option position profit.

    Parameters
    ----------
    st
        int, underlying asset price at time of t
    k
        int, strike price
    premium
        int, premium
    qty
        int, quantity
    """

    def __init__(self, st: int, k: int, premium: int, qty: int = 1) -> None:
        self.st = st
        self.k = k
        self.premium = premium
        self.qty = qty

    def long_call(self) -> int:
        """
        Calculate long call position profit.

        Returns
        -------
        int
        """
        return (max(self.st - self.k, 0) - self.premium) * self.qty

    def short_call(self) -> int:
        """Calculate short call position profit.

        Returns
        -------
        int
        """
        return (-max(self.st - self.k, 0) + self.premium) * self.qty

    def long_put(self) -> int:
        """Calculate long put position profit.

        Returns
        -------
        int
        """
        return (max(self.k - self.st, 0) - self.premium) * self.qty

    def short_put(self) -> int:
        """Calculate short call position profit.

        Returns
        -------
        int
        """
        return (-max(self.k - self.st, 0) + self.premium) * self.qty


class AssetPositionProfit:
    """
    Calculate asset position profit.

    Parameters
    ----------
    price
        int, asset price at time of 0
    st
        int, asset price at time of t
    qty
        int, quantity
    """

    def __init__(self, price: int, st: int, qty: int = 1) -> None:
        self.price = price
        self.st = st
        self.qty = qty

    def long(self) -> int:
        """
        Calculate long UA position profit.

        Returns
        -------
        int
        """
        return (self.st - self.price) * self.qty

    def short(self) -> int:
        """
        Calculate short UA position profit.

        Returns
        -------
        int
        """
        return (self.price - self.st) * self.qty
