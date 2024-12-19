from flask import Flask, render_template, request, redirect,url_for

import numpy as np
from scipy.stats import norm

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def start():
    result = None
    if request.method == 'POST':
        try:
            value = request.form.get('choice')
            if value == 'Calculator':
                result = 1
                return redirect(url_for('calculator'))
            else:
                result = 2

        except Exception as e:
              result = ("Error: ", e)
   
   
    return render_template('start.html', result=result)

@app.route('/calculator', methods=["GET","POST"])
def calculator():
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
   
    return render_template('app.html', result=result)


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

