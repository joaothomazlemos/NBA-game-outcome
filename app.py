import pickle
from django.shortcuts import render
from flask import Flask, request, app, jsonify, url_for, render_template
import numpy as np
import pandas as pd

# creating a Flask app, with LogisticRegression model trained with the 50 features selected dataset
app = Flask(__name__)
#load model
model = pickle.load(open('Data Analysis/models_2/LogisticRegression_50.pkl', 'rb'))

# defining the home page of our site
@app.route('/')
def home():
    return render_template('home.html')

# defining the function which will make the prediction using the data whith the user inputs
@app.route('/predict_api', methods=['POST'])

def predict_api():
    '''
    For direct API calls trought request
    '''
    data = request.json['data']# type: ignore
    print(f'raw data: {data}')
    print(np.array(list(data.values())).reshape(1, -1))
    data = np.array(list(data.values())).reshape(1, -1)
    prediction = model.predict(data)

    output = prediction[0]
    print(f'output: {output}')
    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)