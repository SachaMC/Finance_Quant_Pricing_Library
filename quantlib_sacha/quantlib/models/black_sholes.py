from __future__ import annotations

import numpy as np
from scipy.stats import norm
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quantlib_sacha.quantlib.instruments.option import Option
#nouveau push avec nouveau compte


class BlackScholes:

    def _validate_and_get_params(self, option: Option):
        """Valide l'option, calcule le spot ajusté (ex-dividend) ainsi que d1 et d2."""
        if not option.IsEuropean:
            raise ValueError("L'option doit être de type Européen")

        # Ajustement du Spot pour les dividendes discrets
        S = option.spot
        if option.div is not None:
            if not (isinstance(option.div, list) and all(isinstance(t, tuple) and len(t) == 2 for t in option.div)):
                raise TypeError("Les dividendes doivent être une liste de tuples (temps, montant).")

            pv_dividend = sum(
                amount * np.exp(-option.rf * t)
                for t, amount in option.div
                if t <= option.maturity
            )
            S -= pv_dividend

        if S <= 0:
            raise ValueError("Le spot ajusté des dividendes doit être strictly positif.")

        vol_sqrt_T = option.volatility * np.sqrt(option.maturity)

        d1 = (np.log(S / option.strike) + (
                    option.rf - option.div_rate + 0.5 * option.volatility ** 2) * option.maturity) / vol_sqrt_T
        d2 = d1 - vol_sqrt_T

        return S, d1, d2

    def price(self, option: Option) -> float:
        S, d1, d2 = self._validate_and_get_params(option)
        df_rf = np.exp(-option.rf * option.maturity)
        df_q = np.exp(-option.div_rate * option.maturity)

        if option.IsCall:
            return S * df_q * norm.cdf(d1) - option.strike * df_rf * norm.cdf(d2)
        else:
            return option.strike * df_rf * norm.cdf(-d2) - S * df_q * norm.cdf(-d1)

    ## GREEKS

    def delta(self, option: Option) -> float:
        S, d1, _ = self._validate_and_get_params(option)
        df_q = np.exp(-option.div_rate * option.maturity)

        if option.IsCall:
            return df_q * norm.cdf(d1)
        else:
            return df_q * (norm.cdf(d1) - 1.0)

    def gamma(self, option: Option) -> float:
        S, d1, _ = self._validate_and_get_params(option)
        df_q = np.exp(-option.div_rate * option.maturity)
        return df_q * norm.pdf(d1) / (S * option.volatility * np.sqrt(option.maturity))

    def vega(self, option: Option) -> float:
        S, d1, _ = self._validate_and_get_params(option)
        df_q = np.exp(-option.div_rate * option.maturity)
        # Vega pour un changement de 1% (0.01) de volatilité
        return S * df_q * norm.pdf(d1) * np.sqrt(option.maturity) / 100.0

    def theta(self, option: Option) -> float:
        S, d1, d2 = self._validate_and_get_params(option)
        df_rf = np.exp(-option.rf * option.maturity)
        df_q = np.exp(-option.div_rate * option.maturity)

        p1 = -S * option.volatility * df_q * norm.pdf(d1) / (2 * np.sqrt(option.maturity))

        if option.IsCall:
            theta_val = p1 + option.div_rate * S * df_q * norm.cdf(d1) - option.rf * option.strike * df_rf * norm.cdf(
                d2)
        else:
            theta_val = p1 - option.div_rate * S * df_q * norm.cdf(-d1) + option.rf * option.strike * df_rf * norm.cdf(
                -d2)

        return theta_val / 365.0

    def rho(self, option: Option) -> float:
        S, _, d2 = self._validate_and_get_params(option)
        df_rf = np.exp(-option.rf * option.maturity)

        # Rho pour un changement de 1% (0.01) du taux sans risque
        if option.IsCall:
            return option.strike * option.maturity * df_rf * norm.cdf(d2) / 100.0
        else:
            return -option.strike * option.maturity * df_rf * norm.cdf(-d2) / 100.0