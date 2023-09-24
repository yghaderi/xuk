from collections import namedtuple

Cols = namedtuple("Cols", ["covered_call"])
Property = namedtuple("Property", ["rename", "drop", "rep"])

_covered_call = {
    "rename": {"symbol_far": "writing", "buy_price": "writing_at", "ua_symbol_far": "buy_ua",
               "ua_sell_price": "buy_ua_at"},
    "rep": ["symbol_far", "buy_price", "ua_symbol_far", "ua_sell_price", "strike_price", "t", "bs", "pct_status",
            "break_even", "pct_break_even", "max_pot_loss", "max_pot_profit", "pct_mpp", "pct_monthly_mpp",
            "current_profit", "pct_cp", "pct_monthly_cp"],
}

covered_call = Property(
    rename=_covered_call.get("rename"),
    drop=_covered_call.get("drop"),
    rep=_covered_call.get("rep"),
)

cols = Cols(
    covered_call=covered_call
)
