#from quantlib_sacha.quantlib.bonds.bond import Bond
import pandas as pd
import numpy as np

def fraction(bond):
    dates = np.array(
        [(bond.start_date + pd.DateOffset(months=i * 12 / bond.coupon_frequency)) for i in range(0, bond.maturity * bond.coupon_frequency + 1)]
    )
    start_dates = pd.to_datetime(dates[:-1])
    end_dates = pd.to_datetime(dates[1:])

    day_count = np.array((end_dates - start_dates).days)

    if bond.day_count_convention is None:
        raise Exception("day_count_convention must be set")

    elif bond.day_count_convention == "ACT/ACT":
        return day_count / np.array([((bond.start_date + pd.DateOffset(years=i + 1)) - (bond.start_date + pd.DateOffset(years=i))).days for i in range(0, len(dates) - 1)])
    elif bond.day_count_convention == "ACT/360":
        return day_count / 360
    elif bond.day_count_convention == "ACT/365":
        return day_count / 365
    elif bond.day_count_convention == "30/360":
        day_count = 360 * (end_dates.year - start_dates.year) + 30 * (end_dates.month - start_dates.month) + (end_dates.day - start_dates.day)
        return day_count / 360
    else:
        raise ValueError(f"Unsupported day count: {bond.day_count_convention}")