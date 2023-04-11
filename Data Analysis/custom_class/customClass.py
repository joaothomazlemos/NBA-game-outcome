


class ModelParams:
        
         
        
        """ Info:
        This class initializes the parameters and scalers for the models, which will be used for gridsearchcv,
        and their scaling methods.
        Input:
          model: the model to be used
          n_features: number of features of the dataset so that some hyperparameters grid can be set, mostly for emsembled.
          Like, for example, the max depth of the tree, which will be set a number between 2 and the square root of the number of features.
          Or max_leaf_nodes, which will be set to the number between  the square of features and the number of features.

          scaler: Default = False, if True, the model will be scaled accordily with its respective scaler
        Output:
          get_pipe: returns the model pipeline and its parameters
          model_name: returns the model name
            """
      
      
      #creating the models respective pipelines and its parameters
        def __init__(self, model, n_features=None, scaler=False):
              import numpy as np
              """ Info:
                This method initializes the model and the scaling method
                ---------------------------------------------------------------------------------------------

                  Input:
                  model: the model to be used
                    Scaler: boolean
                    -------------------------------------------------------------------------------------------
                    
                      Output:
                      None """
              
              self.model = model
              self.scaler = scaler
              self.model_name = model.__class__.__name__
                            
              #models_list = [LogisticRegression(random_state=42), LinearSVC(random_state=42), RandomForestClassifier(random_state=42), GradientBoostingClassifier(random_state=42)]     
          
              #creating the models  parameters dictionary
              # Parameters of pipelines can be set using '__' separated parameter names:
              self.models_params = {
              'LogisticRegression': {'logisticregression__penalty': ['l1', 'l2', 'elasticnet'],
                                        'logisticregression__C': [0.001, 0.01, 0.1, 1, 10, 100],
                                          'logisticregression__solver': ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'],
                                            'logisticregression__max_iter': [10000]},
              'LinearSVC': {'linearsvc__C': [0.0001, 0.001, 0.01, 0.1, 1, 10], 'linearsvc__loss': ['hinge', 'squared_hinge'],
                                'linearsvc__max_iter': [100000]},
              'RandomForestClassifier': {   'randomforestclassifier__n_estimators': [50, 100, 200, 300, 400, 500, 1000, 1500],
                                            'randomforestclassifier__criterion':['gini', 'entropy'],
                                            'randomforestclassifier__max_depth': list(np.arange(start = 2, stop=((n_features)**(1/2) + 1), step=1, dtype=int)) if n_features else None,
                                              'randomforestclassifier__min_samples_split': [2, 5, 10],
                                                'randomforestclassifier__min_samples_leaf': [1, 2, 4],
                                            'randomforestclassifier__max_features': ['sqrt', None],
                                              'randomforestclassifier__min_weight_fraction_leaf': [0.0, 0.25, 0.5],
                                            'randomforestclassifier__max_leaf_nodes': list(np.arange(start=n_features**(1/2), stop = n_features, step=3, dtype=int)) if n_features else None,
                                              'randomforestclassifier__min_impurity_decrease': [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0]},
              'GradientBoostingClassifier': {'gradientboostingclassifier__loss': ['deviance', 'exponential'],
                                                'gradientboostingclassifier__learning_rate': [0.001, 0.01, 0.1, 1, 10],
                                                'gradientboostingclassifier__subsample': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                                                  'gradientboostingclassifier__n_estimators': [100, 200, 300, 400, 500, 1000, 1500],
                                                    'gradientboostingclassifier__criterion': ['friedman_mse', 'squared_error'],
                                                      'gradientboostingclassifier__min_samples_split': [2, 5, 10],
                                                        'gradientboostingclassifier__min_samples_leaf': [1, 2, 4],
                                                          'gradientboostingclassifier__min_weight_fraction_leaf': [0.0, 0.25, 0.5],
                                                            'gradientboostingclassifier__max_depth': list(np.arange(start = 2, stop=n_features**(1/2) + 1, step=1, dtype=int)) if n_features else None,
                                                              'gradientboostingclassifier__min_impurity_decrease': [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0],
                                                                'gradientboostingclassifier__max_features': ['sqrt', None],
                                                                  'gradientboostingclassifier__max_leaf_nodes': list(np.arange(start=n_features**(1/2), stop = n_features, step=3, dtype=int)) if n_features else None}
          }
        #importing the necessary libraries
        from sklearn.preprocessing import StandardScaler, MinMaxScaler
    

      #creating the models respective scalers:
        models_scalers = {
                'LogisticRegression': StandardScaler(),
                'LinearSVC': StandardScaler(),
                'RandomForestClassifier': MinMaxScaler(),
                'GradientBoostingClassifier': MinMaxScaler()
        }
      
      

        def get_pipe(self):
                from sklearn.pipeline import make_pipeline
                """ Info:
                  This method returns the model pipeline and its parameters and the model name
                  ---------------------------------------------------------------------------------------------

                    Input:
                    None
                    ---------------------------------------------------------------------------------------------

                      Output:
                      model pipeline, model parameters, model name """
                
                self.params = self.models_params[self.model_name]
                if self.scaler:
                        self.scaler = self.models_scalers[self.model_name]
                else:
                        self.scaler = None
                return make_pipeline(self.scaler, self.model), self.params, self.model_name






# creating a class to take in the model and return the metrics of this model with the best parameters,
# using for this the GridSearchCV function
class ModelDevelopment:
    
     
    """ Takes in the model, the X and y data and splits the data into train and test sets.
    Functions:
    - grid_search: Takes in the parameters to be tested and the scoring metric and returns the best model, best parameters and best score
    - model_metrics: Prints the accuracy, precision, recall, f1 and auc of best model parameters found by the grid search against the test set
    - roc_curve: Plots the ROC curve of the best model parameters found by the grid search against the test set"""

    def __init__(self, model, model_name, X, y):
        #importing necessary libraries
        from sklearn.model_selection import train_test_split
        """ Info:
            Takes in the model, the X and y data and splits the data into train and test sets.

            Input:
            model: Model to be tested
            model_name: Name of the model to be tested
            X: Feature set
            y: Target series
            
            

            Output:
            X_train: Feature set for the train set
            X_test: Feature set for the test set
            y_train: Target series for the train set
            y_test: Target series for the test set
            
                    """
        self.model = model
        self.model_name = model_name
        self.best_model = None
        self.X = X
        self.y = y
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        

        
    

    def grid_search(self, params: dict, scoring: str): # scoring is the metric we want to optimize, mostly 'roc_auc'
        #importing necessary libraries
        import time
        from sklearn.model_selection import GridSearchCV
        """ Info:
            Takes in the parameters to be tested and the scoring metric and returns the best model, best parameters and best score
             Input:
              params: Dictionary with the parameters to be tested
              scoring: Metric to be optimized
             Output:
              best_model: Best model found by the grid search
              best_params: Best parameters found by the grid search
              best_score: Best score found by the grid search """
        
        #measuring the time it takes to run the grid search
        #start time
        start = time.time()
        
        grid = GridSearchCV(self.model, params, cv=5, scoring=scoring, n_jobs=-1, verbose=3) #verbose = 2 so we can watch the progress in more detail
        #trying to fit the model with the parameters
        try:
            grid.fit(self.X, self.y)
        except Exception as e:
            print("An error occurred:", e)
            pass
        self.best_model = grid.best_estimator_
        self.best_params = grid.best_params_
        self.best_score = grid.best_score_

        #final time
        end = time.time()
        #print the total time it took to run the grid search in minutes
        print('Total time: ', round((end-start)/60), ' minutes')

        return self.best_model, self.best_params, self.best_score
    
    def random_search(self, params_range: dict, scoring: str):
        #importing necessary libraries
        import time
        from sklearn.model_selection import RandomizedSearchCV
        """ Info:
            Takes in the parameters to be tested using the RandomizedSearchCV() funtion and the scoring metric and returns the best model, best parameters and best score. The randomized search allows us to test more parameters in less time.
            --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
             Input:
              params: Dictionary with the parameters to be tested
              scoring: Metric to be optimized
            --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
             Output:
              best_model: Best model found by the grid search
              best_params: Best parameters found by the grid search
              best_score: Best score found by the grid search """
        
        #measuring the time it takes to run the grid search
        #start time
        start = time.time()
        
        grid = RandomizedSearchCV(self.model, params_range, cv=3, scoring=scoring, n_jobs=-1, verbose=3, n_iter=1000, random_state=42)
        #trying to fit the model with the parameters
        try:
            grid.fit(self.X, self.y)
        except Exception as e:
            print("An error occurred:", e)
            pass
        self.best_model = grid.best_estimator_
        self.best_params = grid.best_params_
        self.best_score = grid.best_score_
        #final time
        end = time.time()
        #print the total time it took to run the grid search in minutes
        print('Total time: ', round((end-start)/60), ' minutes')
        return self.best_model, self.best_params, self.best_score
        
        
    
    def model_metrics(self):
        #importing necessary libraries
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        """ Prints the accuracy, precision, recall, f1 and auc of best model parameters found by the grid search against the test set
            For this, we use the pre split X test and y test data, which are 20% of the original data
          """
        y_pred = self.best_model.predict(self.X_test) #type: ignore
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred)
        recall = recall_score(self.y_test, y_pred)
        f1 = f1_score(self.y_test, y_pred)
        auc = roc_auc_score(self.y_test, y_pred)
        print(f'Accuracy: {accuracy:.1%}' )
        print(f'Precision: {precision:.1%}')
        print(f'Recall: {recall:.1%}')
        print(f'F1: {f1:.1%}')
        print(f'AUC: {auc:.1%}') #auc score
        
    
    def roc_curve(self):
        #importing necessary libraries
        from sklearn.metrics import roc_curve
        import matplotlib.pyplot as plt
        """ Plots the ROC curve of the best model parameters found by the grid search against the test set
            For this, we use the pre split X test and y test data, which are 20% of the original data
          """
        y_pred_proba = self.best_model.predict_proba(self.X_test)[:,1] #type: ignore
        fpr, tpr, thresholds = roc_curve(self.y_test, y_pred_proba)
        plt.plot([0,1], [0,1], 'k--')
        plt.plot(fpr, tpr, label=self.model_name)
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(self.model_name+' ROC Curve')
        plt.show()

    # function to plot the confusion matrix
    def plot_confusion_matrix(self):
        #importing necessary libraries
        from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
        import seaborn as sns
        import matplotlib.pyplot as plt
        """ Plots the confusion matrix of the best model parameters found by the grid search against the test set
            For this, we use the pre split X test and y test data, which are 20% of the original data
          """
        y_pred = self.best_model.predict(self.X_test) #type: ignore
        cm = confusion_matrix(self.y_test, y_pred)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
        disp.plot()
        plt.title('Confusion Matrix')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.show()