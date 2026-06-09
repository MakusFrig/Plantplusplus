#this is a simulation for seperating fluids

"""
TODO LIST
1. improve algo for solving, create branches for top k nodes
2. add support for multi output seperators
3. create framework for one system, multiple inputs (months of data)
4. create gui with pyqt probably

"""

import random

import copy

import sys

import time

import os

from objects import *

from system import *

from util import *

from solver import *

import matplotlib.pyplot as plt

import numpy as np

from numba import njit, prange

from multiprocessing import Pool


#ray.init()

#this function will generate a random split to be used
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

#this function will generate a random split to be used
def get_random_splits(splits, tolerance=10):

	#need to define a way to generate random splits

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

def randomize_splits(system, tolerance=100):

	for each_s in range(len(system.seperators)):



		old_splits = system.seperators[each_s].splits

		new_splits = get_random_splits(old_splits, tolerance)



		system.seperators[each_s].set_splits(copy.deepcopy(new_splits))




	return system

#this function will compare the two results
def compare_states(real_state, predicted_state):

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


#we want a function that will take a system, a test case and run 
def run_system_sim(system, sys_outputs, tolerance=100, sim_runtime=500):

	

	#now they are in the correct hourly format we can add them to the system

	system1 = copy.deepcopy(system)

	system1 = randomize_splits(system1, tolerance)

	#print([e.splits for e in system1.seperators])



	system1.run(sim_runtime)

	final_state = system1.get_system_state()

	

	return system1, compare_states(sys_outputs, final_state)

def load_system(sys_filename, tc_filename, file_type="json",hours=24*30):

	if file_type == "json":

		system = get_system_json(sys_filename)

	elif file_type == "csv":

		system = get_system_csv(sys_filename)

	sys_inputs, sys_outputs = get_testcase_csv(tc_filename, system)

	#from here we have a system, the desired inputs, outputs

	#assuming monthly we want to alter the slurries for the inputs so they can run on an hourly basis

	#this means dividing by the hours

	sys_inputs = divide_slurries(sys_inputs, hours)

	system = add_inputs(system, sys_inputs)

	print(f"System Check:{check_system(system)}")

	give_default_splits(system)

	return system, sys_inputs, sys_outputs

#this function will take a test case thats in a folder, two files a massbalance and a system_def
def load_entire_system(foldername, hours= 500):

	#now we want to extract this

	system = get_system_csv(f"test_cases/{foldername}/system_def.csv")

	mass_balance, system = get_mass_balance_csv(f"test_cases/{foldername}/mass_balance.csv", system)

	return system, mass_balance

#this funciton has the while loop
def simulation_ray(system, sys_outputs, trials, tolerance=100,tolerance_dec=10, sim_runtime=500,max_systems = 5):

	original_tolerance = tolerance

	

	best_systems = [[copy.deepcopy(system)]]

	while tolerance > 0:

		print(f"\rDepth: {int((original_tolerance-tolerance)/tolerance_dec)+1}", end="", flush=True)

		#from here we need to go through each system in best_systems
		new_best_systems = []
		for each_system in range(len(best_systems)):

			best_systems[each_system][0].clear_slurries()

			temp_best_systems = compile_results(best_systems[each_system][0], sys_outputs, trials, tolerance,tolerance_dec, sim_runtime)

			for e in temp_best_systems:

				new_best_systems.append(e)

			#best_systems.output_system()

		#now from here reduce the tollerance

		tolerance -= tolerance_dec
		trials -=0 #rgo down 10 pct each time

		#from here we want to check again that all the systems are unique

		best_systems = sorted(new_best_systems, key = lambda x:x[1])[:max_systems]

		#from here we want to add to the output of how many systems are being evaluated

		print(f"\tCurrent Possible Solves: {len(best_systems)}", end="", flush=True)

	#now here we have a best system

	#lets just clear the command line



	print("\r\x1b[K")

	return best_systems

#
#Function to check that system solutions are more or less unique
#
def check_unique(best_systems):
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

#this function will compile all of the numba results from one loop
def compile_results(system, sys_outputs, trials, tolerance, tolerance_dec, sim_runtime):
	actual_results = []

	for each_trial in range(trials):

		actual_results.append(
			evaluate_trial((system, sys_outputs, tolerance, sim_runtime))
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
	del actual_results

	#print(f"Possible Solves: {len(possible_solves)}")


	return possible_solves

#this function does the evaluation for numba
def evaluate_trial(args):
	system, sys_outputs, tolerance, sim_runtime = args
	temp_system = copy.deepcopy(system)
	end_system, trial_err = run_system_sim(system, sys_outputs, tolerance, sim_runtime)
	return [end_system, trial_err]

def regression_trial(foldername):

	data = []

	for each_case in range(12):

		data.append(
			input_system_results_csv(f"test_cases/{foldername}/results/case{each_case}.csv")
		)

	sources, splits = prep_csv_data(data)

	#we also want the feature names for better output in the regression

	feature_names = get_feature_names(foldername)

	separator_feature_names = get_separator_names(foldername, feature_names)

	print("Running Multiple Regression...\n")

	run_all_regression(sources, splits, feature_names, separator_feature_names)





def analyse_system(inputs, best_systems, foldername):

	#lets output each system to a csv so we can see what the model came up with

	#run_MLP_regression(best_systems)

	#print(run_own_regression(best_systems, 3))

	#first need to create the folder

	os.makedirs(f"test_cases/{foldername}/results", exist_ok=True)

	for each_case in range(len(best_systems)):

		output_system_csv(f"test_cases/{foldername}/results/case{each_case}.csv", best_systems[each_case])



	#lets start by just trying to analyse the ore

	"""x = np.array([])
				y = np.array([])
			
				for each_case in range(len(inputs)):
			
					#x is the inputs so we look to find the source
			
					target_input = inputs[each_case][source_name][slurry_index]
			
					
			
					collector_index = best_systems[each_case].collectors_names.index(collector_name)
			
					target_output = best_systems[each_case].collectors[collector_index].slurry[slurry_index]
					target_recovery = target_output/target_input
			
					x = np.append(x, target_input)
			
					y = np.append(y, target_recovery)
			
				#from here lets put this in a plot and show it
			
				plt.scatter(x, y)
				plt.show()"""

	return

#
#Function to run multiple cases
#Need to turn this into a parrallel process
#
def run_multiple(system, mass_balance, foldername,trials=1000, tolerance=100,tolerance_dec=2,sim_runtime=25):

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

		best_system_s = simulation_ray(copy_system, copy_outputs, trials=trials, tolerance=tolerance, tolerance_dec = tolerance_dec, sim_runtime=sim_runtime,max_systems = 10)

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

	analyse_system(inputs, best_systems, foldername)

	return

if __name__ == "__main__":

	st = time.time()

	#system, mass_balance = load_entire_system("test_case_1")

	#run_multiple(system, mass_balance, "test_case_1")

	regression_trial("test_case_4")

	et = time.time()

	print(f"Program Ran in {round(et-st, 4)}s")

	#main("mysystem2.json", "testcases/testcasenew1.csv")