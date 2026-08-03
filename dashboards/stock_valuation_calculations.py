import pandas as pd

# +/- 2% band around market price is treated as "fairly valued"
DEFAULT_TOLERANCE = 0.02

# Validation helper functions


def validate_ticker(ticker):
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("Stock ticker cannot be blank.")
    cleaned = ticker.strip().upper()
    if not cleaned.replace(".", "").replace("-", "").isalnum():
        raise ValueError("Stock ticker contains unexpected characters.")
    if len(cleaned) > 10:
        raise ValueError("Stock ticker is unexpectedly long — check the input.")
    return cleaned


def validate_dividends(dividends):
    if dividends is None or len(dividends) == 0:
        raise ValueError("At least one forecasted annual dividend is required.")

    cleaned = []
    for i, d in enumerate(dividends, start=1):
        if d is None:
            raise ValueError(f"Forecast year {i} is missing a dividend value.")
        try:
            d = float(d)
        except (TypeError, ValueError):
            raise ValueError(f"Forecast year {i} dividend must be numeric.")
        if d < 0:
            raise ValueError(f"Forecast year {i} dividend cannot be negative.")
        cleaned.append(d)

    if cleaned[-1] == 0:
        raise ValueError(
            "The final forecasted dividend cannot be $0 — the Gordon growth "
            "model needs a positive final-year dividend to project a terminal value."
        )

    return cleaned


def validate_rates(discount_rate, terminal_growth_rate):
    if discount_rate is None:
        raise ValueError("Discount rate is required.")
    if terminal_growth_rate is None:
        raise ValueError("Terminal growth rate is required.")
    if discount_rate <= -1:
        raise ValueError("Discount rate cannot be less than or equal to -100%.")
    if terminal_growth_rate <= -1:
        raise ValueError("Terminal growth rate cannot be less than or equal to -100%.")
    if discount_rate <= terminal_growth_rate:
        raise ValueError(
            "Discount rate must be greater than the terminal growth rate, "
            "otherwise the Gordon growth model produces a negative or "
            "infinite terminal value."
        )


def validate_months_to_first_dividend(months):
    if months is None:
        raise ValueError("Months to first dividend is required.")
    try:
        months = float(months)
    except (TypeError, ValueError):
        raise ValueError("Months to first dividend must be numeric.")
    if not (0 < months <= 12):
        raise ValueError(
            "Months to first dividend must be greater than 0 and no more than 12 "
            "(use 12 when the valuation date falls exactly on a fiscal year end)."
        )
    return months


def validate_market_price(price):
    if price is None:
        raise ValueError("Current market price is required.")
    try:
        price = float(price)
    except (TypeError, ValueError):
        raise ValueError("Current market price must be numeric.")
    if price <= 0:
        raise ValueError("Current market price must be positive.")
    return price


# Core math functions
def calc_dividend_timeline(months_to_first_dividend, num_dividends):
    if num_dividends <= 0:
        raise ValueError("There must be at least one forecasted dividend.")
    t1 = months_to_first_dividend / 12
    return [t1 + i for i in range(num_dividends)]


def calc_prorated_first_cash_flow(first_dividend, months_to_first_dividend):
    fraction = months_to_first_dividend / 12
    return first_dividend * fraction


def calc_terminal_value(last_dividend, discount_rate, terminal_growth_rate):
    denom = discount_rate - terminal_growth_rate
    if denom <= 0:
        raise ZeroDivisionError(
            "Discount rate minus terminal growth rate must be positive."
        )
    return last_dividend * (1 + terminal_growth_rate) / denom


def build_stock_cash_flow_table(
    dividends, discount_rate, terminal_growth_rate, months_to_first_dividend
):
    n = len(dividends)
    times = calc_dividend_timeline(months_to_first_dividend, n)

    cash_flows = list(dividends)
    cash_flows[0] = calc_prorated_first_cash_flow(
        dividends[0], months_to_first_dividend
    )

    rows = []
    for i in range(n):
        t = times[i]
        cf = cash_flows[i]
        pv = cf / (1 + discount_rate) ** t
        rows.append(
            {
                "Period": i + 1,
                "Time (yrs)": round(t, 4),
                "Forecasted Dividend": dividends[i],
                "Cash Flow Used": cf,
                "PV of Cash Flow": pv,
            }
        )

    last_dividend = dividends[-1]
    terminal_value = calc_terminal_value(
        last_dividend, discount_rate, terminal_growth_rate
    )
    t_n = times[-1]
    pv_terminal = terminal_value / (1 + discount_rate) ** t_n

    rows.append(
        {
            "Period": "Terminal Value",
            "Time (yrs)": round(t_n, 4),
            "Forecasted Dividend": "",
            "Cash Flow Used": terminal_value,
            "PV of Cash Flow": pv_terminal,
        }
    )

    df = pd.DataFrame(rows)
    intrinsic_value = df["PV of Cash Flow"].sum()
    return df, intrinsic_value, terminal_value


def make_recommendation(intrinsic_value, market_price, tolerance=DEFAULT_TOLERANCE):
    if market_price <= 0:
        raise ValueError("Current market price must be positive.")

    diff_pct = (intrinsic_value - market_price) / market_price

    if diff_pct > tolerance:
        recommendation = "BUY"
    elif diff_pct < -tolerance:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"

    return recommendation, diff_pct


def compute_stock_valuation(
    ticker,
    dividends,
    terminal_growth_rate,
    discount_rate,
    market_price,
    months_to_first_dividend,
):
    ticker = validate_ticker(ticker)
    dividends = validate_dividends(dividends)
    validate_rates(discount_rate, terminal_growth_rate)
    months_to_first_dividend = validate_months_to_first_dividend(
        months_to_first_dividend
    )
    market_price = validate_market_price(market_price)

    df, intrinsic_value, terminal_value = build_stock_cash_flow_table(
        dividends, discount_rate, terminal_growth_rate, months_to_first_dividend
    )

    recommendation, diff_pct = make_recommendation(intrinsic_value, market_price)

    return {
        "ticker": ticker,
        "intrinsic_value": intrinsic_value,
        "terminal_value": terminal_value,
        "market_price": market_price,
        "recommendation": recommendation,
        "diff_pct": diff_pct,
        "cash_flow_table": df,
    }
