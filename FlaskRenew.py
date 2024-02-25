from flask import Flask, render_template, request, redirect, url_for,jsonify
import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import load_model

app = Flask(__name__)

gb_model = pickle.load(open(r"D:\HackAIThon\gbm_model.pkl", 'rb'))

lemmatizer = WordNetLemmatizer()
intents = json.loads(open(r"D:\HackAIThon\EnergyIntents.json").read())
words = pickle.load(open(r"D:\HackAIThon\words.pkl", 'rb'))
classes = pickle.load(open(r"D:\HackAIThon\classes.pkl", 'rb'))
model = load_model(r"D:\HackAIThon\chatbot_model.h5")

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/welcome.html')
def welcome():
    return render_template('welcome.html')

@app.route('/index.html')
def home_index():
    return render_template('index.html')

@app.route('/back.html')
def home_back():
    return render_template('home.html')

@app.route('/home.html')
def home_home():
    return render_template('home.html')

@app.route('/chat.html')
def home_chat():
    return render_template('chat.html')


@app.route('/get')
def get_bot_response():
    user_input = request.args.get('msg')
    ints = predict_class(user_input)
    response = get_response(ints, intents)
    return response

@app.route('/map.html')
def map():
    return render_template('map.html')

@app.route('/predict_gb', methods=['POST'])
def predict_gb():
    try:
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        energy_need = float(request.form['energy'])
        budget = float(request.form['budget'])
        square_feet = float(request.form['squarefeet'])
        data = np.array([[latitude, longitude, energy_need, budget, square_feet]])
        prediction = gb_model.predict(data)

               
        return render_template('prediction.html', prediction=prediction[0])
    except Exception as e:
        return render_template('prediction.html', error=str(e))

@app.route('/estimate.html')
def estimate():
    return render_template('estimate.html')
   
@app.route('/calculate', methods=['POST'])
def calculate():
    energy_type = request.form['energy_type']
    budget = int(request.form['budget'])
    result = {}
    
    if energy_type == 'solar':
        result = calculate_solar(budget)
    elif energy_type == 'wind':
        result = calculate_wind(budget)
    elif energy_type == 'hydro':
        result = calculate_hydro(budget)
    else:
        return "Invalid energy type"
    
    return render_template('result.html', result=result)

def calculate_solar(budget):
    panel_price = 12000  
    inverter_price = 35000 
    battery_price = 15000 
    installation_cost = 70000  
    max_panels = budget // panel_price
    max_inverters = budget // inverter_price
    max_batteries = budget // battery_price
    max_panels_with_installation = (budget - installation_cost) // panel_price
    max_inverters_with_installation = (budget - installation_cost) // inverter_price
    max_batteries_with_installation = (budget - installation_cost) // battery_price
    result = {
        "Items_within_budget": budget,
        "Without_installation_cost": {
            "Maximum_panels": max_panels,
            "Maximum_inverters": max_inverters,
            "Maximum_batteries": max_batteries
        },
        "Considering_installation_cost": {
            "Maximum_panels_with_installation": max_panels_with_installation,
            "Maximum_inverters_with_installation": max_inverters_with_installation,
            "Maximum_batteries_with_installation": max_batteries_with_installation
        }
    }
    return result

def calculate_wind(budget):
    result = {
        "Items_within_budget": budget,
        "Without_installation_cost": {
            "Maximum_wind_turbines": budget // 20000,
            "Maximum_capacity_per_turbine": 5,
            "Total_maximum_capacity": (budget // 20000) * 5
        },
        "Considering_installation_cost": {
            "Maximum_wind_turbines_with_installation": (budget - 5000) // 20000,
            "Maximum_capacity_per_turbine": 5,
            "Total_maximum_capacity_with_installation": ((budget - 5000) // 20000) * 5
        }
    }
    return result

def calculate_hydro(budget):
    turbine_price = 90000  
    shaft_price = 100000
    rotor_price = 1500 
    stator_price = 400000
    generator_price = 150000
    installation_cost = 60000000
    
    # Calculate the maximum number of hydroelectric components without installation cost
    max_turbine = budget // turbine_price
    max_shaft = budget // shaft_price
    max_rotor = budget // rotor_price
    max_stator = budget // stator_price
    max_generator = budget // generator_price
    
    # Calculate the maximum number of hydroelectric components with installation cost
    max_turbine_with_installation = (budget - installation_cost) // turbine_price
    max_shaft_with_installation = (budget - installation_cost) // shaft_price
    max_rotor_with_installation = (budget - installation_cost) // rotor_price
    max_stator_with_installation = (budget - installation_cost) // stator_price
    max_generator_with_installation = (budget - installation_cost) // generator_price
    
    result = {
        "Items_within_budget": budget,
        "Without_installation_cost": {
            "Maximum_turbines": max_turbine,
            "Maximum_shafts": max_shaft,
            "Maximum_rotors": max_rotor,
            "Maximum_stators": max_stator,
            "Maximum_generators": max_generator
        },
        "Considering_installation_cost": {
            "Maximum_turbines_with_installation": max_turbine_with_installation,
            "Maximum_shafts_with_installation": max_shaft_with_installation,
            "Maximum_rotors_with_installation": max_rotor_with_installation,
            "Maximum_stators_with_installation": max_stator_with_installation,
            "Maximum_generators_with_installation": max_generator_with_installation
        }
    }

    return result
if __name__ == '__main__':
    app.run(debug=True)