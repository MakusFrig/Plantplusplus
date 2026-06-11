#Mainfile for Simulation

"""
TODO LIST
4. create gui with pyqt probably

"""

print("Plant++ Starting...")

#import necessary modules

import matplotlib.pyplot as plt

import numpy as np

import random

import copy

import sys

import time

import pathlib

import pyfiglet

import pickle

#imports from other files

from objects import *

from system import *

from util import *

from solver import *

#some startup text
startup_text = pyfiglet.figlet_format("PLANT ++", font="slant")
print("\n",startup_text)

#
#this function will generate a random split to be used (working on it)
#
def get_random_splits_dirichlet(splits, tolerance=10):

	#need to define a way to generate random splits

	num_outflows = len(splits)

	new_splits = splits

	for each in range(len(splits[0])):

		#we're going to use a dirichlet distribtion to randomize the splits

		old_split = np.array([x[each] for x in splits])
		old_split = np.where(old_split == 0, 1e-8, old_split) #this is to get rid of 0s which cause an error with the function

		t = (tolerance+0.1)/100

		p = 1/3

		K = (1-p)/(t**2 * p) #this will define a k that adjusts with tolerance

		try:
			new_split = np.random.dirichlet(old_split * K).tolist()

		except:

			print(splits, K)

			quit()

		#from here we need to change the number in the nuew splits

		for i in range(len(new_splits)):

			new_splits[i][each] = round(new_split[i], 8)



	return new_splits

#
#this function will generate a random split to be used
#
def get_random_splits(splits, tolerance=100):

	#need to define a way to generate random splits
	#currently doing this kind of crudely, want to upgrade to a dirichlet funciton later (mostly cuz its cool)

	num_outflows = len(splits)

	new_splits = splits

	for each in range(len(splits[0])):

		#we're going to use a dirichlet distribtion to randomize the splits

		old_split = [x[each] for x in splits]

		#from here we use random function to determine new numbers

		#to make sure we're not biased to picking the overflow and randomizing it each time

		order = list(range(len(old_split)))

		random.shuffle(order)

		

		#this gives us an order of three numbers

		#since the last number we evaluate is just going to be the remainder we trim the order by 1
		last_index = order[-1]

		order = order[:-1]


		new_split = [0 for i in range(len(old_split))]

		for i in order:

			old_val = old_split[i]

			top_val = min(old_val * (1+tolerance/100), 1.0)

			bottom_val = max(old_val * (1-tolerance/100), 1e-8)

			#now we pick

			new_val = random.uniform(bottom_val, top_val)

			new_split[i] = new_val

		#from here we need to set the last one to be the remainder

		other_values = sum(new_split)

		new_val = 1-other_values

		new_split[last_index] = new_val

		#from here we need to change the number in the nuew splits

		for i in range(len(new_splits)):

			new_splits[i][each] = round(new_split[i], 8)



	return new_splits

#
#This function will go through a systems splits and randomize them within the current iterations tolerance
#
def randomize_splits(system, tolerance=100):

	#just going to go through each seperator and pass its split to random splits function

	for each_s in range(len(system.separators)):

		old_splits = system.separators[each_s].splits

		new_splits = get_random_splits(old_splits, tolerance)

		system.separators[each_s].set_splits(copy.deepcopy(new_splits))

	return system

#
#this function will take a test case thats in a folder, two files a mass_balance and a system_def
#It will return the system usable for solving and a mass balance with cases of the inputs and outputs from the csv file
#
def load_entire_system(foldername):

	#now we want to extract this

	system = get_system_csv(f"cases/{foldername}/system_def.csv")

	mass_balance, system = get_mass_balance_csv(f"cases/{foldername}/mass_balance.csv", system)

	return system, mass_balance

#
#this function will compare the simulated systems output and the actual system output from the mass balance
#
def compare_system_outputs(real_state, predicted_state):

	#the idea is to go through each collector, find the different relative to the acc values and return the average of this

	errors = []

	for each_c in predicted_state.keys():

		for each_q in range(len(predicted_state[each_c])):

			

			temp_err = round(100*abs(predicted_state[each_c][each_q]-real_state[each_c][each_q])/real_state[each_c][each_q], 3)

			
			errors.append(temp_err)

	#from here we have a list full of errors

	max_err = max(errors)

	min_err = min(errors)

	avg_err = round(sum(errors)/len(errors), 3)

	#print(f"Avg Err: {avg_err}\t Max Err: {max_err}\t Min Err: {min_err}")


	return avg_err

#
#Function to check that system solutions are unique relative to one another (working on it)
#
def check_unique(best_systems):
	#the idea here is to first sort by the best systems
	#the iterate through them and check the difference of their splits

	unique_systems = []

	best_systems = sorted(best_systems, key = lambda x:x[1]) #make sure its all sorted
	for each_trial in range(len(best_systems)):

		#from here we need to go through whats already in the possible  solves

		#we need to check that this system is different enough

		should_continue = True

		for each_system in range(0, each_trial):

			if compare_systems(best_systems[each_trial][0], best_systems[each_system][0]) < 1.20: #the system splits are median 20% different

				should_continue = False

				break

		if should_continue:
			unique_systems.append(best_systems[each_trial])


	return unique_systems

#
#Function to analyse the results of the solver
#
def output_solver_results(inputs, best_systems, foldername):

	#lets output each system to a csv so we can see what the model came up with

	#print(run_own_regression(best_systems, 3))

	#first need to create the folder

	new_results_folder = pathlib.Path.cwd() / "cases" /  foldername / "results"

	new_results_folder.mkdir(parents=True, exist_ok=True)

	for each_case in range(len(best_systems)):

		output_system_csv(f"cases/{foldername}/results/case{each_case}.csv", best_systems[each_case])

	return

#
#we want a function that will take a system, a test case and run 
#
def simulate_system(system, sys_outputs, tolerance=100, sim_runtime=50):

	

	#now they are in the correct hourly format we can add them to the system

	system1 = copy.deepcopy(system)

	system1 = randomize_splits(system1, tolerance)

	#print([e.splits for e in system1.separators])

	system1.run(sim_runtime)

	final_state = system1.get_system_state()

	

	return system1, compare_system_outputs(sys_outputs, final_state)

#
#this function will simulate and compile results of one iteration of the solver for a specific system
#
def simulate_iteration(system, sys_outputs, trials, tolerance, tolerance_dec, sim_runtime):
	actual_results = []

	for each_trial in range(trials):

		temp_system = copy.deepcopy(system)

		end_system, trial_err = simulate_system(system, sys_outputs, tolerance, sim_runtime)

		actual_results.append(

			[end_system, trial_err]
			
		)

	#from here we need to determine which trials we should be following

	#this means looking for both the least error as well as different system definitions

	#we will search through the top 20% of results and then find ones that on average diff by x

	#first lets sort through the list

	actual_results = sorted(actual_results, key = lambda x: x[1]) #this sorts it so the start is lowest error

	#now lets get the top 20%

	top_pct = int(0.1*len(actual_results))

	#create a list to store the possible results to go through

	smallest_error = actual_results[0][1]

	possible_solves = [actual_results[0]]

	for each_trial in range(1, top_pct):

		#from here we need to go through whats already in the possible  solves

		#we need to check that this system is different enough

		should_continue = True

		for each_system in possible_solves:

			if compare_systems(each_system[0], actual_results[each_trial][0]) < 0.80: #the system splits are median 20% different

				should_continue = False

				break

		if should_continue:

			possible_solves.append(actual_results[each_trial])
	
	del actual_results #idk hopefully to save on memory

	#print(f"Possible Solves: {len(possible_solves)}")


	return possible_solves

#
#This function will run a simulation for one case
#
def simulate_case(system, sys_outputs, trials, tolerance=100,tolerance_dec=10, sim_runtime=500,max_systems = 5, target_error=0.05):

	original_tolerance = tolerance

	best_systems = [[copy.deepcopy(system)]]

	while tolerance > 0:

		print(f"\rDepth: {int((original_tolerance-tolerance)/tolerance_dec)+1}", end="", flush=True)

		#from here we need to go through each system in best_systems
		new_best_systems = []
		for each_system in range(len(best_systems)):

			best_systems[each_system][0].clear_slurries()

			temp_best_systems = simulate_iteration(best_systems[each_system][0], sys_outputs, trials, tolerance,tolerance_dec, sim_runtime)

			for e in temp_best_systems:

				new_best_systems.append(e)

			#best_systems.output_system()

		#now from here reduce the tollerance

		tolerance -= tolerance_dec
		trials -=0 #rgo down 10 pct each time

		#from here we want to check again that all the systems are unique

		best_systems = sorted(new_best_systems, key = lambda x:x[1])[:max_systems]

		#lets just check if the best system is below the target error so we can end the cycle and return what we have saving processing time

		if best_systems[0][1] < target_error*100:

			break

		#from here we want to add to the output of how many systems are being evaluated

		print(f"\tCurrent Possible Solves: {len(best_systems)}", end="", flush=True)

	#now here we have a best system

	#lets just clear the command line



	print("\r\x1b[K")

	return best_systems


#
#Function to run multiple cases through the solver
#
def solve_multiple_cases(system, mass_balance, foldername,trials=1000, tolerance=100,tolerance_dec=2,sim_runtime=25, target_error=0.05):

	#basically what we need to do is go through each test case,
	#run the simulation
	#collect the best system for the splits
	#create another function that will take all of these system definitions and their inputs
	#it will display how it thinks its working

	best_systems = []
	inputs = []

	for each_case in mass_balance:

		print(f"\rEvaluating Case {mass_balance.index(each_case)+1}")

		#just define and create deepcopies so that nothing gets messed up

		copy_system = copy.deepcopy(system)

		copy_inputs = copy.deepcopy(each_case[0])

		copy_outputs = copy.deepcopy(each_case[1])

		#now add the inputs

		copy_system = add_inputs(copy_system, copy_inputs)

		#now give it default splits to work with
		#old now we do that when we load the mass balance

		#from here run the simulation

		best_system_s = simulate_case(copy_system, copy_outputs, trials=trials, tolerance=tolerance, tolerance_dec = tolerance_dec, sim_runtime=sim_runtime,max_systems = 10, target_error=target_error)

		best_system_s = sorted(best_system_s, key = lambda x:x[1])

		best_system = best_system_s[0][0]

		print(f"\r\x1b[KEvaluated Case {mass_balance.index(each_case)+1}")

		print("\nFound System:\n")

		print(f"{best_system}\n")

		print(f"^^^System Error {best_system_s[0][1]}\n")

		#from here append to the best systems and inputs

		best_systems.append(best_system)

		inputs.append(copy_inputs)

	#from here we have collected all of the best_system and their corresponding inputs

	#we throw it in a function that will output how this works

	output_solver_results(inputs, best_systems, foldername)

	return

#
#Function to my regression analysis on the outputs of the solver
#
def run_regression_analysis(foldername):

	#we want the feature names for better output in the regression

	feature_names = get_feature_names(foldername)

	separator_feature_names = get_separator_names(foldername, feature_names)

	data = []

	for each_case in range(12):

		data.append(
			get_solver_results_csv(f"cases/{foldername}/results/case{each_case}.csv", feature_names)
		)

	sources, splits = prep_solver_results(data)

	

	print("Running Multiple Regression...\n")

	return run_all_regression(sources, splits, feature_names, separator_feature_names)

#
#Function to create and run a model on new data based on the solver and regression (work in progress)
#
def simulate_new_inputs(inputname,foldername, modelname = None):

	#this function will have to take the the new inputs
	# 1. Run regression on the specified system
	# 2. Solve for the splits with regression
	# 3. Define the system
	# 4. Run the system simulation (throw warning if outside of training bounds)
	# 5. Return the mass balance with these new inputs

	if modelname != None:

		model_save_name = "modelling/models/" + modelname

		with open(model_save_name, "rb") as file_obj:

			load_package = pickle.load(file_obj)

		file_obj.close()

		all_equations, chosen_feature_names = load_package[0], load_package[1]

	else:

		all_equations, chosen_feature_names = run_regression_analysis(foldername) #this gets all of the best defined equations from the analysis

	sources = load_new_inputs_csv(inputname)

	feature_names = get_feature_names(foldername)

	#convert the sources

	new_X = []

	for each_src in sources.keys():

		total = sum(sources[each_src])

		for each_feature in sources[each_src]:

			new_X.append(round(each_feature/total, 8)) #this is because of how inputs need to be for the regression model

	new_X = np.array([new_X])

	#from here have to get all of the same features as the analysis
	#the pick it apart for the chosen features for the models

	#copied from the my solver file
	data_variants = [
		get_polynomial_data(new_X, feature_names, degree=2),
		get_exponential_inputs(new_X, feature_names),
		get_negative_exponential_inputs(new_X, feature_names),
		get_logarithmic_data(new_X, feature_names)
	]

	#now from here we get the extended feature_names    

	new_X, feature_names = combine_data_variants(data_variants)

	#now we need to condense this

	#copied from the solver file
	chosen_feature_indexes = []

	for e in chosen_feature_names:

		chosen_feature_indexes.append(feature_names.index(e))

	#now from here we have to get the correct features used in the model found

	new_sources = []

	for each_case in range(len(new_X)):

		new_sources.append(new_X[each_case][chosen_feature_indexes])

	new_sources = np.array(new_sources)

	#now from here we have the sources and can define the splits better

	for each_sep in all_equations.keys():

		for each_outflow in all_equations[each_sep].keys():

			for each_feature in all_equations[each_sep][each_outflow].keys():

				model = all_equations[each_sep][each_outflow][each_feature][2] #get the model

				recovery = model.predict(new_sources)

				all_equations[each_sep][each_outflow][each_feature].append(recovery[0])

	#from here we need to setup up the system,

	system, mass_balance = load_entire_system(foldername)

	#run it with a long runtime

	#need to make new_sources ready to be added to the system

	system = add_inputs(system, sources) #give it the sources

	#now from here need to input the calculated splits

	system = add_splits_from_regression(system, all_equations)

	#now run the system

	runtime = int(input("Input Simulation Runtime (higher numbers > 100 for complex systems): "))

	system.run(n = runtime)

	#output the results to a csv and done!

	#now just come up with filename

	filename = inputname.split(".")[0] + "_results.csv" #adjust the input name to make one identical but with the results

	filename = f"modelling/outputs/{filename}"

	output_system_csv(filename, system)

	print(f"System Ran and output to {filename}")



	return


#
#Main Function to take user input from the command line to run things
#
def main():

	#first need to determine if user is solving or analyzing a system

	#if solving then need to get inputs required for running the system

	#if analysing then just get the name of the case and should be good

	#will need to do a fair bit of error handling

	#start a mainloop

	running = True

	while running:

		mode = input("Please Select a Mode: (S)olver / (A)nalysis / (M)odel / (Q)uit: ")

		if mode in ["S","s", "Solver","solver"]:

			#in the case of solving we still need a foldername
			#lets print out what the options are

			print_usable_cases()

			foldername = input("Please Input the Case Foldername: ")

			system, mass_balance = load_entire_system(foldername)

			#define some default values to run the simulation with

			trials=200
			tolerance=100
			iterations = 20
			tolerance_dec=tolerance/iterations
			sim_runtime=25
			target_error=0.05

			#now from here we want to check if the users want to use the defaults

			run_defaults = input("Run Solver with Default values?: (Y)es / (N)o: ")

			if run_defaults in ["Y", "y", "Yes", "yes"]:

				solve_multiple_cases(system, mass_balance, foldername, trials=1000, tolerance=100,tolerance_dec=2,sim_runtime=25, target_error = 0.05)

			elif run_defaults in ["N", "n", "No", "no"]:

				#in this case we need to take more input about how they want to run their simulation

				trials = int(input("How many Trials per Iteration (Default 200): "))

				while trials < 0:

					print("Error: Invalid Input")

					trials = int(input("How many Trials per Iteration (Default 200): "))

				iterations = int(input("How many Iterations (Default 20): "))

				while iterations < 0:

					print("Error: Invalid Input")

					iterations = int(input("How many Iterations (Default 20): "))

				#from here convert this to a tolerance decrease

				tolerance_dec = tolerance/iterations

				sim_runtime = int(input("Input Simulation Runtime (Default 25): "))

				while sim_runtime < 0:

					print("Error: Invalid Input")

					sim_runtime = int(input("Input Simulation Runtime (Default 25): "))

				target_error = float(input("Input Simulation Target Error (Default 5%): "))/100

				while target_error < 0:

					print("Error: Invalid Input")

					target_error = float(input("Input Simulation Target Error (Default 5%): "))/100

				solve_multiple_cases(system, mass_balance, foldername, trials, tolerance,tolerance_dec,sim_runtime, target_error)

			print("Solver Finished.\n")

		elif mode in ["A", "a", "Analysis", "analysis"]:

			#in the case of analysis all we need is the folder name

			print_usable_cases() #print out the possible cases

			foldername = input("Please Input the Case Foldername: ")

			#run_defaults = input("Run Solver with Default values?: (Y)es / (N)o: ")

			#if run_defaults in ["Y", "y", "Yes", "yes"]:

			run_regression_analysis(foldername)

			#elif run_defaults in ["N", "n", "No", "no"]:

				#pass

			print("Analysis Finished.\n")

		elif mode in ["M", "m", "Model", "model"]:

			#in this case we need to model with mass balance inputs, using a specific system definition

			#first get the filename of the desired mass balance inputs

			print_usable_model_inputs()

			inputname = input("Please Input the input file name: ")

			print_usable_cases()

			foldername = input("Please Input the Case Foldername: ")

			

			#now check if they already trained a model

			use_model = input("Do you want to load a model (Y)es / (N)o : ")

			if use_model in ["Y", "y", "Yes", "yes"]:

				print_usable_models()

				model_name = input("Input Model File Name: ")

				simulate_new_inputs(inputname, foldername, model_name)

			elif use_model in  ["N", "n", "No", "no"]:

				simulate_new_inputs(inputname, foldername)

			print("Modelling Finished.\n")


		elif mode in ["Q", "q", "Quit", "quit"]:

			running = False

		else:

			print("Error: Invalid Selection")

	print("Program Exiting...")


	return

if __name__ == "__main__":

	st = time.time()

	main()

	et = time.time()

	print(f"Program Total Runtime: {round(et-st, 4)}s")

