#this file stores all the objects and their functions


class Seperator:

	def __init__(self, name, destinations=["", "", ""], splits=[]):

		self.name = name

		self.input_slurries = [] #this is a list of slurries, will constantly be updated

		self.input = None

		self.overflow = [] #this will be a slurry
		self.middleflow= []
		self.underflow = []

		if "" in destinations:

			destinations.remove("")

		self.destinations = destinations



		self.output_slurries = [[] for _ in range(len(destinations))]



		#now we define their destinations
		if len(destinations) == 0 or destinations == None:

			print("No Destinations Given")

			return
		else:

			self.destinations = destinations

		self.num_outflows = len(destinations)






		

		self.splits = splits

	def __repr__(self):

		

		return f"{self.name}\nDestinations:{self.destinations}\nSplits:{self.splits}"

	#this function will add a destination
	def set_destination(self, dest_index, destination):



		self.destinations[dest_index] = destination


		#need to make sure to update the number of outflows

		self.num_outflows = len(self.destinations)




	#this function will add a slurry to the seperators input slurries
	def add_slurry(self, input_slurry):

		self.input_slurries.append(input_slurry)

		return

	def set_splits(self, splits):

		self.splits = splits

		return

	#this function will take all the slurries in the input and mix them together
	def create_input(self):

		#self.slurry_length = len(self.input_slurries[0])

		self.input = [0 for i in range(self.slurry_length)]

		for each_slurry in self.input_slurries:

			for i in range(self.slurry_length):

				self.input[i] += each_slurry[i]


		return


	def clear_inputs(self):

		self.input_slurries = []

		self.input = None

		return

	def clear_slurries(self):

		#need to use loops because the slurry length can vary

		

		self.output_slurries = [[0 for i in range(self.slurry_length)] for _ in range(self.num_outflows)]

		return

	#this function will seperate whatever is the input
	def seperate(self):

		#this will work regardless of 2 or 3 destinations

		for ind1 in range(self.num_outflows):

			self.output_slurries[ind1] = []

			for each_comp in range(len(self.input)):



				temp_amount = self.input[each_comp] * self.splits[ind1][each_comp]

				



				self.output_slurries[ind1].append(temp_amount)



		return

#a source just holds one slurry and supplies it to a seperators or something
class Source:

	def __init__(self, name, destination=None, slurry=[]):

		self.name = name

		self.slurry = slurry

		self.dest = destination

	def __repr__(self):

		return f"{self.name}\nDestination:{self.dest}\nSlurry:{self.slurry}"

	def set_slurry(self, new_slurry):

		self.slurry = new_slurry

		return

	def set_destination(self, destination):

		self.dest = destination



#a collector is the last line in the chain and will just accumulate the slurry
class Collector:

	def __init__(self, name):

		self.name = name

		self.input_slurries = []

		



	def __repr__(self):

		return f"{self.name}\nSlurry:{[round(i, 3) for i in self.slurry]}"


	#this function will just add a slurry
	def add_slurry(self, slurry):

		self.input_slurries.append(slurry)

		return

	def set_slurry(self, slurry):

		self.slurry = slurry

	def mix(self):


		for each_slurry in self.input_slurries:

			for e in range(len(self.slurry)):

				self.slurry[e] += each_slurry[e]



		return

	def clear_inputs(self):

		self.input_slurries = []

		return

	def clear_slurries(self):

		for i in range(len(self.slurry)): #need to use the loop because slurry size can vary

			self.slurry[i] = 0

		return