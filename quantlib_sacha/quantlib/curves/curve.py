import numpy as np
from dataclasses import dataclass
import pandas as pd

@dataclass
class Curve:
    curve_data: pd.DataFrame

def interpolate(maturity, matu1, matu2, rate1, rate2):
    a = (float(rate2) - float(rate1)) / (float(matu2) - float(matu1))
    b = float(rate1) - float(matu1) * a
    rate = float(maturity) * a + b
    return rate

class Curve_Interpolation:
    def __init__(self, curve : Curve, maturity, payment_frequency):
        self.curve = curve
        self.maturity = maturity
        self.payment_frequency = payment_frequency

    def yield_curve(self):
        period = np.array([i / self.payment_frequency for i in range (1, self.maturity * self.payment_frequency + 1)])
        rates = np.zeros(len(period))
        i = 0
        compteur = 0
        while compteur <= len(period)-1:
            if period[compteur] == self.curve.curve_data["Maturity"].loc[i]:
                rates[compteur] = float(self.curve.curve_data["Rate"].loc[i])
                i += 1
                compteur += 1
            elif period[compteur] == self.curve.curve_data["Maturity"].loc[i+1]:
                rates[compteur] = float(self.curve.curve_data["Rate"].loc[i+1])
                i += 2
                compteur += 1
            elif period[compteur] == self.curve.curve_data["Maturity"].loc[i+2]:
                rates[compteur] = float(self.curve.curve_data["Rate"].loc[i+2])
                i += 3
                compteur += 1
            elif period[compteur] == self.curve.curve_data["Maturity"].loc[i+3]:
                rates[compteur] = float(self.curve.curve_data["Rate"].loc[i+3])
                i += 4
                compteur += 1
            else:
                rates[compteur] = interpolate(period[compteur],self.curve.curve_data["Maturity"].loc[i], self.curve.curve_data["Maturity"].loc[i+1], self.curve.curve_data["Rate"].loc[i], self.curve.curve_data["Rate"].loc[i+1])
                compteur += 1
        return period, rates

