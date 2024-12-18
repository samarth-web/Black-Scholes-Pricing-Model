import numpy as np
from scipy.stats import norm
from flask import Flask, request, 

app = Flask(__name__, template_folder='app')

@app.route('/')
def index():
    return render_template('app.component.html') 

@app.route('/process', methods=['POST'])
def process():
    user_input = request.form['userInput']

    result = my_python_function(user_input)
    return f"Processed input: {result}"

def my_python_function(input_value):
   
    return f"You entered: {input_value}"


def d1_d2(S, K, r, T, sigma):
   
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2

def black_scholes_price(S, K, r, T, sigma, option_type='call'):
  
    d1, d2 = d1_d2(S, K, r, T, sigma)
    
    if option_type.lower() == 'call':
        price = S * norm.cdf(d1) - K * np.exp(-r*T) * norm.cdf(d2)
    elif option_type.lower() == 'put':
        price = K * np.exp(-r*T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("option_type must be 'call' or 'put'.")

    return price

def black_scholes_greeks(S, K, r, T, sigma, option_type='call'):
   
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
    app.run(debug=True)
    print("Please provide the following inputs for the Black-Scholes model:")
    S = float(input("Underlying price (S): "))
    K = float(input("Strike price (K): "))
    r = float(input("Risk-free rate (r) as a decimal (e.g., 0.01 for 1%): "))
    T = float(input("Time to maturity (T) in years (e.g., 0.5 for 6 months): "))
    sigma = float(input("Volatility (sigma) as a decimal (e.g., 0.2 for 20%): "))
    option_type = input("Option type ('call' or 'put'): ").strip().lower()
    
    # Validate option type
    if option_type not in ['call', 'put']:
        raise ValueError("Invalid option type. Please enter 'call' or 'put'.")
    
    # Compute price and Greeks
    price = black_scholes_price(S, K, r, T, sigma, option_type)
    greeks = black_scholes_greeks(S, K, r, T, sigma, option_type)


    print("\n--- Black-Scholes Results ---")
    print(f"Option Type: {option_type.capitalize()}")
    print(f"Price: {price:.4f}")
    print("Greeks:")
    for greek, value in greeks.items():
        print(f"  {greek}: {value:.4f}")
