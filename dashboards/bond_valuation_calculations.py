"""
All numeric and data logic for the Bond Valuation Dashboard.
Takes plain inputs and returns plain python/pandas values for functions.py

Things to calculate:
- Bond value
- Macaulay duration
- Modified duration
"""

import datetime as dt
import numpy as np
import pandas as pd
import math as m

DEFAULT_PAR = 1000

COMPOUNDING_OPTIONS = {
    "Annual": 1,
    "Semiannual": 2,
    "Quarterly": 4,
    "Monthly": 12,
}

DEFAULT_COMPOUNDING = "Semiannual"


def pct_to_decimal(rate_pct):
    return rate_pct / 100


def compounding_to_n(label):
    if label not in COMPOUNDING_OPTIONS:
        raise ValueError(f"Unknown compounding option: {label}")
    return COMPOUNDING_OPTIONS[label]


def _validate_and_prep(payments_per_year, years, yield_rate):
    """Shared validation + period setup for duration calculations."""
    if payments_per_year <= 0:
        raise ValueError("payments per year must be positive")
    if years <= 0:
        raise ValueError("Years must be positive")

    total_periods = years * payments_per_year
    if total_periods != int(total_periods):
        raise ValueError("years * payments per year must be a whole number of periods")
    total_periods = int(total_periods)

    periodic_yield = yield_rate / payments_per_year
    if periodic_yield <= -1:
        raise ValueError("Yield / payments per year cannot be negative")

    return total_periods, periodic_yield


def calc_bond_value(cf, ytm, T, par):
    # Edge case checks:
    if T < 0:
        raise ValueError("Time (periods) cannot be negative")
    if ytm <= -1:
        raise ValueError("Yield to maturity cannot be negative")

    if ytm == 0:
        bond_annuity = cf * T
    else:
        bond_annuity = (cf / ytm) * (1 - (1 / (1 + ytm) ** T))
    bond_par = par / (1 + ytm) ** T
    return bond_annuity + bond_par


def calc_macaulay_duration(par, coupon_rate, yield_rate, years, payments_per_year=1):
    total_periods, periodic_yield = _validate_and_prep(
        payments_per_year, years, yield_rate
    )

    coupon_payment = par * coupon_rate / payments_per_year
    bond_price = 0
    weighted_cf = 0
    for period in range(1, total_periods + 1):
        cf = coupon_payment
        if period == total_periods:
            cf += par
        pv = cf / (1 + periodic_yield) ** period
        bond_price += pv
        weighted_cf += period * pv

    if bond_price == 0:
        raise ZeroDivisionError("Bond Price is 0. Check par and coupon rate inputs")

    return (weighted_cf / bond_price) / payments_per_year


def calc_modified_duration(macualay, ytm, n):
    # Edge case check
    if n <= 0:
        raise ValueError("Compounding frequenct n must be positive")
    if macualay <= 0:
        raise ValueError("Macualay duration must be positive")

    # zero division check
    denom = 1 + (ytm / n)
    if denom == 0:
        raise ZeroDivisionError("Denominator cannot equal 0")

    return macualay / denom


def compute_bond_metrics(coupon_rate, years, ytm, par=DEFAULT_PAR, payments_per_year=2):
    total_periods = years * payments_per_year
    if total_periods != int(total_periods):
        raise ValueError("Total periods must be a whole number")
    total_periods = int(total_periods)

    periodic_coupon = par * coupon_rate / payments_per_year
    periodic_ytm = ytm / payments_per_year

    price = calc_bond_value(periodic_coupon, periodic_ytm, total_periods, par)
    mac_duration = calc_macaulay_duration(
        par, coupon_rate, ytm, years, payments_per_year
    )
    mod_duration = calc_modified_duration(mac_duration, ytm, payments_per_year)

    return {
        "price": price,
        "macaulay_duration": mac_duration,
        "modified_duration": mod_duration,
    }


def build_duration_table(par, coupon_rate, ytm, years, payments_per_year=2):
    total_periods, periodic_yield = _validate_and_prep(payments_per_year, years, ytm)

    coupon_payment = par * coupon_rate / payments_per_year
    rows = []
    bond_price = 0
    for period in range(1, total_periods + 1):
        cf = coupon_payment
        if period == total_periods:
            cf += par
        pv = cf / (1 + periodic_yield) ** period
        bond_price += pv
        rows.append(
            {
                "Period": period,
                "Time (yrs)": period / payments_per_year,
                "Cash Flow": cf,
                "PV of CF": pv,
            }
        )

    if bond_price == 0:
        raise ZeroDivisionError("Par value cannot be negative")

    for row in rows:
        row["Weight"] = row["PV of CF"] / bond_price
        row["Time x Weight"] = row["Time (yrs)"] * row["Weight"]

    df = pd.DataFrame(rows)
    totals = pd.DataFrame(
        [
            {
                "Period": "Total",
                "Time (yrs)": "",
                "Cash Flow": df["Cash Flow"].sum(),
                "PV of CF": df["PV of CF"].sum(),
                "Weight": df["Weight"].sum(),
                "Time x Weight": df["Time x Weight"].sum(),
            }
        ]
    )
    return pd.concat([df, totals], ignore_index=True)


def generate_price_yield_curve(
    coupon_rate,
    years,
    par,
    payments_per_year=2,
    ytm_center=None,
    yield_spread=0.03,
    num_points=61,
):
    if payments_per_year <= 0:
        raise ValueError("payments per year must be positive")
    if years <= 0:
        raise ValueError("Years must be positive")
    if yield_spread <= 0:
        raise ValueError("yield_spread must be positive")
    if num_points < 2:
        raise ValueError("num_points must be at least 2")

    total_periods = years * payments_per_year
    if total_periods != int(total_periods):
        raise ValueError("years * payments per year must be a whole number of periods")
    total_periods = int(total_periods)

    if ytm_center is None:
        ytm_center = coupon_rate

    low = max(ytm_center - yield_spread, -0.999)
    high = ytm_center + yield_spread
    yields = np.linspace(low, high, num_points)

    periodic_coupon = par * coupon_rate / payments_per_year
    prices = np.array(
        [
            calc_bond_value(periodic_coupon, y / payments_per_year, total_periods, par)
            for y in yields
        ]
    )

    return yields, prices
