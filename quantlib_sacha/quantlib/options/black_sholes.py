from dataclasses import dataclass

def price(option):
    if option.IsEuropean == False:
        raise ValueError("L'option doit être de type Européen")
    if option.Div != None:
        try:
            if isinstance(option.Div, list) and all(isinstance(t, tuple) for t in option.Div):
                None
            else:
                print("Erreur : Vous devez entrer une liste de tuples.")
        except (SyntaxError, ValueError):
            print("Erreur : Format invalide.")
        PV_div = 0
        for div in option.Div:
            if div[0] <= option.T:
                PV_div += div[1] * np.exp(-option.r * div[0])
        S = option.S - PV_div
    else:
        S = option.S
    d1 = (np.log(S / option.K) + (option.r - option.q + 0.5 * option.vol ** 2) * option.T) / (option.vol * np.sqrt(option.T))
    d2 = d1 - option.vol * np.sqrt(option.T)
    if option.IsCall:
        price = S * np.exp(-option.q * option.T) * norm.cdf(d1) - option.K * np.exp(-option.r * option.T) * norm.cdf(d2)
    else:
        price = option.K * np.exp(-option.r * option.T) * norm.cdf(-d2) - S * np.exp(-option.q * option.T) * norm.cdf(-d1)
    return price

## GREEKS

def delta(option):
    if option.IsEuropean == False:
        raise ValueError("L'option doit être de type Européen")
    if option.Div != None:
        try:
            if isinstance(option.Div, list) and all(isinstance(t, tuple) for t in option.Div):
                None
            else:
                print("Erreur : Vous devez entrer une liste de tuples.")
        except (SyntaxError, ValueError):
            print("Erreur : Format invalide.")
        PV_div = 0
        for div in option.Div:
            if div[0] <= option.T:
                PV_div += div[1] * np.exp(-option.r * div[0])
        S = option.S - PV_div
    else:
        S = option.S
    d1 = (np.log(S / option.K) + (option.r - option.q + 0.5 * option.vol ** 2) * option.T) / (option.vol * np.sqrt(option.T))
    if option.IsCall:
        delta = np.exp(-option.q * option.T) * norm.cdf(d1)
    else:
        delta = np.exp(-option.q * option.T) * (norm.cdf(d1) - 1)
    return delta

def gamma(option):
    if option.IsEuropean == False:
        raise ValueError("L'option doit être de type Européen")
    if option.Div != None:
        try:
            if isinstance(option.Div, list) and all(isinstance(t, tuple) for t in option.Div):
                None
            else:
                print("Erreur : Vous devez entrer une liste de tuples.")
        except (SyntaxError, ValueError):
            print("Erreur : Format invalide.")
        PV_div = 0
        for div in option.Div:
            if div[0] <= option.T:
                PV_div += div[1] * np.exp(-option.r * div[0])
        S = option.S - PV_div
    else:
        S = option.S
    d1 = (np.log(S / option.K) + (option.r - option.q + 0.5 * option.vol ** 2) * option.T) / (option.vol * np.sqrt(option.T))
    gamma = np.exp(-option.q * option.T) * norm.pdf(d1) / (S * option.vol * np.sqrt(option.T))
    return gamma

def vega(option):
    if option.IsEuropean == False:
        raise ValueError("L'option doit être de type Européen")
    if option.Div != None:
        try:
            if isinstance(option.Div, list) and all(isinstance(t, tuple) for t in option.Div):
                None
            else:
                print("Erreur : Vous devez entrer une liste de tuples.")
        except (SyntaxError, ValueError):
            print("Erreur : Format invalide.")
        PV_div = 0
        for div in option.Div:
            if div[0] <= option.T:
                PV_div += div[1] * np.exp(-option.r * div[0])
        S = option.S - PV_div
    else:
        S = option.S
    d1 = (np.log(S / option.K) + (option.r - option.q + 0.5 * option.vol ** 2) * option.T) / (option.vol * np.sqrt(option.T))
    vega = S * np.exp(-option.q * option.T) * norm.pdf(d1) * np.sqrt(option.T) / 100
    return vega

def theta(option):
    if option.IsEuropean == False:
        raise ValueError("L'option doit être de type Européen")
    if option.Div != None:
        try:
            if isinstance(option.Div, list) and all(isinstance(t, tuple) for t in option.Div):
                None
            else:
                print("Erreur : Vous devez entrer une liste de tuples.")
        except (SyntaxError, ValueError):
            print("Erreur : Format invalide.")
        PV_div = 0
        for div in option.Div:
            if div[0] <= option.T:
                PV_div += div[1] * np.exp(-option.r * div[0])
        S = option.S - PV_div
    else:
        S = option.S
    d1 = (np.log(S / option.K) + (option.r - option.q + 0.5 * option.vol ** 2) * option.T) / (option.vol * np.sqrt(option.T))
    d2 = d1 - option.vol * np.sqrt(option.T)
    if option.IsCall:
        theta = (-S * option.vol * np.exp(-option.q * option.T) * norm.pdf(d1) / (
                    2 * np.sqrt(option.T)) + option.q * S * np.exp(-option.q * option.T) * norm.cdf(
            d1) - option.r * option.K * np.exp(-option.r * option.T) * norm.cdf(d2)) / 365
    else:
        theta = (-S * option.vol * np.exp(-option.q * option.T) * norm.pdf(d1) / (
                    2 * np.sqrt(option.T)) - option.q * S * np.exp(-option.q * option.T) * norm.cdf(
            -d1) + option.r * option.K * np.exp(-option.r * option.T) * norm.cdf(-d2)) / 365
    return theta

def rho(option):
    if option.IsEuropean == False:
        raise ValueError("L'option doit être de type Européen")
    if option.Div != None:
        try:
            if isinstance(option.Div, list) and all(isinstance(t, tuple) for t in option.Div):
                None
            else:
                print("Erreur : Vous devez entrer une liste de tuples.")
        except (SyntaxError, ValueError):
            print("Erreur : Format invalide.")
        PV_div = 0
        for div in option.Div:
            if div[0] <= option.T:
                PV_div += div[1] * np.exp(-option.r * div[0])
        S = option.S - PV_div
    else:
        S = option.S
    d1 = (np.log(S / option.K) + (option.r - option.q + 0.5 * option.vol ** 2) * option.T) / (option.vol * np.sqrt(option.T))
    d2 = d1 - option.vol * np.sqrt(option.T)
    if option.IsCall:
        rho = option.K * option.T * np.exp(-option.r * option.T) * norm.cdf(d2) / 100
    else:
        rho = -option.K * option.T * np.exp(-option.r * option.T) * norm.cdf(-d2) / 100
    return rho
