from flask import Flask, render_template, request
import requests

app = Flask(__name__)

class TemperatureConverter:
    @staticmethod
    def convert_temperature(temp,input_unit, output_unit):
        if input_unit == output_unit:
            return temp
            
        conversion_map = {
            ('celsius', 'fahrenheit'): lambda t: (t * 9/5) + 32,
            ('celsius', 'kelvin'): lambda t: t + 273.15,
            ('fahrenheit', 'celsius'): lambda t: (t - 32) * 5/9,
            ('fahrenheit', 'kelvin'): lambda t: (t - 32) * 5/9 + 273.15,
            ('kelvin', 'celsius'): lambda t: t - 273.15,
            ('kelvin', 'fahrenheit'): lambda t: (t - 273.15) * 9/5 + 32
        }
        
        key = (input_unit, output_unit)
        if key in conversion_map:
            return conversion_map[key](temp)
        return temp

class CurrencyService:
    @staticmethod
    def get_exchange_rates():
        try:
            response = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'USD_to_BDT': round(data['rates']['BDT'], 2),
                    'USD_to_INR': round(data['rates']['INR'], 2),
                    'USD_to_EUR': round(data['rates']['EUR'], 2)
                }
        except:
            pass
        # Fallback rates
        return {
            'USD_to_BDT': 122.50,
            'USD_to_INR': 83.25,
            'USD_to_EUR': 0.92
        }
    @staticmethod
    def currency_converter(amount, input_amount, output_amount):
        data1 = CurrencyService.get_exchange_rates()
        if input_amount == output_amount:
            return amount
        conversion_amount ={
          ("USD", "BDT"): lambda a: a * data1['USD_to_BDT'],
        ("USD", "INR"): lambda a: a * data1['USD_to_INR'], 
        ("USD", "EUR"): lambda a: a * data1['USD_to_EUR'],
        
        #USD
        ("BDT", "USD"): lambda a: a / data1['USD_to_BDT'],
        ("INR", "USD"): lambda a: a / data1['USD_to_INR'],
        ("EUR", "USD"): lambda a: a / data1['USD_to_EUR'],
        
        #BDT
        ("BDT", "INR"): lambda a: (a / data1['USD_to_BDT']) * data1['USD_to_INR'],
          
        ("BDT", "EUR"): lambda a: (a / data1['USD_to_BDT']) * data1['USD_to_EUR'],
        
        #INR
        ("INR", "BDT"): lambda a: (a / data1['USD_to_INR']) * data1['USD_to_BDT'],
    
        ("INR", "EUR"): lambda a: (a / data1['USD_to_INR']) * data1['USD_to_EUR'],
        
        #EUR
        ("EUR", "BDT"): lambda a: (a / data1['USD_to_EUR']) * data1['USD_to_BDT'],
        
        ("EUR", "INR"): lambda a: (a / data1['USD_to_EUR']) * data1['USD_to_INR'],
        }
        key = (input_amount, output_amount)
        if key in conversion_amount:
            return conversion_amount[key](amount)   
        return amount
@app.route("/", methods=["GET", "POST"])
def index():
    temp_result = None
    currency_result = None
    error_message = None
    exchange_data = CurrencyService.get_exchange_rates()
    
    if request.method == "POST":
        try:
            temp_input = float(request.form["temperature"])
            from_unit = request.form["from_unit"]
            to_unit = request.form["to_unit"]
            
            converted_temp = TemperatureConverter.convert_temperature(temp_input, from_unit, to_unit)
            temp_result = {
                'value': f"{converted_temp:.2f}",
                'from_unit': from_unit,
                'to_unit': to_unit
            }
            
        except ValueError:
            error_message = "Please enter a valid number for temperature"
        except Exception as e:
            error_message = "An error occurred during conversion"
        
        try:
            if "currency_amount" in request.form:
                currency_input = float(request.form["currency_amount"])
                from_currency = request.form["from_currency"]
                to_currency = request.form["to_currency"]

                converted_currency = CurrencyService.currency_converter(currency_input,from_currency,to_currency)
                currency_result = {
                    "value": f"{converted_currency: .2f}",
                    "from_currency": from_currency,
                    "to_currency": to_currency
                }
        except ValueError:
            error_message = "Please enter a valid number for currency"
        except Exception as e:
            error_message = f"An error occured during currency conversion: {str(e)}"
    
    return render_template("index.html", 
                         result=temp_result,
                         currency_result = currency_result, 
                         rates=exchange_data, 
                         error=error_message)

if __name__ == "__main__":
    app.run(debug=True)