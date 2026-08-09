"""
Capital Budgeting Model
========================

Builds a pro forma free cash flow schedule for the project described in the
assignment (revenue growth, gross margin, straight-line depreciation, a
conditional opex step-up, and pegged net working capital), then evaluates it
using NPV, IRR, and payback period against management's decision rules.

Run this file directly to print the test results.
"""

import pandas as pd


# HELPER FUNCTIONS
def calculate_dcf(cf: float, rate: float, period: int) -> float:
    """Takes in a single period cash flow and returns the discounted cash flow for that period"""
    return cf / (1 + rate) ** period


def calculate_revenue_schedule(initial_revenue, growth_rate, term):
    """Returns a {period: revenue} schedule.
    Period 0 = 0 revenue (pre-operations), period 1 = initial revenue,
    and each period afterwards grows by the growth rate"""
    revenue = {0: 0.0}
    for t in range(1, term + 1):
        revenue[t] = initial_revenue if t == 1 else revenue[t - 1] * (1 + growth_rate)
    return revenue


def calculate_gross_profit_schedule(revenue_sched, gross_margin):
    """Takes in revenue schedule and gross margin and applies that margin percentage
    (excluding depreciation) to each period's revenue"""
    return {t: rev * gross_margin for t, rev in revenue_sched.items()}


def calculate_opex_schedule(revenue_sched, base_opex, step_up_threshold, step_up_pct):
    """Returns a {period: opex} schedule.
    Period 0 = no opex (pre-operations).
    In any operating period where revenue exceeds the threshold, opex is increased by
    the step up percentage of the base opex."""
    opex_sched = {}
    for t, rev in revenue_sched.items():
        if t == 0:
            opex_sched[t] = 0.0
        elif rev > step_up_threshold:
            opex_sched[t] = base_opex + step_up_pct * base_opex
        else:
            opex_sched[t] = base_opex
    return opex_sched


def calculate_nwc_schedule(revenue_sched, nwcreq, term):
    """ "Returns the required NWC balance at each period, pegged to the next period's revenue (pre-funding),
    fully unwound (0) at the terminal period"""
    return {
        t: (0.0 if t == term else nwcreq * revenue_sched[t + t])
        for t in range(term + 1)
    }


# PRO FORMA CASH FLOWS
def pro_forma_cf_schedule(
    initial_revenue,
    growth_rate,
    gross_margin,
    term,
    base_opex,
    opex_step_up_threshold,
    opex_step_up_pct,
    capex,
    disposal,
    nwcreq,
    taxrate,
):
    """Takes in project assumptions and returns a dictionary of form {period: free cash flow}.
    Revenue grows from initial revenue at the growth rate, gross margin is a flat % of revenue,
    depreciation is straight-line over the term, and opex steps up in periods where
    revenue exceeds the opex step up threshold"""
    fcf_schedule = {}

    revenue = calculate_revenue_schedule(initial_revenue, growth_rate, term)
    gross_profit = calculate_gross_profit_schedule(revenue, gross_margin)
    depex = capex / term  # straight-line depreciation over the full term
    opex_schedule = calculate_opex_schedule(
        revenue, base_opex, opex_step_up_threshold, opex_step_up_pct
    )
    nwc_balance = calculate_nwc_schedule(revenue, nwcreq, term)

    for t in range(term + 1):
        prior_balance = nwc_balance[t - 1] if t > 0 else 0
        delta_nwc_cf = -(nwc_balance[t] - prior_balance)

        if t == 0:
            operating_cf = 0
        else:
            operating_profit = gross_profit[t] - opex_schedule[t] - depex
            taxes = operating_profit * taxrate
            nopat = operating_profit - taxes
            operating_cf = nopat + depex

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
            return mid  # returns as decimal
        # NPV decreases as rate increases
        if npv_at_mid > 0:
            low = mid
        else:
            high = mid
    # return best estimate as a decimal
    return mid


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
    # Set default decision as no go
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
        initial_revenue=1_000_000_000.00,
        growth_rate=0.075,
        gross_margin=0.40,
        term=6,
        base_opex=200_000_000.00,
        opex_step_up_threshold=1_250_000_000.00,
        opex_step_up_pct=0.10,
        capex=750_000_000.00,
        disposal=0,
        nwcreq=0.10,
        taxrate=0.21,
    )
    npv = calculate_npv(pro_forma_sched, discrate=0.155)
    irr = calculate_irr(pro_forma_sched)
    pb = calculate_payback(pro_forma_sched)
    go = is_go(irr, pb, management_target=3, npv=npv, discrate=0.155)

    print("The Pro Forma cash flows for each period are:", pro_forma_sched)
    print("The Net Present Value is:", npv)
    print("The Internal Rate of Return is:", irr)
    print("The Payback Period is:", pb)
    print("The Decision Rules are as follows:", go)


if __name__ == "__main__":
    tests()
