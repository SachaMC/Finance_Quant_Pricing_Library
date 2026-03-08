import numpy as np

def payoff(option, type, paths):
    if type == None:
        raise ValueError("Option Type cannot be None")
    elif type not in option.OPTION_TYPES:
        raise ValueError("Option Type must be one of {}".format(option.OPTION_TYPES))
    elif type == "VANILLA":
        return payoff_vanilla(option, paths)
    elif type == "AVERAGE_STRIKE":
        return payoff_average_strike(option, paths)
    elif type == "AVERAGE_PRICE":
        return payoff_average_price(option, paths)
    elif type == "STRIKE_MIN":
        return payoff_strike_min(option, paths)
    elif type == "STRIKE_MAX":
        return payoff_strike_max(option, paths)
    elif type == "DOWN_IN":
        return payoff_down_in(option, paths)
    elif type == "DOWN_OUT":
        return payoff_down_out(option, paths)
    elif type == "UP_IN":
        return payoff_up_in(option, paths)
    elif type == "UP_OUT":
        return payoff_up_out(option, paths)

def generate_paths(option, steps, simulations):
    paths = np.ones((simulations, steps)) * option.spot
    dt = option.maturity / steps
    Z = np.random.randn(simulations, steps)

    for step in range(1, steps):
        paths[:, step] = paths[:, step - 1] * np.exp(
            (option.rf - option.div_rate - 0.5 * option.volatility ** 2) * dt + option.volatility * np.sqrt(dt) * Z[:,
                                                                                                          step - 1])
    return paths
    
def payoff_vanilla(option, paths):
    if option.IsCall:
        payoff = np.maximum(paths[:, -1] - option.strike, 0)
    else:
        payoff = np.maximum(option.strike - paths[:, -1], 0)
    
    return paths, payoff

def payoff_average_strike(option, paths):
    if option.IsCall:
        payoff = np.maximum(paths[:, -1] - np.mean(paths[:, -1], axis=1), 0)
    else:
        payoff = np.maximum(np.mean(paths[:, -1], axis=1) - paths[:, -1], 0)
    return paths, payoff

def payoff_average_price(option, paths):
    if option.IsCall:
        payoff = np.maximum(np.mean(paths[:, -1] - option.strike, axis=1), 0)
    else:
        payoff = np.maximum(option.strike - np.mean(paths[:, -1], axis=1), 0)
    return paths, payoff

def payoff_strike_min(option, paths):
    if option.IsCall:
        payoff = np.maximum(paths[:, -1] - np.min(paths[:, -1], axis=1), 0)
    else:
        payoff = np.maximum(np.min(paths[:, -1], axis=1) - paths[:, -1], 0)

    return paths, payoff

def payoff_strike_max(option, paths):
    if option.IsCall:
        payoff = np.maximum(paths[:, -1] - np.max(paths[:, -1], axis=1), 0)
    else:
        payoff = np.maximum(np.max(paths[:, -1], axis=1) - paths[:, -1], 0)

    return paths, payoff


def payoff_down_in(option, paths):
    touched = np.min(paths, axis=1) <= option.barrier

    if option.IsCall:
        vanilla = np.maximum(paths[:, -1] - option.strike, 0)
    else:
        vanilla = np.maximum(option.strike - paths[:, -1], 0)

    payoff = vanilla * touched
    return paths, payoff


def payoff_down_out(option, paths):
    not_touched = np.min(paths, axis=1) > option.barrier

    if option.IsCall:
        vanilla = np.maximum(paths[:, -1] - option.strike, 0)
    else:
        vanilla = np.maximum(option.strike - paths[:, -1], 0)

    payoff = vanilla * not_touched
    return paths, payoff

def payoff_up_in(option, paths):
    touched = np.max(paths, axis=1) >= option.barrier

    if option.IsCall:
        vanilla = np.maximum(paths[:, -1] - option.strike, 0)
    else:
        vanilla = np.maximum(option.strike - paths[:, -1], 0)

    payoff = vanilla * touched
    return paths, payoff


def payoff_up_out(option, paths):
    not_touched = np.max(paths, axis=1) < option.barrier

    if option.IsCall:
        vanilla = np.maximum(paths[:, -1] - option.strike, 0)
    else:
        vanilla = np.maximum(option.strike - paths[:, -1], 0)

    payoff = vanilla * not_touched
    return paths, payoff