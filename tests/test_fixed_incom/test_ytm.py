import unittest
from xuk.fixed_incom.ytm import coupon_bond_ytm, zero_coupon_bond_ytm


class TestYTM(unittest.TestCase):
    def test_coupon_bond_ytm(self):
        ytm = coupon_bond_ytm(fv=100, pv=98, coupon_rate=0.09, n=6, maturity_date="1404-02-18", start_date="1402-08-18")
        self.assertEquals(ytm, 0.20562720385247046)

    def test_zero_coupon_bond_ytm(self):
        ytm = zero_coupon_bond_ytm(fv=100, pv=73, n=543)
        self.assertEqual(ytm, 0.23558667358353835)


if __name__ == "__main__":
    unittest.main()
