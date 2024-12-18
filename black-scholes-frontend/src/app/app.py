from flask import Flask, render_template_string, request

import numpy as np
from scipy.stats import norm

app = Flask(__name__)

# HTML template for the website
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Black Scholes App</title>
</head>
<body>
    <h1>Please provide the following inputs for the Black-Scholes model:</h1>
    <form method="POST">
        <label for="S">Underlying price (S):</label>
        <input type="decimal" id="S" name="S" required><br><br>

        <label for="K">Strike price (K):</label>
        <input type="decimal" id="K" name="K" required><br><br>

        <label for="r">Risk-free rate (r) as a decimal (e.g., 0.01 for 1%):</label>
        <input type="decimal" id="r" name="r" required><br><br>

        <label for="T">Time to maturity (T) in years (e.g., 0.5 for 6 months):</label>
        <input type="decimal" id="T" name="T" required><br><br>

        <label for="sigma">Volatility (sigma) as a decimal (e.g., 0.2 for 20%):  </label>
        <input type="decimal" id="sigma" name="sigma" required><br><br>

        <label for="option_type">Option type ('call' or 'put'):</label>
        <input type="String" id="option_type" name="option_type" required><br><br>

        <button type="submit">Calculate</button>
    </form>

    {% if result is not none %}
        <h2>Result: {{ result }}</h2>
    {% endif %}
</body>
</html>
"""
@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    if request.method == 'POST':
        try:

            app.logger.info(request.form)
            S = float(request.form.get('S'))
            K = float(request.form.get('K'))
            r = float(request.form.get('r'))
            T = float(request.form.get('T'))
            sigma = float(request.form.get('sigma'))
            option_type = request.form.get('option_type', 'call').strip().lower()

            if option_type == 'call':
                pass
            elif option_type == 'put':
                pass
            else:
                raise ValueError("Option type must be 'call' or 'put'.")

            price = black_scholes_price(S, K, r, T, sigma, option_type)
            greeks = black_scholes_greeks(S, K, r, T, sigma, option_type)

            result =("Price: ", price ,", Greeks: ", greeks)

        except Exception as e:
                result = ("Error: ", e)
   
    return render_template_string(HTML_TEMPLATE, result=result)


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


if __name__ == '__main__':
    app.run(debug=True)

