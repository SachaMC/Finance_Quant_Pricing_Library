from dataclasses import dataclass
import quantlib_sacha.quantlib.options.black_sholes as black_sholes
import quantlib_sacha.quantlib.options.binomial_tree as binomial_tree
import quantlib_sacha.quantlib.options.monte_carlo as monte_carlo

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
    div: list(tuple)  # Veuillez entrez les dividendes dans une liste de tuples. Ex:[(1, 50), (2,50)...(Maturité en années, Montant en euros]


    def pricer(self):
        if self.IsEuropean == True:
            return black_sholes.price(self)
        else:
            return binomial_tree.price(self)

    def delta(self):
        if self.IsEuropean == True:
            return black_sholes.delta(self)
        else:
            return .delta(self)

    def gamma(self):
        if self.IsEuropean == True:
            return black_sholes.gamma(self)
        else:
            return .delta(self)

    def vega(self):
        if self.IsEuropean == True:
            return black_sholes.vega(self)
        else:
            return .delta(self)

    def theta(self):
        if self.IsEuropean == True:
            return black_sholes.theta(self)
        else:
            return .theta(self)


    def plot_greeks(self, greek_name):
        if self.IsEuropean == False:
            raise ValueError("L'option doit être de type Européen")
        option_spot = self.S
        X = np.linspace(0.3 * self.S, 1.7 * self.S, 100)
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
        if self.Div != None:
            try:
                if isinstance(self.Div, list) and all(isinstance(t, tuple) for t in self.Div):
                    None
                else:
                    print("Erreur : Vous devez entrer une liste de tuples.")
            except (SyntaxError, ValueError):
                print("Erreur : Format invalide.")
            PV_div = 0
            for div in self.Div:
                if div[0] <= self.T:
                    PV_div += div[1] * np.exp(-self.r * div[0])
            S = self.S - PV_div
        else:
            S = self.S

        def BSM_IV(vol):
            d1 = (np.log(S / self.K) + (self.r - self.q + 0.5 * vol ** 2) * self.T) / (vol * np.sqrt(self.T))
            d2 = d1 - vol * np.sqrt(self.T)
            if self.IsCall:
                price = S * np.exp(-self.q * self.T) * norm.cdf(d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
            else:
                price = self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - S * np.exp(-self.q * self.T) * norm.cdf(-d1)
            return price - price_market

        return scipy.optimize.newton(BSM_IV, self.vol)

    ## MONTE-CARLO SIMULATIONS

    def price_MC(self, nb_simulations):
        if self.Div != None:
            try:
                if isinstance(self.Div, list) and all(isinstance(t, tuple) for t in self.Div):
                    None
                else:
                    print("Erreur : Vous devez entrer une liste de tuples.")
            except (SyntaxError, ValueError):
                print("Erreur : Format invalide.")
            PV_div = 0
            for div in self.Div:
                if div[0] <= self.T:
                    PV_div += div[1] * np.exp(-self.r * div[0])
            S = self.S - PV_div
        else:
            S = self.S
        price = [S * np.exp(
            (self.r - self.q - 0.5 * self.vol ** 2) * self.T + self.vol * np.sqrt(self.T) * np.random.randn()) for i in
                 range(nb_simulations)]
        if self.IsCall == True:
            pv_payoff = [max(price[i] - self.K, 0) * np.exp(-self.r * self.T) for i in range(nb_simulations)]
        else:
            pv_payoff = [max(self.K - price[i], 0) * np.exp(-self.r * self.T) for i in range(nb_simulations)]
        return np.mean(pv_payoff)

    ## BINOMIAL TREE
    def price_BT(self, nb_steps):
        delta_t = self.T / nb_steps
        u = np.exp(self.vol * np.sqrt(delta_t))
        d = np.exp(- self.vol * np.sqrt(delta_t))
        pi = (np.exp((self.r - self.q) * delta_t) - d) / (u - d)
        # On doit détermniner les spots prices des colonnes de l'arbre qui sont arpès le versement du dernier coupon.
        # Pour ce faire, on part de S0 - PV[div] et on multiplie par u et d selon le noeud concerné
        # On détemrine maintenant S0 - PV[div]:
        if self.Div != None:
            try:
                if isinstance(self.Div, list) and all(isinstance(t, tuple) for t in self.Div):
                    None
                else:
                    print("Erreur : Vous devez entrer une liste de tuples.")
            except (SyntaxError, ValueError):
                print("Erreur : Format invalide.")
            PV_div = 0
            for div in self.Div:
                if div[0] <= self.T:
                    PV_div += div[1] * np.exp(-self.r * div[0])
            S = self.S - PV_div
        else:
            S = self.S
        # print(S)

        last = [(S * u ** nb_steps) * d ** (i * 2) for i in range(0, nb_steps + 1)]
        # print(last)
        if self.IsCall == True:
            payoff_last = [max(last[i] - self.K, 0) for i in range(0, nb_steps + 1)]
        else:
            payoff_last = [max(self.K - last[i], 0) for i in range(0, nb_steps + 1)]
        # print(payoff_last)

        for k in range(nb_steps):
            PV_add = 0
            if self.Div != None:
                for div in self.Div:  # div est donc un tuple
                    if div[0] > (nb_steps - (k + 1)) * delta_t and div[0] < self.T:
                        PV_add += div[1] * np.exp(-self.r * (div[0] - (nb_steps - (k + 1)) * delta_t))
            if self.IsEuropean == True:
                price = [S * u ** (nb_steps - (k + 1)) * d ** (i * 2) + PV_add for i in range(0, nb_steps - k)]
                payoff_last = [(pi * payoff_last[j] + (1 - pi) * payoff_last[j + 1]) * np.exp(-self.r * delta_t) for j
                               in range(nb_steps - k)]
            else:
                price = [S * u ** (nb_steps - (k + 1)) * d ** (i * 2) + PV_add for i in range(0, nb_steps - k)]
                if self.IsCall == True:
                    payoff_last = [max(price[j] - self.K,
                                       (pi * payoff_last[j] + (1 - pi) * payoff_last[j + 1]) * np.exp(
                                           -self.r * delta_t)) for j in range(nb_steps - k)]
                else:
                    payoff_last = [max(self.K - price[j],
                                       (pi * payoff_last[j] + (1 - pi) * payoff_last[j + 1]) * np.exp(
                                           -self.r * delta_t)) for j in range(nb_steps - k)]
            # print(price)
            # print(payoff_last)
        return payoff_last[0]

    def price_BT_2(self, nb_steps):
        delta_t = self.T / nb_steps
        u = np.exp(self.vol * np.sqrt(delta_t))
        d = np.exp(- self.vol * np.sqrt(delta_t))
        pi = (np.exp((self.r - self.q) * delta_t) - d) / (u - d)
        matrice_spot = [
            [self.S * * (u ** j) * (d ** (t - j)) for j in range(t + 1)]
            for t in range(N + 1)
        ]