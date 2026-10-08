from __future__ import annotations

from dataclasses import dataclass

import scipy.stats as stats
from matplotlib import pyplot as plt

from quantlib_sacha.quantlib.models.black_sholes import BlackScholes
from quantlib_sacha.quantlib.models.monte_carlo import MonteCarlo
from typing import ClassVar
import numpy as np
#nouveau push avec nouveau compte

@dataclass
class Option:
    spot: float  # spot price
    strike: float # strike price
    rf: float  # risk-free rate
    div_rate: float  # dividend rate
    volatility: float# volatility
    maturity: float  # time to maturity in years
    IsCall: bool  # True for call, False for put
    IsEuropean: bool  # True for European's option, False for American's option
    option_type: str
    barrier: float
    div: list[tuple[float, float]]

    def price(self, simulations=None, steps=None):
        if self.IsEuropean == True:
            return BlackScholes().price(option=self)
        elif steps == None or simulations == None:
            raise TypeError("American Option need steps and simulations to be priced")
        else:
            return MonteCarlo(simulations, steps).price(self)

    OPTION_TYPES: ClassVar[list[str]] = [
        "VANILLA",
        "AVERAGE_STRIKE",
        "AVERAGE_PRICE",
        "STRIKE_MIN",
        "STRIKE_MAX",
        "DOWN_IN",
        "DOWN_OUT",
        "UP_IN",
        "UP_OUT"]

    def delta(self, simulations=None, steps=None):
        if self.IsEuropean == True:
            return BlackScholes().delta(self)
        elif steps == None or simulations == None:
            raise TypeError("American Option need steps and simulations to be priced")
        else:
            return MonteCarlo(steps, simulations).delta(self)

    def gamma(self, simulations=None, steps=None):
        if self.IsEuropean == True:
            return BlackScholes().gamma(self)
        elif steps == None or simulations == None:
            raise TypeError("American Option need steps and simulations to be priced")
        else:
            return MonteCarlo(steps, simulations).gamma(self)

    def theta(self, simulations=None, steps=None):
        if self.IsEuropean == True:
            return BlackScholes().theta(self)
        elif steps == None or simulations == None:
            raise TypeError("American Option need steps and simulations to be priced")
        else:
            return MonteCarlo(steps, simulations).theta(self)

    def rho(self, simulations=None, steps=None):
        if self.IsEuropean == True:
            return BlackScholes().rho(self)
        elif steps == None or simulations == None:
            raise TypeError("American Option need steps and simulations to be priced")
        else:
            return MonteCarlo(steps, simulations).rho(self)

    def vega(self, simulations=None, steps=None):
        if self.IsEuropean == True:
            return BlackScholes().vega(self)
        elif steps == None or simulations == None:
            raise TypeError("American Option need steps and simulations to be priced")
        else:
            return MonteCarlo(steps, simulations).vega(self)


    def plot_greeks(self, greek_name):
        if self.IsEuropean == False:
            raise ValueError("L'option doit être de type Européen")
        option_spot = self.spot
        X = np.linspace(0.3 * option_spot, 1.7 * option_spot, 100)
        Y = np.zeros(len(X))
        for i in range(len(X)):
            self.S = X[i]
            if greek_name == "delta":
                Y[i] = self.delta()
            elif greek_name == "gamma":
                Y[i] = self.gamma()
            elif greek_name == "vega":
                Y[i] = self.vega()
            elif greek_name == "theta":
                Y[i] = self.theta()
            elif greek_name == "rho":
                Y[i] = self.rho()
        self.S = option_spot
        plt.plot(X, Y)
        plt.xlabel('Spot Price')
        plt.ylabel(greek_name)
        plt.title(greek_name + ' vs Spot Price')
        plt.show()

    ## IMPLIED VOLATILITY

    def implied_vol(self, price_market):
        if self.IsEuropean == False:
            raise ValueError("L'option doit être de type Européen")
        if self.div != None:
            try:
                if isinstance(self.div, list) and all(isinstance(t, tuple) for t in self.div):
                    None
                else:
                    print("Erreur : Vous devez entrer une liste de tuples.")
            except (SyntaxError, ValueError):
                print("Erreur : Format invalide.")
            PV_div = 0
            for div in self.div:
                if div[0] <= self.T:
                    PV_div += div[1] * np.exp(-self.r * div[0])
            S = self.S - PV_div
        else:
            S = self.S








    def payoff(self, type, paths):
        if type == None:
            raise ValueError("Option Type cannot be None")
        elif type not in self.OPTION_TYPES:
            raise ValueError("Option Type must be one of {}".format(self.OPTION_TYPES))
        elif type == "VANILLA":
            return self.payoff_vanilla(paths)
        elif type == "AVERAGE_STRIKE":
            return self.payoff_average_strike(paths)
        elif type == "AVERAGE_PRICE":
            return self.payoff_average_price(paths)
        elif type == "STRIKE_MIN":
            return self.payoff_strike_min(paths)
        elif type == "STRIKE_MAX":
            return self.payoff_strike_max(paths)
        elif type == "DOWN_IN":
            return self.payoff_down_in(paths)
        elif type == "DOWN_OUT":
            return self.payoff_down_out(paths)
        elif type == "UP_IN":
            return self.payoff_up_in(paths)
        elif type == "UP_OUT":
            return self.payoff_up_out(paths)


    def payoff_vanilla(self, paths_last):
        if self.IsCall:
            payoff = np.maximum(paths_last - self.strike, 0)
        else:
            payoff = np.maximum(self.strike - paths_last, 0)

        return payoff

    def payoff_average_strike(self, paths_last):
        if self.IsCall:
            payoff = np.maximum(paths_last - np.mean(paths_last, axis=1), 0)
        else:
            payoff = np.maximum(np.mean(paths_last, axis=1) - paths_last, 0)
        return payoff

    def payoff_average_price(self, paths_last):
        if self.IsCall:
            payoff = np.maximum(np.mean(paths_last - self.strike, axis=1), 0)
        else:
            payoff = np.maximum(self.strike - np.mean(paths_last, axis=1), 0)
        return payoff

    def payoff_strike_min(self, paths_last):
        if self.IsCall:
            payoff = np.maximum(paths_last - np.min(paths_last, axis=1), 0)
        else:
            payoff = np.maximum(np.min(paths_last, axis=1) - paths_last, 0)

        return payoff

    def payoff_strike_max(self, paths_last):
        if self.IsCall:
            payoff = np.maximum(paths_last - np.max(paths_last, axis=1), 0)
        else:
            payoff = np.maximum(np.max(paths_last, axis=1) - paths_last, 0)

        return payoff

    def payoff_down_in(self, paths_last):
        touched = np.min(paths_last, axis=1) <= self.barrier

        if self.IsCall:
            vanilla = np.maximum(paths_last - self.strike, 0)
        else:
            vanilla = np.maximum(self.strike - paths_last, 0)

        payoff = vanilla * touched
        return payoff

    def payoff_down_out(self, paths_last):
        not_touched = np.min(paths_last, axis=1) > self.barrier

        if self.IsCall:
            vanilla = np.maximum(paths_last - self.strike, 0)
        else:
            vanilla = np.maximum(self.strike - paths_last, 0)

        payoff = vanilla * not_touched
        return payoff

    def payoff_up_in(self, paths_last):
        touched = np.max(paths_last, axis=1) >= self.barrier

        if self.IsCall:
            vanilla = np.maximum(paths_last - self.strike, 0)
        else:
            vanilla = np.maximum(self.strike - paths_last, 0)

        payoff = vanilla * touched
        return payoff

    def payoff_up_out(self, paths_last):
        not_touched = np.max(paths_last, axis=1) < self.barrier

        if self.IsCall:
            vanilla = np.maximum(paths_last - self.strike, 0)
        else:
            vanilla = np.maximum(self.strike - paths_last, 0)

        payoff = vanilla * not_touched
        return payoff