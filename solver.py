import copy
import numpy as np
import pandas as pd
from gplearn.genetic import SymbolicRegressor

from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.feature_selection import SequentialFeatureSelector
from sklearn.linear_model import LassoCV
from sklearn.metrics import r2_score

from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import mean_absolute_error, r2_score



"""
X = np.random.uniform(-5, 5, (1000, 2))
y = 2 * X[:, 0] + X[:, 1]**2

est = SymbolicRegressor(
    population_size=5000,
    generations=20,
    stopping_criteria=0.01,
    p_crossover=0.7,
    p_subtree_mutation=0.1,
    p_hoist_mutation=0.05,
    p_point_mutation=0.1,
    max_samples=0.9,
    verbose=1
)

est.fit(X, y)

print(est._program)"""
#
#Function to prep that data to use for whatever regression model
#
def prep_data(best_systems):


    #basically we first want to gather our input data

    sources = []

    splits = []

    for _ in best_systems:

        #from here lets compile our inputs

        temp_inputs = []

        for each_src in _.sources:

            temp_inputs += each_src.slurry

        sources.append(temp_inputs)

        #from here lets compile the splits

        temp_splits = []

        for each_sep in _.seperators:

            temp_splits += each_sep.splits[0] #for now lets just have it solve for the overflow

        splits.append(temp_splits)

    #from here we have the splits but we need to redo it because each array has all the separators
    #we want an array for each separator

    temp_splits = [[] for i in range(len(splits[0]))]

    for each_case in splits:

        for i in range(len(each_case)):

            temp_splits[i].append(each_case[i])

    splits = temp_splits

    del temp_splits

    #from here we have the splits as well as the 
    #the issue here is that the sources are in tonnes
    #we need to make sure that they are in a pct
    for each_source in range(len(sources)):

        total = sum(sources[each_source])

        for i in range(len(sources[each_source])):

            sources[each_source][i] /= total

    #from here we have the splits as well as the sources

    return sources, splits

#A helper fucntion for loading system data from csv
def prep_csv_data(data):

    #data will be an array of sources and splits
    # data = [[sources1, splits1], [sources2, splits2]]

    #we need to compile this to
    #sources = [[3, 5, 8], [5, 8, 3]] #for each month
    #splits = [[3, 5, 8], [5, 8, 3]] #for each month
    

    sources = []

    splits = []

    for each_case in data:

        sources.append(each_case[0])

        splits.append(each_case[1])

    #basically now because we know that the splits are the"y"
    #what we're solving for 
    #we make it so that each array is the 12 months of the recovery pct

    temp_splits = [[] for i in range(len(splits[0]))]

    for each_case in splits:

        for i in range(len(each_case)):

            temp_splits[i].append(each_case[i])

    splits = temp_splits

    #from here we have the splits as well as the 
    #the issue here is that the sources are in tonnes
    #we need to make sure that they are in a pct
    for each_source in range(len(sources)):

        total = sum(sources[each_source])

        for i in range(len(sources[each_source])):

            sources[each_source][i] /= total

    return sources, splits


#
#Function to take all the resulting equations and return the equations with the best r2
#
def determine_best_equations(all_equations, seperator_feature_names):

    #all equations contains a list of each equation for each seperator feature
    #within this list, sort it to get the best one
    #then replace the name of recovery = with the actual feature name
    #define a function to print this out best

    for each_fe in range(len(seperator_feature_names)):

        best_equation = sorted(all_equations[each_fe], key=lambda x: x[1], reverse = True)[0]

        best_equation[1] = best_equation[1].replace("Recovery = ", f"{seperator_feature_names[each_fe]} = ")

        print(best_equation)
    return

#
#Function to run all the different types of regression and return which ones have the best r2 score
#
def run_all_regression(sources, splits, feature_names=None, seperator_feature_names=None):

    if feature_names == None:

        feature_names = [f"x{i}" for i in range(len(sources[0]))]

    #now from here run the various regression types

    all_equations = [[] for i in range(len(splits))] #this will be a list to hold all the equations found
    #there will be an array for each split "y" value

    #print(seperator_feature_names)

    #lets start with linear

    #define a lambda function for adding to the all_equations

    append_to_all_equations = lambda sep_feature_index, equation_results: all_equations[sep_feature_index].append(equation_results)

    linear_results = run_linear_regression(sources, splits, feature_names)

    for each_eq in range(len(linear_results)):

        all_equations[each_eq].append(linear_results[each_eq])

    #all_equations[i].append(linear_results[i]) for i in range(len(linear_results))

    #now try the rest

    poly_sources, poly_feature_names = get_polynomial_data(sources, feature_names, degree=2)

    poly_results = run_linear_regression(poly_sources, splits, poly_feature_names)

    for each_eq in range(len(poly_results)):

        all_equations[each_eq].append(poly_results[each_eq])

    exp_sources, exp_feature_names = get_exponential_inputs(sources, feature_names)

    exp_results = run_linear_regression(exp_sources, splits, exp_feature_names)

    for each_eq in range(len(exp_results)):

        all_equations[each_eq].append(exp_results[each_eq])

    nexp_sources, nexp_feature_names = get_negative_exponential_inputs(sources, feature_names)

    nexp_results = run_linear_regression(nexp_sources, splits, nexp_feature_names)

    for each_eq in range(len(nexp_results)):

        all_equations[each_eq].append(nexp_results[each_eq])

    log_sources, log_feature_names = get_logarithmic_data(sources, feature_names)

    log_results = run_linear_regression(log_sources, splits, log_feature_names)

    for each_eq in range(len(log_results)):

        all_equations[each_eq].append(log_results[each_eq])

    #from here we want to apply the separator feature names and determine the best based on the r2 score

    determine_best_equations(all_equations, seperator_feature_names)    

    return all_equations

#
#Function for preparing exponential data
#
def get_exponential_inputs(sources, feature_names):

    new_feature_names = copy.deepcopy(feature_names)

    sources = np.array(sources).copy() 

    new_X = np.exp(sources) #turn it to exponentials

    #now we also want to change the feature names for nicer output

    for i in range(len(new_feature_names)):

        new_feature_names[i] = "e^"+new_feature_names[i]

    return new_X, new_feature_names
#
#Function for negative exponential data
#
def get_negative_exponential_inputs(sources, feature_names):

    new_feature_names = copy.deepcopy(feature_names)

    sources = np.array(sources).copy() 

    new_X = np.exp(-1*sources) #turn it to exponentials

    #now we also want to change the feature names for nicer output

    for i in range(len(new_feature_names)):

        new_feature_names[i] = "e^-"+new_feature_names[i]

    return new_X, new_feature_names

#
#Function for preparing polynomial data
#
def get_polynomial_data(sources, feature_names, degree=2):

    num_features = len(feature_names)

    new_feature_names = copy.deepcopy(feature_names)

    new_X = np.array(sources).copy() 

    for each_degree in range(2, degree+1):

        degree_X = np.array(sources)**each_degree #turn it to polynomial

        new_X = np.hstack((new_X, degree_X))

        for i in range(num_features):

            new_feature_names.append(
                new_feature_names[i]+f"^{each_degree}"
            )



    return new_X, new_feature_names


#
#Function for preparing logarithmic data
#
def get_logarithmic_data(sources, feature_names):

    sources = np.array(sources).copy() 

    new_feature_names = copy.deepcopy(feature_names)

    sources[sources == 0] = 1e-8 #just to make sure there are no zero errors

    new_X = np.log(sources) #turn it to exponentials

    for i in range(len(feature_names)):

        new_feature_names[i] = f"log({feature_names[i]})"

    return new_X, new_feature_names
#
#Function for exponential regression
#
def run_linear_regression(sources, splits, feature_names, output=False):

    #start the leave on out
    loo = LeaveOneOut()

    new_X = np.array(sources) #just easier for debugging

    #create an array for storing the equations we come up with

    all_equations = []

    #now can run the linear regression on these terms

    for each_split in range(len(splits)):
        y = np.array(splits[each_split]) #turny into a numpy array for ease

        loo_preds = np.zeros(len(y))
        
        #now loop through each case
        for train_index, test_index in loo.split(new_X):
            X_train, X_test = new_X[train_index], new_X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            
            #try and fit the model on 11 months of data
            cv_model = LinearRegression()
            cv_model.fit(X_train, y_train)
            
            #predict the last case
            loo_preds[test_index] = cv_model.predict(X_test)
            
        #now get the r2 score
        val_r2 = r2_score(y, loo_preds)
        
        #now train the model on all the data
        model = LinearRegression()
        model.fit(new_X, y)
        
        #and get he r2 score again
        train_pred = model.predict(new_X)
        train_r2 = r2_score(y, train_pred)

        if output == True:

            print(
                f"\nRegression\n"
                f"  Training R2 (In-Sample):  {train_r2:.5f}\n"
                f"  Validation R2 (LOOCV):    {val_r2:.5f}"
            )
        #now get the equation ai wrote this
        equation_terms = [f"{model.intercept_:.4f}"]
        
        for coef, name in zip(model.coef_, feature_names):
            clean_name = name.replace(" ", " * ")
            
            if coef >= 0:
                equation_terms.append(f"+ {coef:.7f} * ({clean_name})")
            else:
                equation_terms.append(f"- {abs(coef):.7f} * ({clean_name})")
        
        full_equation = "Recovery = " + " ".join(equation_terms)

        #from here package the equation and the r2 score and append to the possible equations
        function_package = [train_r2, full_equation]

        all_equations.append(function_package)


        if output == True:

            print(f"  {full_equation}")
            print("-" * 60)

    #basically from here we return the index of the "y" along with the equation in plan english
    #and the r2 score so that we can compare them all in the end
    return all_equations



