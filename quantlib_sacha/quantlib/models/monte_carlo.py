from __future__ import annotations

import copy

import numpy as np
from numpy.polynomial import laguerre


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from quantlib_sacha.quantlib.instruments.option import Option

#nouveau push avec nouveau compte
class MonteCarlo:
    def __init__(self, simulations : int, steps : int, seed : int | None = 42):
        self.simulations = simulations
        self.steps = steps
        self.seed = seed

    @staticmethod
    def generate_paths(option : Option, simulations : int, steps : int, seed : int | None):
        if seed is not None:
            np.random.seed(seed)

        paths = np.ones((simulations, steps)) * option.spot
        dt = option.maturity / steps
        Z = np.random.randn(simulations, steps)

        for step in range(1, steps):
            paths[:, step] = paths[:, step - 1] * np.exp(
                (option.rf - option.div_rate - 0.5 * option.volatility ** 2) * dt + option.volatility * np.sqrt(dt) * Z[
                    :,
                    step - 1])
        return paths

    def _longstaff_schwartz(self, option: Option, seed : int | None = None):
        # On utilise le seed passé en argument s'il existe, sinon celui de l'instance
        active_seed = seed if seed is not None else self.seed

        paths = self.generate_paths(option, self.simulations, self.steps, active_seed)
        dt = option.maturity / self.steps
        discount_factor = np.exp(-option.rf * dt)
        #step_exercise_point = np.ones((self.steps, self.simulations))
    
        cashflows = option.payoff(option.option_type, paths[:,-1])
    
        for i in reversed(range(1, self.steps-1)):
            step_exercise_point = np.ones(self.simulations) < 0
            spot_values = paths[:,i]
    
            #prix d'exercice au step[i]
            exercise_values = option.payoff(option.option_type, paths[:,i])
    
            if exercise_values.sum() > 0:
                # On ne régresse que sur les trajectoires dans la monnaie
                itm = exercise_values > 0
    
                # Régression polynomiale : E[continuation | S_t]
                X = spot_values[itm]
                # On normalise X
                X_norm = (X/option.strike).ravel()
                Y = cashflows[itm].ravel()
                coef = laguerre.lagfit(x=X_norm, y=Y, deg=4)
    
                # Approximation de la valeur de continuation
                continuation_values = laguerre.lagval(X_norm, coef).ravel()
                exercise_now = (exercise_values[itm] > continuation_values).ravel()
    
                # Mise à jour des cashflows
                new_cashflows = cashflows.copy()
                itm_indices = np.where(itm)[0]
    
                exercise_now_indices = itm_indices[exercise_now]
                continue_indices = itm_indices[~exercise_now]
    
                # Trajectoires où on exerce : cashflow = payoff immédiat
                new_cashflows[exercise_now_indices] = exercise_values[exercise_now_indices]
                # Trajectoires où on continue : cashflow = cashflow futur actualisé
                new_cashflows[continue_indices] = cashflows[continue_indices] * discount_factor
    
                cashflows = new_cashflows
            else:
                # Aucune trajectoire ITM : on actualise juste
                cashflows = cashflows * discount_factor
    
            #step_exercise_point[itm_indices[exercise_now]] = True
            #exercise_now_matrix[self.steps-i] = step_exercise_point
    
        # 4. Prix = moyenne des cashflows actualisés jusqu'en t=0
        price = np.mean(cashflows) * discount_factor  # actualisation du dernier pas (t=1 -> t=0)
    
        return price #, np.array([paths, exercise_now_matrix.T])

    def price(self, option):
        return self._longstaff_schwartz(option)

    # --- MÉTHODE AUXILIAIRE : PERTURBATION D'UNE OPTION ---
    def _bump_option(self, option: Option, **kwargs) -> Option:
        """Crée une copie de l'option en modifiant certains attributs."""
        opt_copy = copy.copy(option)
        for attr, value in kwargs.items():
            setattr(opt_copy, attr, value)
        return opt_copy

    # --- GRECS PAR DIFFÉRENCES FINIES (BUMPING) ---

    def delta(self, option: Option, dS_pct: float = 0.01) -> float:
        dS = option.spot * dS_pct
        opt_up = self._bump_option(option, spot=option.spot + dS)
        opt_down = self._bump_option(option, spot=option.spot - dS)

        price_up = self._longstaff_schwartz(opt_up)
        price_down = self._longstaff_schwartz(opt_down)

        return (price_up - price_down) / (2 * dS)

    def gamma(self, option: Option, dS_pct: float = 0.01) -> float:
        dS = option.spot * dS_pct
        opt_up = self._bump_option(option, spot=option.spot + dS)
        opt_down = self._bump_option(option, spot=option.spot - dS)

        p_base = self.price(option)
        price_up = self._longstaff_schwartz(opt_up)
        price_down = self._longstaff_schwartz(opt_down)

        return (price_up - 2 * p_base + price_down) / (dS ** 2)

    def vega(self, option: Option, dvol: float = 0.01) -> float:
        opt_up = self._bump_option(
            option, volatility=max(1e-4, option.volatility + dvol)
        )
        opt_down = self._bump_option(
            option, volatility=max(1e-4, option.volatility - dvol)
        )

        price_up = self._longstaff_schwartz(opt_up)
        price_down = self._longstaff_schwartz(opt_down)

        # Retourne le Vega pour 1% (0.01) de variation de vol
        return (price_up - price_down) / (2 * dvol * 100)

    def theta(self, option: Option, dt_days: float = 1.0) -> float:
        dt = dt_days / 365.0
        if option.maturity <= dt:
            raise ValueError("La maturité est trop courte pour calculer Theta.")

        opt_down = self._bump_option(option, maturity=option.maturity - dt)

        p_base = self.price(option)
        price_down = self._longstaff_schwartz(opt_down)

        # Theta journalier
        return (price_down - p_base) / dt_days

    def rho(self, option: Option, dr: float = 0.0001) -> float:
        opt_up = self._bump_option(option, rf=option.rf + dr)
        opt_down = self._bump_option(option, rf=option.rf - dr)

        price_up = self._longstaff_schwartz(opt_up)
        price_down = self._longstaff_schwartz(opt_down)

        # Rho pour 1 bps (0.0001)
        return (price_up - price_down) / (2 * dr * 10000)

