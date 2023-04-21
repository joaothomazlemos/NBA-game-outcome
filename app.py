import pickle
from django.shortcuts import render
from flask import Flask, request, app, jsonify, url_for, render_template
import numpy as np
import pandas as pd
import warnings
import datetime
import os

# The input are provided with feature names, as  we did in the training phase. So the warnings are not relevant. We are going to ignore them.
warnings.filterwarnings('ignore', message='X does not have valid feature names, but StandardScaler was fitted with feature names')
warnings.filterwarnings('ignore', message='X does not have valid feature names, but MinMaxScaler was fitted with feature names')



# create a Flask app
app = Flask(__name__)

# load the logistic regression model dinamically from path
model = pickle.load(open(os.path.join(os.path.dirname(__file__), 'Data Analysis', 'models_2', 'RandomForestClassifier_100.pkl'), 'rb'))

# load the NBA games dataset from the pickle file
games = pickle.load(open(os.path.join(os.path.dirname(__file__), 'production_df.pkl'), 'rb'))
games['date'] = pd.to_datetime(games['date'])

# Getting the most recent scraped data from games['date'] column
last_date = datetime.datetime.strftime(games['date'].max(), "%d-%m-%Y")

# Loadings the best 50 features
best_features = pd.read_csv(os.path.join(os.path.dirname(__file__), 'Data Analysis', 'best_features', 'PCA_100.csv'))

# define the information columns. We are going to take out all this information to concatenate the rows of the last n games of the 2 teams
#although, as the df is already date ordered, we are only using the 'Team' column to search for the last n games of each team. Is the col that we associate with the user input
info_cols = ['date', 'Team', 'opponent_Team', 'season', 'home', 'WIN']

# define the home page of the web app
@app.route('/')
def home():
    return render_template('home.html', message='Lastest games scraped on: ' + str(last_date))

# define the predict API endpoint
@app.route('/predict', methods=['POST'])
def predict():
    """ Predict the winner of a NBA game
     This function takes the home and away team names as input and returns the predicted winner
      :param home_team: the name of the home team
       :param away_team: the name of the away team
        :return: the predicted winner of the game                  
         ---------------------------------------
         Information about what is happening in the function:
            1. We get the team names from the request
            2. We raise an error if the team names are not in the 3 letters format, using assert
            3. We raise an error if the team names are not all in caps, using assert
            4. We raise an error if the team names are not in the dataset
            5. We assign the team names to variables
            6. We retrieve the past 6 games stats for each team from the dataset that we loaded and is stored in the variable games
            7. We calculate the means of the past 6 games stats of team A and team B
            8. We rename the columns so it matches the training dataset, and we can properly select the features
               8.1. The columns names of the loaded dataset for the home team will be renamed to 'home_rolling_' + column name
                8.2. The columns names of the loaded dataset for the away team will be renamed to 'away_rolling_' + column name
            9. We concatenate the means of team A and team B to create the feature vector
            10. We select the best 50 features from the feature vector, using the best_features variable. This will be the input of the model.
            11. We make the prediction using the logistic regression model
             """
    
    #request_data = request.get_json() # if the request is in json format to pass in POSTMAN for example
    # get the team names from the request to a list with the teams names
    request_data = [str(x) for x in request.form.values()] #type: ignore
    #passing the name sin the list to a dictionary, with keyvalues 'home_team' and 'away_team'
    request_data = {'home_team': request_data[0], 'away_team': request_data[1]}
    
    # raising an error if the team names are not in the 3 letters format, using assert, returning a message to the user on the webpage:
    if (len(request_data['home_team']) != 3) or (len(request_data['away_team']) != 3):
        return jsonify({'error': 'Team name should have 3 letters format'})
    # getting the correct format of the team names, all in caps
    if not ((request_data['home_team'].isupper()) or (request_data['away_team'].isupper())):
        request_data['home_team'] = request_data['home_team'].upper()
        request_data['away_team'] = request_data['away_team'].upper()
    if 'home_team' not in request_data or 'away_team' not in request_data:
        return jsonify({'error': 'home_team and away_team are required'})
    # Raising an error if the team names are not in the dataset
    if request_data['home_team'] not in games['Team'].unique() or request_data['away_team'] not in games['Team'].unique():
        return jsonify({'error': 'Team not found in the dataset'})


    #assigning the team names to variables
    home_team = request_data['home_team']
    away_team = request_data['away_team']

        # retrieve the past 6 games stats for each team from the dataset
    home_team_games = games.loc[games['Team'] == home_team].tail(6).drop(columns=info_cols)
    away_team_games = games.loc[games['Team'] == away_team].tail(6).drop(columns=info_cols)

    # calculate the means of the past 6 games stats of team A and team B
    home_team_mean = np.mean(home_team_games, axis=0)
    away_team_mean = np.mean(away_team_games, axis=0)



    #renaming the columns so it matches the training dataset, and we can properly select the features
    home_team_mean.rename(lambda x: 'home_rolling_' + x, inplace=True)
    away_team_mean.rename(lambda x: 'away_rolling_' + x, inplace=True)

    # concatenate the means of team A and team B to create the feature vector into a dataframe format
    feature_vector = pd.concat([home_team_mean, away_team_mean], axis=0)
    

    #selecting the best 50 features
    feature_vector = feature_vector[best_features.iloc[:, 0].to_list()]


    # make the prediction using the logistic regression model
    prediction = model.predict([feature_vector])[0]
    prob = model.predict_proba([feature_vector])[0][prediction]
    if prediction == 1:
        winner = home_team
    else:
        winner = away_team

    # return the prediction with render_template
    return render_template('home.html', message='Lastest games scraped on: ' + str(last_date),
         prediction_text='You choose to see who will win in the game between {} and {}.\n The predicted winner is {} with certainty of {:.1%}'.format(home_team, away_team,winner, prob))

   # return the prediction as a JSON object
    return jsonify(f'The predicted winner is {winner} with certainty of {prob: .1%}')


if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
    #app.run(host='0.0.0.0', port=5000)
    # link to the app: http://192.168.0.14:5000
    #app.run(debug=True)