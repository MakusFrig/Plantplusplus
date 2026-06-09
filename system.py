#This file holds the System Object and the simulation method
import copy

from objects import *


class System:

	def __init__(self, sources, seperators, collectors):

		self.seperators = seperators

		self.seperators_names = [e.name for e in self.seperators]

		self.collectors = collectors

		self.collectors_names = [e.name for e in self.collectors]

		self.sources = sources

		self.sources_names = [e.name for e in self.sources]

		return

	def __repr__(self):

		return f"{self.sources}\n{self.seperators}\n{self.collectors}"

	def run(self, n):



		#basically we need to go through and do things in a specific order
		#0. Input from all the sources
		#1. mix all of the input slurries in the seperators + collectors
		#2. run the seperations
		#3. clear all of the inputs in the seperators
		#4. output the seperators to the other seperators or collectors
		#5. repeat n times

		for each_iter in range(n):

			for each_source in self.sources:

				#we then need to go through the seperators and collectors until we find the destination name

				#create a variable to tell us if we found the destination of the slurry
				found_dest = False

				for each_name in range(len(self.seperators_names)):

					if self.seperators_names[each_name] == each_source.dest:

						#in this case we found the destination and have the index of the where the source is

						#this creates a slurry proportional to trials
						#you need to do this basically to improve accuracy of seperating
						#more so for complex system and small n but otherwise it will
						#input the monthly slurry as the "hourly" or wtv you set n to
						portion_slurry = [i/n for i in each_source.slurry] 

						self.seperators[each_name].add_slurry(portion_slurry)

						found_dest = True

						break

				#now we check if we found the destination and if not then we search through the collectors

				if not found_dest:

					for each_name in range(len(self.collectors_names)):

						if self.collectors_names[each_name] == each_source.dest:

							#in this case this source is going to a collector for some reason

							portion_slurry = [i/n for i in each_source.slurry] 

							self.collectors[each_name].add_slurry(portion_slurry)

							found_dest = True

							break

				#from here if we havent found the destinatino then we want to return an error

				if not found_dest:

					print("Error: Source does not connect to a Seperator or a Collector")

					return



			#from here we have completed step 0 and have added slurries from the sources

			#from here we go to step 1 and mix all of the input slurries in the seperators and collectors

			for each_sep in range(len(self.seperators)):

				self.seperators[each_sep].create_input()

			for each_col in range(len(self.collectors)):

				self.collectors[each_col].mix()

			#from here we have completed step 1 and mixed all of the input slurries

			#from here we go to step 2 and seperate everything

			for each_sep in range(len(self.seperators)):

				self.seperators[each_sep].seperate()

			#from here we have completed step 2 and seperated all of the input slurries

			#now we go to step 3 and eliminate the input to all the collectors and seperators

			for each_sep in range(len(self.seperators)):

				self.seperators[each_sep].clear_inputs()

			for each_col in range(len(self.collectors)):

				self.collectors[each_col].clear_inputs()

			#from here step 3 is complete and all of the inputs are empty

			#now we go to step 4 and add the outputs from the seperators to the inputs and their destinations

			#we need to loop through the seperators, then loop through the rest of the system to identify destinations and add them

			for each_sep in range(len(self.seperators)):

				#now we need to go through the destinations (will work with 2 or 3)

				

				temp_sep = self.seperators[each_sep]

				#from here we iterate through the destinations

				for ind1 in range(temp_sep.num_outflows):

					if temp_sep.destinations[ind1] in self.seperators_names:

						#in this case we output to another separator

						dest_index = self.seperators_names.index(temp_sep.destinations[ind1])

						self.seperators[dest_index].add_slurry(temp_sep.output_slurries[ind1])

					elif temp_sep.destinations[ind1] in self.collectors_names:

						dest_index = self.collectors_names.index(temp_sep.destinations[ind1])

						self.collectors[dest_index].add_slurry(temp_sep.output_slurries[ind1])

					else:

						print("Error: Defined destination does not exist in the simulation")

						return


			#from here we have completed step 4 and can continue in the loop

		#now from here everything has run and the system is in its final state
		#need to return the system
		return copy.deepcopy(self)
		

	def get_system_state(self):
		system_state = {}

		for each_name in range(len(self.collectors_names)):

			system_state[self.collectors_names[each_name]] = [round(e, 3) for e in self.collectors[each_name].slurry]

		#from here we want to convert the lists to percentages
		"""
		for each_name in system_state.keys():

			total = sum(system_state[each_name])

			for each_type in range(len(system_state[each_name])):

				

				system_state[each_name][each_type] /= total
		"""
		return system_state




	#this function will go through the seperators, collectors, sources and print out the information of the system
	def output_system(self):

		#start by outputting info about the sources

		for each_source in self.sources:

			print(f"Source    - Name:{each_source.name} Slurry:{each_source.slurry}")

		for each_sep in self.seperators:

			print(f"Seperator - Name:{each_sep.name}")

			for each_split in each_sep.splits:

				print(f"\tSplit:{[round(e, 2) for e in each_split]}")

		for each_col in self.collectors:

			print(f"Collector - Name:{each_col.name} Slurry:{[round(e, 2) for e in each_col.slurry]}")

		return


	#we need a function that clears everything except the inputs and splits

	def clear_slurries(self):

		for each_s in self.seperators:

			each_s.clear_slurries()

		#now the collectors

		for each_c in self.collectors:

			each_c.clear_slurries()

		return

