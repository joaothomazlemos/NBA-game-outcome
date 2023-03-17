import pickle
from django.shortcuts import render
from flask import Flask, request, app, jsonify, url_for, render_template
import numpy as np
import pandas as pd


# create a Flask app
app = Flask(__name__)

# load the logistic regression model
model = pickle.load(open('Data Analysis/models_2/LogisticRegression_50.pkl', 'rb'))

# load the NBA games dataset
df = pd.read_csv('path/to/nba/games/dataset.csv')

# define the home page of the web app
@app.route('/')
def home():
    return 'Welcome to NBA Predictor!'

# define the predict API endpoint
@app.route('/predict', methods=['POST'])
def predict():
    # get the team names from the request
    request_data = request.get_json()
    if 'home_team' not in request_data or 'away_team' not in request_data:
        return jsonify({'error': 'home_team and away_team are required'})

    home_team = request_data['home_team']
    away_team = request_data['away_team']

    # retrieve the past 6 games stats for each team from the dataset
    team_a_games = df.loc[df['Team'] == home_team].tail(6).drop(columns=['Team'])
    team_b_games = df.loc[df['Team'] == away_team].tail(6).drop(columns=['Team'])

    # calculate the means of the past 6 games stats of team A and team B
    team_a_mean = np.mean(team_a_games, axis=0)
    team_b_mean = np.mean(team_b_games, axis=0)

    # concatenate the means of team A and team B to create the feature vector
    feature_vector = np.concatenate([team_a_mean, team_b_mean])

    # make the prediction using the logistic regression model
    prediction = model.predict([feature_vector])[0]

    # return the prediction as a JSON object
    return jsonify({'prediction': prediction})

if __name__ == '__main__':
    app.run(debug=True)