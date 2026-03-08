
import numpy as np
from numpy.polynomial import laguerre
from quantlib_sacha.quantlib.options._payoffs import payoff, generate_paths


def longstaff_schwartz(option, simulations, steps):
    paths = generate_paths(option, simulations, steps)
    discount_factor = discount_factor = np.exp(-self.rf * dt)

    cashflows = payoff(option, paths)

    for i in reversed(range(1, steps-1)):
        step_exercise_point = np.ones(simulations) < 0
        spot_values = paths[:,i]
        #prix d'exercice au step[i]
        exercise_values = payoff(option, paths[:,i])

        if exercise_values.sum() > 0:
            # On ne régresse que sur les trajectoires dans la monnaie
            itm = exercise_values > 0

            # Régression polynomiale : E[continuation | S_t]
            X = spot_values[itm]
            # On normalise X
            X_norm = X/option.strike
            Y = cashflows[itm]
            coef = laguerre.lagfit(x=X_norm, y=Y, deg=4)

            # Approximation de la valeur de continuation
            continuation_values = laguerre.lagval(X_norm, coef)
            exercise_now = exercise_values[itm] > continuation_values

            # Mise à jour des cashflows
            new_cashflows = cashflows.copy()
            itm_indices = np.where(itm)[0]

            # Trajectoires où on exerce : cashflow = payoff immédiat
            new_cashflows[itm_indices[exercise_now]] = exercise_values[itm][exercise_now]
            # Trajectoires où on continue : cashflow = cashflow futur actualisé
            new_cashflows[itm_indices[~exercise_now]] = cashflows[itm_indices[~exercise_now]] * discount_factor

            cashflows = new_cashflows
        else:
            # Aucune trajectoire ITM : on actualise juste
            cashflows = cashflows * discount_factor

        step_exercise_point[itm_indices[exercise_now]] = True
        exercise_now_matrix[steps-i] = step_exercise_point
    # 4. Prix = moyenne des cashflows actualisés jusqu'en t=0
    price = np.mean(cashflows) * discount_factor  # actualisation du dernier pas (t=1 -> t=0)

    return price, np.array([paths, exercise_now_matrix.T])
