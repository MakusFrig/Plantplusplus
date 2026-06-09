#this is a util file to deal with better input and output
import csv

import json

import numpy as np

from objects import *

from system import *

#define some global variables here

DEFAULT_SPLITS = [
	[0.5, 0.5, 0.5],
	[0.5, 0.5, 0.5]
]

#Function to fetch inputs and outputs for a mass balance system
def get_mass_balance_csv(filename, system):
		
	#before we start seaching we want to make sure were only looking at valid data

	valid_sources = system.sources_names

	valid_separators = system.seperators_names #this is important for setting the default splits later

	valid_collectors = system.collectors_names	
	#first get an object

	file_obj = open(filename, "r")

	reader = csv.reader(file_obj)

	test_cases = []

	temp_data = []

	inputs = dict.fromkeys(valid_sources)

	outputs = dict.fromkeys(valid_collectors)

	#when we go through we want to keep track that all the define slurries are the same length
	#assuming they are we need to make sure the separators default splits are designed for this

	slurry_length = None

	for row in reader:

		#basically each "month" starts with the word data

		if row[0] == "data":

			#here we want to append the dat because this signifies the end of a testcase massbalance

			#first check that there is data to append



			temp_data = [inputs, outputs]

			test_cases.append(temp_data)

			temp_data = []

			inputs = dict.fromkeys(valid_sources)

			outputs = dict.fromkeys(valid_collectors)

		else:

			if row[0] in valid_sources:

				#in this case we have a row with data

				inputs[row[0]] = [float(i) for i in row[1:]]

				if len(inputs[row[0]]) != slurry_length and slurry_length != None:

					print("Error: Not all slurry lengths match")

				elif len(inputs[row[0]]) != slurry_length:

					slurry_length = len(inputs[row[0]])



			elif row[0] in valid_collectors:

				outputs[row[0]] = [float(i) for i in row[1:]]

				if len(outputs[row[0]]) != slurry_length and slurry_length != None:

					print("Error: Not all slurry lengths match")

				elif len(outputs[row[0]]) != slurry_length:

					slurry_length = len(outputs[row[0]])
	#now from here we need to go through the systems separators and give them the default splits
	system = give_default_splits(system, slurry_length)


	#also need to go through and make sure the collectors have the correct slurry length
	system = give_defualt_collector_slurry(system, slurry_length)

	return test_cases, system

#we want a function that takes a csv that defines the system
def get_system_csv(filename):

	file_obj = open(filename, "r")

	reader = csv.reader(file_obj)





	#from here we have each entry, now we need to go through and create the system

	#create blank arrays to return later
	system_sources, system_seperators, system_collectors = [], [], []

	for row in reader:

		row  = [x for x in row if x != ''] #get rid of the blanks

		if row[0] == "source":

			src_name = row[1] #source name

			src_dest = row[2] #source destination

			src_slurry = [int(e) for e in row[3:]]

			system_sources.append(
				Source(src_name, src_dest)
			)

		elif row[0] == "seperator":

			sep_name = row[1] #seperator name

			sep_dests = row[2:]

			system_seperators.append(
				Seperator(sep_name, sep_dests)
			)


		elif row[0] == "collector":

			col_name = row[1]

			system_collectors.append(
				Collector(col_name)
			)

		else:

			print("Error reading CSV file")

			return

	file_obj.close()


	return System(system_sources, system_seperators, system_collectors)

#this function will get a system from a json file
def get_system_json(filename):

	file_obj = open(filename, "r")

	data = json.load(file_obj)

	#now from here we have data which is a dictionary of 'nodes' and 'edges'

	nodes = data["nodes"]
	edges = data["edges"]

	system_collectors = []

	system_seperators = []

	system_sources = []

	#start by iterating through the nodes

	for each_node in nodes:

		#check what type it is

		if each_node["type"] == "Plant.SourceNode":


			#we have a source

			system_sources.append(
				Source(each_node["name"]) #we dont need to do the destination yet
			)

			#we also generally have a slurry in the data

			temp_slurry = list(each_node["data"].values())

			#now set the slurry

			system_sources[len(system_sources)-1].set_slurry(temp_slurry)

		elif each_node["type"] == "Plant.SeparatorNode":

			

			#we have a seperator

			system_seperators.append(
				Seperator(each_node["name"])
			)

			#from here we want to get the splits and add those

			temp_splits = list(each_node["data"].values())

			#now we have splits but need to transpose them

			temp_splits = list(map(list, zip(*temp_splits)))

			system_seperators[len(system_seperators)-1].set_splits(temp_splits)



		elif each_node["type"] == "Plant.CollectorNode":

			#we have a collector

			system_collectors.append(
				Collector(each_node["name"])
			)

			temp_slurry = list(each_node["data"].values())

			#now set the slurry

			system_collectors[len(system_collectors)-1].set_slurry(temp_slurry)

		else:
			

			print("Error: Node of Unknown Type")

	#from here we create name lists 

	#now from here we iterate through the edges and add these destinations

	for each_edge in edges:

		#we iterate through the sources

		edge_start = each_edge["from"].split(":")[0]

		edge_start_output = each_edge["from"].split(":")[1]

		edge_end = each_edge["to"].split(":")[0]

		edge_end_input = each_edge["to"].split(":")[1]

		is_src = False

		for each_src in system_sources:

			if each_src.name == edge_start:

				#now we have which source is coming from

				each_src.set_destination(edge_end)

				is_src = True

				break

		#now check if it was a src

		if is_src:

			continue

		#otherwise we check the collectors which is more tricky

		is_sep = False

		for each_sep in system_seperators:

			if each_sep.name == edge_start:

				#now we have which seperator its coming from

				#from here we need to figure out which output it is from the seperator

				destination_index = int(edge_start_output[6:])-1



				each_sep.set_destination(destination_index, edge_end)

				

				is_sep = True

				break

		#now check if it was a separator

		if is_sep:

			continue

		else:

			print("Error: Edge has Unknown Start/Finish")

			return


	#from here lets output our system

	



	return System(system_sources, system_seperators, system_collectors)

#this function will get a testcase with slurry data for the system inputs and expected outputs
def get_testcase_csv(filename, system):

	#create two dictionaries that will be returned seperatley

	inputs = dict.fromkeys(system.sources_names)

	outputs = dict.fromkeys(system.collectors_names)

	file_obj = open(filename, "r")

	reader = csv.reader(file_obj)

	



	

	#now we iterate through the rows of the test case and

	for row in reader:

		row  = [x for x in row if x != ''] #get rid of the blanks

		

		#now we need to iterate through the sources and collectors to determine where to append this to

		if row[0] in system.sources_names:

			inputs[row[0]] = [int(e) for e in row[1:]]


		elif row[0] in system.collectors_names:

			outputs[row[0]] = [int(e) for e in row[1:]]


		#QAQC if its in neither
		else:

			print("Error: Testcase not in Sources or Collectors")

			print(f"Error row:{row}")

			return

	file_obj.close()

	return inputs, outputs

#This function will take the inputs from a testcase and add them to a system
def add_inputs(system, inputs):

	#inputs are a dictionary, keys = source names, items = slurries

	for each_i in inputs.keys():

		src_index = system.sources_names.index(each_i) #the index in the list of sources that we want to target

		system.sources[src_index].set_slurry(
			inputs[each_i]
		)



	return system

#this funciton will go through a dictionary of slurries and divide each number
#mostly used for turning daily totals to hourly inputs etc
def divide_slurries(slurries, x):

	for each_s in slurries.keys():

		slurries[each_s] = [round(i/x, 3) for i in slurries[each_s]]

	return slurries


#This function will check that each slurry is the same length
def check_system(system):

	slurry_length = len(system.sources[0].slurry)

	#now we have one of hte lengths we iterate through all collectors and sources to make sure they match

	for each_s in system.sources:

		if len(each_s.slurry) != slurry_length:

			print("Error: System has varying slurry elements")

			return False

	for each_c in system.collectors:

		if len(each_c.slurry) != slurry_length:

			print("Error: System has varying slurry elements")

			return False

	return True

#This function will give default splits
def give_default_splits(system, slurry_length):

	DEFAULT_SPLITS = [
		[0.5, 0.5, 0.5],
		[0.5, 0.5, 0.5]
	]

	for each_s in range(len(system.seperators)):

		temp_outflows = system.seperators[each_s].num_outflows

		temp_split = [
			[0.5 for e in range(slurry_length)] for i in range(temp_outflows)
		]

		system.seperators[each_s].set_splits(temp_split)

		#the other thing we want to do here is save the slurry length

		system.seperators[each_s].slurry_length = slurry_length


	return system

#A helper function to get the slurry feature names
def get_feature_names(foldername):

	file_obj = open(f"test_cases/{foldername}/mass_balance.csv")

	csv_reader = csv.reader(file_obj)

	for row in csv_reader:

		feature_names = row[1:]

		break #break here because the feature names are all in the first row
	return feature_names

#A helper function to get the separator names
def get_separator_names(foldername, feature_names):

	num_features = len(feature_names)

	file_obj = open(f"test_cases/{foldername}/system_def.csv")

	csv_reader = csv.reader(file_obj)

	separator_names = {}

	for row in csv_reader:

		if row[0] == "seperator":

			name = row[1]

			num_outflows = len(row[2:])

			separator_names[name] = num_outflows #this is just the number of outflows
	#from here need to construct separator_feature_names for each separator, each outflow and each feature

	separator_feature_names = []

	for each_sep in separator_names.keys():

		for each_outflow in range(separator_names[each_sep]):

			for each_feature in feature_names:

				separator_feature_names.append(
					#here we constrcut what the "y" feature name will be
					f"{each_sep}>Outflow{each_outflow+1}>{each_feature} Recovery"
				)


	return separator_feature_names

#This function will give default 0s to the collectors fo slurry length
def give_defualt_collector_slurry(system, slurry_length):

	for each_c in range(len(system.collectors)):

		system.collectors[each_c].set_slurry([0 for i in range(slurry_length)])

	return system

#This function will take a filename and unpack it and return a system
def input_system_results_csv(filename):

	csv_data = []

	file_obj = open(filename, "r")

	csv_reader = csv.reader(file_obj)

	for row in csv_reader:

		csv_data.append(row)



	#now from here we go through and extract the data about the sources and separators

	on_type = "source" #set a tracker for what type of source we are extracting

	slurry_length = 0

	sources = []

	splits = []

	for each_row in csv_data:

		if each_row == []:

			#skip blank rows from the csv file

			continue

		if on_type == "source":

			#this is default so we want to check if its changed

			if len(each_row)-1 > slurry_length and sources != []: #basically check if its the start

				#then in this case we need to switch it to separators

				on_type = "separators"

			else:

				#in this case we need to append a new value of the source to the sources array

				slurry_length = len(each_row)-1

				for i in each_row[1:]:

					sources.append(float(i))

				

		if on_type == "separators":

			#lets check if we've moved on from the separators

			if len(each_row)-1 == slurry_length:

				#in this case this line is a collector and we need to stop

				break

			else:

				#in this case we want to add the separator splits

				for i in each_row[1:]:

					#need to get all the splits in case of 3+ outflows
					#each split will then need to be calculated

					splits.append(float(i))

				

	#from here we have all the splits and sources and return them

	return sources, splits


#This function will take a system and package a csv with the splits used
def output_system_csv(filename, system):

	#first create an array that will output this all to csv

	csv_data = []

	#now iterate through the collectors and populate the output list

	for each_src in range(len(system.sources)):

		temp_slurry = system.sources[each_src].slurry

		csv_data.append([system.sources_names[each_src]] + temp_slurry)

	for each_s in range(len(system.seperators)):

		flat_splits = []

		for each_split in range(len(system.seperators[each_s].splits)):

			temp_splits = system.seperators[each_s].splits

			flat_splits += temp_splits[each_split]



		csv_data.append(
			[system.seperators_names[each_s]] + flat_splits
		)

	for each_c in range(len(system.collectors)):

		temp_slurry = system.collectors[each_c].slurry

		csv_data.append([system.collectors_names[each_c]]+ temp_slurry)

	#from here we have a fully populate list no write it to a file

	file_obj = open(filename, "w")

	writer = csv.writer(file_obj)

	writer.writerows(csv_data)

	print(f"Output Best System to {filename}")

	file_obj.close()

	return True

#
#Function to compare how the splits in each system are
#
def compare_systems(system1, system2):

	#all differences will be compared to system1

	differences = []

	for each_sep in range(len(system1.seperators)):

		for each_quality in range(len(system1.seperators[each_sep].splits[0])):

			temp_diff = abs(system1.seperators[each_sep].splits[0][each_quality]-system2.seperators[each_sep].splits[0][each_quality])

			

			temp_diff /= max(system1.seperators[each_sep].splits[0][each_quality], 0.00001) #need to have something to avoid 0 error
			#remember to divide to get in % as the systems get compared as a percentage not absolute difference

			differences.append(temp_diff)


	#from here we have an array with all of the differences each system has in splits in % form

	#we want to get the median

	return np.median(np.array(differences))


if __name__ == "__main__":

	print(get_system_json("mysystem2.json"))