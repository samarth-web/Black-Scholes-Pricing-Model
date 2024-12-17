import numpy as np
from scipy.stats import norm

def d1_d2(S, K, r, T, sigma):
    """
    Compute the d1 and d2 terms used in the Black-Scholes formula.
    """
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2

def black_scholes_price(S, K, r, T, sigma, option_type='call'):
    """
    Compute the Black-Scholes price for a European call or put option.
    
    Parameters
    ----------
    S : float
        Current underlying asset price.
    K : float
        Strike price.
    r : float
        Risk-free interest rate (annualized).
    T : float
        Time to maturity in years.
    sigma : float
        Volatility (annualized).
    option_type : str
        'call' or 'put'.
    
    Returns
    -------
    price : float
        Theoretical option price according to the Black-Scholes model.
    """
    d1, d2 = d1_d2(S, K, r, T, sigma)
    
    if option_type.lower() == 'call':
        price = S * norm.cdf(d1) - K * np.exp(-r*T) * norm.cdf(d2)
    elif option_type.lower() == 'put':
        price = K * np.exp(-r*T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("option_type must be 'call' or 'put'.")

    return price

def black_scholes_greeks(S, K, r, T, sigma, option_type='call'):
    """
    Compute the Greeks (Delta, Gamma, Vega, Theta, Rho) for a European option under Black-Scholes.
    
    Parameters
    ----------
    S : float
        Current underlying asset price.
    K : float
        Strike price.
    r : float
        Risk-free interest rate (annualized).
    T : float
        Time to maturity in years.
    sigma : float
        Volatility (annualized).
    option_type : str
        'call' or 'put'.
    
    Returns
    -------
    greeks : dict
        A dictionary with keys 'Delta', 'Gamma', 'Vega', 'Theta', 'Rho'.
    """
    d1, d2 = d1_d2(S, K, r, T, sigma)
    pdf_d1 = norm.pdf(d1)  
    
    
    discount = np.exp(-r * T)

   
    if option_type.lower() == 'call':
        delta = norm.cdf(d1)
    else:
        delta = norm.cdf(d1) - 1

    gamma = pdf_d1 / (S * sigma * np.sqrt(T))


    vega = S * pdf_d1 * np.sqrt(T)

    if option_type.lower() == 'call':
        theta = (- (S * pdf_d1 * sigma) / (2 * np.sqrt(T))) \
                - r * K * discount * norm.cdf(d2)
    else:
        theta = (- (S * pdf_d1 * sigma) / (2 * np.sqrt(T))) \
                + r * K * discount * norm.cdf(-d2)

   
    if option_type.lower() == 'call':
        rho = K * T * discount * norm.cdf(d2)
    else:
        rho = -K * T * discount * norm.cdf(-d2)

    greeks = {
        'Delta': delta,
        'Gamma': gamma,
        'Vega': vega,
        'Theta': theta,
        'Rho': rho
    }

    return greeks


if __name__ == "__main__":
    
    S = 100.0   
    K = 100.0  
    r = 0.01    
    T = 1.0     
    sigma = 0.2

    call_price = black_scholes_price(S, K, r, T, sigma, 'call')
    put_price = black_scholes_price(S, K, r, T, sigma, 'put')

    call_greeks = black_scholes_greeks(S, K, r, T, sigma, 'call')
    put_greeks = black_scholes_greeks(S, K, r, T, sigma, 'put')

    print("Call Option Price:", call_price)
    print("Call Greeks:", call_greeks)
    print("Put Option Price:", put_price)
    print("Put Greeks:", put_greeks)
