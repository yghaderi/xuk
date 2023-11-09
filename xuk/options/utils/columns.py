from collections import namedtuple

Cols = namedtuple(
    "Cols",
    [
        "covered_call",
        "married_put",
        "bull_call_spread",
        "bear_call_spread",
        "bull_put_spread",
        "bear_put_spread",
    ],
)
Property = namedtuple("Property", ["rename", "drop", "rep"])

_covered_call = {
    "rename": {
        "symbol": "writing",
        "bid_price": "writing_at",
        "ua_symbol": "buy_ua",
        "ua_ask_price": "buy_ua_at",
    },
    "rep": [
        "symbol",
        "bid_price",
        "ua_symbol",
        "ua_ask_price",
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
}
_married_put = {
    "rename": {
        "symbol": "buy",
        "ask_price": "buy_at",
        "ua_symbol": "buy_ua",
        "ua_ask_price": "buy_ua_at",
    },
    "rep": [
        "symbol",
        "ask_price",
        "ua_symbol",
        "ua_ask_price",
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
}

_bull_call_spread = {
    "rep": [
        "writing",
        "buy",
        "writing_at",
        "buy_at",
        "ua",
        "ua_final",
        "max_pot_loss",
        "max_pot_profit",
        "current_profit",
    ],
}

_bear_call_spread = {
    "rep": [
        "writing",
        "buy",
        "writing_at",
        "buy_at",
        "ua",
        "ua_final",
        "max_pot_loss",
        "max_pot_profit",
        "current_profit",
    ],
}

_bull_put_spread = {
    "rep": [
        "writing",
        "buy",
        "writing_at",
        "buy_at",
        "ua",
        "ua_final",
        "max_pot_loss",
        "max_pot_profit",
        "current_profit",
    ],
}

_bear_put_spread = {
    "rep": [
        "writing",
        "buy",
        "writing_at",
        "buy_at",
        "ua",
        "ua_final",
        "max_pot_loss",
        "max_pot_profit",
        "current_profit",
    ],
}

covered_call = Property(
    rename=_covered_call.get("rename"),
    drop=_covered_call.get("drop"),
    rep=_covered_call.get("rep"),
)
married_put = Property(
    rename=_married_put.get("rename"),
    drop=_married_put.get("drop"),
    rep=_married_put.get("rep"),
)

bull_call_spread = Property(
    rename=_bull_call_spread.get("rename"),
    drop=_bull_call_spread.get("drop"),
    rep=_bull_call_spread.get("rep"),
)

bear_call_spread = Property(
    rename=_bear_call_spread.get("rename"),
    drop=_bear_call_spread.get("drop"),
    rep=_bear_call_spread.get("rep"),
)

bull_put_spread = Property(
    rename=_bull_put_spread.get("rename"),
    drop=_bull_put_spread.get("drop"),
    rep=_bull_put_spread.get("rep"),
)

bear_put_spread = Property(
    rename=_bear_put_spread.get("rename"),
    drop=_bear_put_spread.get("drop"),
    rep=_bear_put_spread.get("rep"),
)
cols = Cols(
    covered_call=covered_call,
    married_put=married_put,
    bull_call_spread=bull_call_spread,
    bear_call_spread=bear_call_spread,
    bull_put_spread=bull_put_spread,
    bear_put_spread=bear_put_spread,
)
