# bond.py
from dataclasses import dataclass
from quantlib_sacha.quantlib.utils.fraction import fraction
import numpy as np
import pandas as pd
import scipy.optimize as optimize

@dataclass
class Bond:
    notional: float
    start_date: pd.Timestamp
    maturity: int
    coupon_type: str
    coupon_rate: float
    spread: float
    coupon_frequency: int
    reimbursement_price: float
    day_count_convention: str
    
    def day_count_fraction(self):
        return fraction(self)

    def pricer(self, rates_curve):
        dates = np.array([(self.start_date + pd.DateOffset(years=i)).strftime("%Y-%m-%d") for i in range (0, self.maturity * self.coupon_frequency + 1)])

        start_dates = dates[:-1]
        end_dates = dates[1:]

        period = np.array([i/self.coupon_frequency for i in range(1, self.maturity * self.coupon_frequency + 1)])

        if self.coupon_type == "ZC":
            coupon = np.zeros(len(period))
            coupon[-1] += self.reimbursement_price

        elif self.coupon_type == "FIXED":
            coupon = np.ones(len(period)) * self.notional * self.coupon_rate/self.coupon_frequency #self.day_count_fraction()()
            coupon[-1] += self.reimbursement_price
        elif self.coupon_type == "FLOAT":
            coupon = self.notional * (rates_curve + self.spread) * self.day_count_fraction()
            coupon[-1] += self.reimbursement_price

        DF = np.array([1/(1 + rates_curve[i]) ** float(np.cumsum(self.day_count_fraction())[i]) for i in range (len(period))])
        price = coupon @ DF
        return start_dates, end_dates, period, coupon, rates_curve, DF, price

    def yield_to_maturity(self, rates_curve):
        start_dates, end_dates, period, coupon, rates_curve, DF, price = self.pricer(rates_curve)
        ytm = lambda t : np.sum(coupon / (1+t)**period) - price
        return optimize.newton(ytm, 0.03)


    def duration(self, rates_curve):
        start_dates, end_dates, period, coupon, rates_curve, DF, price = self.pricer(rates_curve)
        a = (coupon * period) @ DF
        b = price
        return a/b

    def sensitivity(self, rates_curve):
        return self.duration(rates_curve)/(1+self.yield_to_maturity(rates_curve))

    def convexity(self, rates_curve):
        start_dates, end_dates, period, coupon, rates_curve, DF, price = self.pricer(rates_curve)
        t = np.cumsum(self.day_count_fraction())
        t_1 = np.cumsum(self.day_count_fraction()) + self.day_count_fraction()
        a = self.yield_to_maturity(rates_curve)
        b = (coupon * t * t_1) @ (1/(1+a) ** t)
        c = price
        return b / (c * (1 + a)**2)


    def schedule(self, rates_curve):
        start_dates, end_dates, period, coupon, rates, DF, price = self.pricer(rates_curve)
        df = pd.DataFrame(columns = ["Start_Dates", "End_Dates", "Period","Rates","DF", "Coupon", "Price"])
        df["Start_Dates"] = start_dates
        df["End_Dates"] = end_dates
        df["Period"] = period
        df["Coupon"] = coupon
        df["Rates"] = rates
        df["DF"] = DF
        df.loc[0, "Price"] = price
        df.loc[0, "YTM"] = self.yield_to_maturity(rates_curve)
        df.loc[0, "Duration"] = self.duration(rates_curve)
        df.loc[0, "Sensitivity"] = self.sensitivity(rates_curve)
        df.loc[0, "Convexity"] = self.convexity(rates_curve)
        return df


