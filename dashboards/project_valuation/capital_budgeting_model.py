"""
Capital Budgeting Model — Helper Functions & Practice Script
==============================================================

This script builds a generic, reusable capital budgeting toolkit in Python,
mirroring the mechanics of the in-class Excel DCF model (pro forma free cash
flow schedule, NPV, IRR, payback period, and a Go/No-Go decision rule).

It is intended as scaffolding/practice for translating a spreadsheet-based
financial model into code — NOT as the deliverable for the assignment itself.
The assumptions used in `tests()` are pulled directly from the in-class Excel
model (volume/price/cost-per-unit based revenue, 3-year term, 20% discount
rate) to validate that the functions reproduce the same outputs as the
spreadsheet. The actual assignment (6-year term, top-down revenue growth,
gross margin, conditional opex, 15.5% WACC, 21% tax rate) is a separate,
graded piece of work and is not implemented in this file.

Functions:
    calculate_dcf        — discounts a single period's cash flow
    pro_forma_cf_schedule — builds the full {period: free cash flow} schedule
    calculate_npv        — sums discounted cash flows into a net present value
    calculate_irr        — solves for the discount rate where NPV = 0 (bisection)
    calculate_payback     — computes the payback period from cumulative cash flows
    is_go                — applies NPV / IRR / Payback decision rules
    tests                — sanity-checks all functions against the class Excel model
"""

import pandas as pd


# HELPER FUNCTIONS
def calculate_dcf(cf: float, rate: float, period: int) -> float:
    """Takes in a single period cash flow and returns the discounted cash flow for that period"""
    return cf / (1 + rate) ** period


# PRO FORMA CASH FLOWS
def pro_forma_cf_schedule(
    volume, ppu, cpu, term, opex, capex, disposal, depex, nwcreq, taxrate
):
    """Takes in project assumptions and returns a dictionary of form {period: free cash flow}"""
    fcf_schedule = {}
    cogs = cpu * volume
    revenue = volume * ppu
    gross_profit = revenue - cogs
    operating_profit = gross_profit - opex - depex
    taxes = operating_profit * taxrate
    nopat = operating_profit - taxes
    operating_cf = nopat + depex

    # Revenue by period: 0 at period 0 (no operations), flat revenue afterwards
    period_revenue = {t: (0 if t == 0 else revenue) for t in range(term + 1)}
    nwc_balance = {
        t: (0 if t == term else nwcreq * period_revenue[t + 1]) for t in range(term + 1)
    }

    for t in range(term + 1):
        prior_balance = nwc_balance[t - 1] if t > 0 else 0
        delta_nwc_cf = -(nwc_balance[t] - prior_balance)

        if t == 0:
            fcf = -capex + delta_nwc_cf
        elif t == term:
            fcf = operating_cf + disposal + delta_nwc_cf
        else:
            fcf = operating_cf + delta_nwc_cf

        fcf_schedule[t] = fcf

    return fcf_schedule


# NET PRESENT VALUE
def calculate_npv(cf_schedule: dict[int, float], discrate: float) -> float:
    """Takes in a dictionary of form {period: free cash flow} and a discount rate,
    and returns the net present value by discounting and summing each periods cash."""
    return sum(
        calculate_dcf(cf, discrate, period) for period, cf in cf_schedule.items()
    )


# INTERNAL RATE OF RETURN
def calculate_irr(cf_schedule, initial_guess=0.05):
    """Takes in a {period: cash_flow} schedule and returns the rate of return as a percentage"""
    low, high = -0.99, 10.0  # rate must be > -100%
    tolerance = 1e-3
    max_iterations = 1000
    for _ in range(max_iterations):
        mid = (low + high) / 2
        npv_at_mid = calculate_npv(cf_schedule, mid)

        if abs(npv_at_mid) < tolerance:
            return mid
        # NPV decreases as rate increases
        if npv_at_mid > 0:
            low = mid
        else:
            high = mid
    # return best estimate as a percentage
    return mid * 100


# PAYBACK PERIOD
def calculate_payback(cf_schedule):
    """Takes in the cash flow schedule and returns the payback period"""
    periods = sorted(cf_schedule.keys())
    cumulative = 0.0
    cumulative_by_period = {}

    for t in periods:
        cumulative += cf_schedule[t]
        cumulative_by_period[t] = cumulative

    # last period where cumulative is negative
    last_neg_period = None
    for t in periods:
        if cumulative_by_period[t] < 0:
            last_neg_period = t
    if last_neg_period is None:
        return 0.0
    if last_neg_period == periods[-1]:
        return float("inf")  # Never recovered within the given term
    next_period = periods[periods.index(last_neg_period) + 1]
    remaining = abs(cumulative_by_period[last_neg_period])
    next_period_cf = cf_schedule[next_period]

    return last_neg_period + remaining / next_period_cf


# TODO:
# GO decision
def is_go(irr, payback_period, management_target, npv, discrate):
    decisions = {"NPV": "No Go", "Payback Period": "No Go", "IRR": "No Go"}
    if npv > 0:
        decisions["NPV"] = "Go"
    if payback_period <= management_target:
        decisions["Payback Period"] = "Go"
    if irr > discrate:
        decisions["IRR"] = "Go"
    return decisions


# Test Helper Function using inputs from class excel model
def tests():
    pro_forma_sched = pro_forma_cf_schedule(
        50000, 4, 2.5, 3, 17430.00, 90000.00, 0, 30000.00, 0.1, 0.21
    )
    npv = calculate_npv(pro_forma_sched, discrate=0.2)
    irr = calculate_irr(pro_forma_sched)
    pb = calculate_payback(pro_forma_sched)
    go = is_go(irr, pb, management_target=2, npv=npv, discrate=0.2)

    print("The Pro Forma cash flows for each period are:", pro_forma_sched)
    print("The Net Present Value is:", npv)
    print("The Internal Rate of Return is:", irr)
    print("The Payback Period is:", pb)
    print("The Decision Rules are as follows:", go)
