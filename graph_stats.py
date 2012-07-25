"""
UPDATE:  July 2012, Created this file from gen_graph.py for collecting statistics about bounded graphs
of the collatz conjecture relations.  Basically the 'bounded graphs' in question are just displaying 
all numbers that terminate in 1 where all of the odd numbers in their Collatz sequence are bounded by 
B bits or 2^B for some B.

UPDATE:  Parallel version added which can use py.cloud.  

TODO:  Load level parallel version designed to use py.cloud so that work is equally distributed. 

TODO:  Refactor code to clean it up.


The 3n+1 conjecture also known as the Collatz conjecture:

The function f:N->N  (N is n\in Z for n>0)

		
f(n) = 3n+1 if n is odd
		n/2 if n is even
		
The conjecture is that the sequence you get by repeated applying this function
to any integer converges to one.

Notes:  We are looking at the idea that we want to consider all numbers that are
one 3n+1 computation away from 1, and then those that are 2 3n+1 computations away
from 1.  Further more we will classify odd numbers by their 'level', namely the number 
of times 3n+1 occurs as a step in the sequence converging to 1.

EXAMPLES:

Level 0		1
Level 1		5	21	85	341	
Level 2		3	13	53	213..
			113	453	1813	7253
			227	909	3637	1459...
			...
Level 3		17	69	277	1109...	
			...
			
Furthermore given a number m on a given level l, you can find the numbers n on level
l+1 that go to l through the formula:

n = (m*2^k -1)/3

for all values of k such that this is an integer.  Note that if m is divisible by
3 there are no values of k for which this is an integer.

Note:  If m is not divisible by 3 then there are an infinite number of values AND moreover,
an infinite number of values of that are not divisible by 3 and so there is an infinite depth
following this number.

Write down notes about "decreasers", namely numbers where the smallest value on the next level
up is smaller than the number.  i.e. 5<-3

	
"""
import math
import time


#################################
#
# Collatz computation function for levels
#
#################################
def compute_up_level(target,num):
	"""
	Computes the first num integers in the sequence(target*2^k -1)/3 if they 
	exist and returns an array containing them.
	"""
	if target%3 == 0:
		return []
	else:
		count = 0
		k = 1
		list = []
		while count<num:
			numerator = target*2**k -1
			if numerator%3 ==0:
				list.append(numerator//3)
				k = k+1
				count = count + 1
			else:
				k = k+1
		return list
		
		

#################################
#
# Functions for computing information about nodes
# used in 'coloring' nodes and collecting statistics
# about the graphs.
#
#################################	

def get_length(n):
	"""
	Length here is defined as the length of the binary
	representation of the number.
	"""
	return math.floor(math.log(n,2))
	
def get_half(n):
	"""
	Half refers to what part of the interval 
	[2^c, 2^(c+1)] the number falls into with 
	the first half being the red and green and 
	the second half is blue.  
	
	COLOR	INTERVAL					RETURN VALUE	
	red		[2^c, 2^c+2^(c-3)]			-1
	green	[2^c+2^(c-3), 3*2^(c-1)]	0
	blue	[3*2^(c-1), 2^(c+1)]		1
	
	"""
	length = get_length(n)
	center = 3*(2**(length-1))
	short_cut = 2**length + 2**(length-3)
	#print "The center is ", center
	#print "The short_cut is ", short_cut
	if n < center:
		if n <short_cut:
			return -1
		else:
			return 0
	else:
		return 1

def get_descendant_parity(n):
	"""
	This returns 0 if all of the lengths of the numbers 
	in the next level up that go through n are even. It returns 
	0 if all of the lengths of the numbers in the next level up 
	that go through n are odd and -1 if there are no numbers that 
	go through n.
	"""
	length = get_length(n)
	color = get_half(n)
	#print "Length: %d, Color: %d, mod3 class: %d"%(length, color, n%3)
	if n%3 == 0:
		return -1
	elif n%3 == 1:
		if color < 1:  #Color red or green.
			if length%2==1:  #Odd length
				return 1
			else:
				return 0
		else:  #Color blue
			if length%2 ==1:
				return 0
			else:
				return 1
	else:
		if color < 1:  #Color red or green.
			if length%2==1:  #Odd length
				return 0
			else:
				return 1
		else:  #Color blue
			if length%2 ==1:
				return 1
			else:
				return 0
				
def get_data(n):
	"""
	Function that returns a list of all of the things we might want 
	to know about a node at once.  Implemented to cut down on the number 
	of calls when compiling statistics.
	"""
	class_mod3 = n%3
	length = int(get_length(n))
	
	#now get the 'color'
	center = 3*(2**(length-1))
	short_cut = 2**length + 2**(length-3)
	if n < center:
		if n <short_cut:
			color = -1
		else:
			color = 0
	else:
		color = 1

	#finally get the descendant parity
	if class_mod3 == 0:
		parity = -1
	elif class_mod3 == 1:
		if color < 1:  #Color red or green.
			if length%2==1:  #Odd length
				parity = 1
			else:
				parity = 0
		else:  #Color blue
			if length%2 ==1:
				parity = 0
			else:
				parity = 1
	else:
		if color < 1:  #Color red or green.
			if length%2==1:  #Odd length
				parity = 0
			else:
				parity = 1
		else:  #Color blue
			if length%2 ==1:
				parity = 1
			else:
				parity = 0
	
	return (class_mod3,length,color,parity) 
	
def max_poss_of_length(j):
	if j==0:
		return 1
	else:
		return 2**(j-1)
		
#################################
#
# Convert node lists into statistics count dictionaries.
#
#################################	

		
def get_stats(list):
	"""
	This takes a list and compiles a dictionary with number of things on the list that 
	have different properties.  The keys for the dictionary are a tuple returned by 
	get_data(n) which have the following ranges:
	
	class_mod3	0,1,2
	length		0,1,2,3,...,i-1 where i is the bit bound on the list
	color		-1,0,1		corresponding to red,green,blue as described above
	parity		-1,0,1		corresponding to no descendants, even length descendants, odd length descendants
	
	So there are at most 3(i)(3) = 9*i keys because parity is completely determined by the first three.
	There will actually be fewer because for small lengths, not all numbers don't exist for all possible
	keys.
	"""
	#initialize the property dictionary
	prop_dict = {}

	for n in list:
		props = get_data(n)
		if props in prop_dict:
			prop_dict[props] = prop_dict[props] + 1
		else:
			prop_dict[props] = 1
	
	return prop_dict

def merge_props(prop_dict1, prop_dict2):
	"""
	This assumes that both prop_dict1 and prop_dict2 are dictionaries of the type created by 
	get_stats and then will merge them into one dictionary.
	
	TODO:  Check whether it's faster to have prop_dict1 or prop_dict2 be the one with fewer keys.
	At a guess I would say prop_dict1 smaller.
	"""
	prop_dict = {}
	#NOTE: Don't use .copy() here because need a real copy and not a shallow copy!
	for key in prop_dict1.keys():
		prop_dict[key] = prop_dict1[key]
		
	for key in prop_dict2.keys():
		if key in prop_dict1.keys():
			prop_dict[key] = prop_dict1[key] + prop_dict2[key]
		else:
			prop_dict[key] = prop_dict2[key]

	return prop_dict
		

#################################
#
# Functions for finding nodes in graph and returning the results in 
# various different ways.  (Also have different input possibilities.)
#
#################################	
		
def get_node_list(start_num, lg2_bound):
	"""
	Returns a list of all numbers with bounded collatz sequence
	that go through start_num and are bounded by lg2_bound.
	"""

	cur_level = [start_num]
	seen_list = [start_num]
	
	#Creating the ith graph
	while len(cur_level) > 0:
		next_level = []
		for target in cur_level:
			temp = compute_up_level(target, 2+ int((lg2_bound - get_length(target))/2)) #Note:  How many terms we need
			if 1 in temp:										#depends on the length.  This speeds things up
				temp.remove(1)									#even with an extra call to get_length.
			trimmed_temp = [x for x in temp if x<= 2**lg2_bound]
			seen_list.extend(trimmed_temp)
			next_level.extend(trimmed_temp)
		cur_level = [x for x in next_level]			

	return seen_list
	

def get_node_list_props(start_num, lg2_bound):
	"""
	Returns a property dictionary for the bounded collatz sequences 
	that go through start_num and are bounded by lg2_bound.
	
	Note:  This is much more memory efficient than generating a 
	complete list and then computing the properties!
	
	CAVEAT NOTE: !!!!  We include start_num in the prop_dict!!!
	
	"""

	cur_level = [start_num]
	prop_dict = get_stats(cur_level)
	cur_prop_dict = {}
	
	#Creating the ith graph
	while len(cur_level) > 0:
		next_level = []
		for target in cur_level:
			temp = compute_up_level(target, 2+ int((lg2_bound - get_length(target))/2)) #Note:  How many terms we need
			if 1 in temp:										#depends on the length.  This speeds things up
				temp.remove(1)									#even with an extra call to get_length.
			trimmed_temp = [x for x in temp if x<= 2**lg2_bound]
			next_level.extend(trimmed_temp)
		cur_level = [x for x in next_level]	
		cur_prop_dict = get_stats(cur_level)
		prop_dict = merge_props(cur_prop_dict, prop_dict)

	return prop_dict

def get_node_list_props_from_list(start_list, lg2_bound):
	"""
	Returns a property dictionary for the bounded collatz sequences 
	that go through an element in start_list and are bounded by lg2_bound.
	
	Note:  This is much more memory efficient than generating a 
	complete list and then computing the properties!
	
	CAVEAT NOTE: !!!!  We include start_list in the prop_dict!!!
	
	Also:  start_list is assumed to be a list of odd integers.
	
	"""

	cur_level = start_list
	prop_dict = get_stats(cur_level)
	cur_prop_dict = {}
	
	#Creating the ith graph
	while len(cur_level) > 0:
		next_level = []
		for target in cur_level:
			temp = compute_up_level(target, 2+ int((lg2_bound - get_length(target))/2)) #Note:  How many terms we need
			if 1 in temp:										#depends on the length.  This speeds things up
				temp.remove(1)									#even with an extra call to get_length.
			trimmed_temp = [x for x in temp if x<= 2**lg2_bound]
			next_level.extend(trimmed_temp)
		cur_level = [x for x in next_level]	
		cur_prop_dict = get_stats(cur_level)
		prop_dict = merge_props(cur_prop_dict, prop_dict)

	return prop_dict




#################################
#
# Functions for creating display tables for 
# outputting statistics
#
#################################	



def create_stats_table(prop_dict):
	"""
	Takes a property list as generated by get_stats and processes it in terms of number and ratio that fall into 
	each of the categories
	
	CLASS MOD3		COLOR		PARITY
	
	where CLASS MOD3 is the equivalence class modulo3, COLOR refers to what part of the interval
	[2^c, 2^(c+1)] the number falls in with 
	
	red		[2^c, 2^c+2^(c-3)]
	green	[2^c+2^(c-3), 3*2^(c-1)]
	blue	[3*2^(c-1), 2^(c+1)]
	
	and PARITY refers to whether the nodes that follow are of even length or odd length or none
	referred to by (0,1) respectively.
	"""
	#Creating a color dictionary for the nodes
	color_dict = {}
	color_dict[1] = "blue"
	color_dict[0] = "green"
	color_dict[-1] = "red"

	w_str = "\t \t %8s \t %8s \t %8s \t %8s \t %8s\n\n"%('CLASS MOD3', 'COLOR', 'PARITY', 'COUNT', 'PERCENT')
	
	
	for mod3 in range(1,3):
		total_count = sum([prop_dict[x] for x in prop_dict.keys() if x[0]==mod3])
		for parity in range(2):		
			for color in range(-1,2):
				count = sum([prop_dict[x] for x in prop_dict.keys() if x[0] == mod3 and x[2] == color and x[3] == parity])	
				w_str = w_str + "\t \t %8d \t %8s \t %8d \t %8d \t %3.5f\n"%(mod3,color_dict[color],parity,count,1.0*count/total_count)
			w_str = w_str + '\n'
		w_str = w_str + '\n'
	return w_str



#################################
#
# Serial computation of statistics for a series 
# of bounds in terms of bit sizes.  This is also the initial
# prototype for the cloud version.
#
#################################	


def graph_stats_nograph(start_num, min_lg2_bound, max_lg2_bound):
	"""
	This function writes the statistics for the graphs without 
	creating the graphs.  The entire purpose is to 
	deal with the fact that at the bound of 15 or 16 
	pydot becomes unweildy.

	"""

	stats_file = open('graph_stats.txt',"w")
	prev_count = 1
	
	for i in range(min_lg2_bound, max_lg2_bound+1):
	
		#Initialization of property dictionary
		prop_dict = {}
		
		
		#Get the property dictionary data
		#####
		# Section A
		#####
		
		### Do the initial levels
		cur_level = [start_num]
		for level in range(2):  #TUNE THIS BOUND FOR PARALLELISM  
			cur_prop_dict = get_stats(cur_level)
			prop_dict = merge_props(cur_prop_dict, prop_dict)
			next_level = []
			for target in cur_level:
				temp = compute_up_level(target, 2+ int((i - get_length(target))/2)) #Note:  How many terms we need
				if 1 in temp:										#depends on the length.  This speeds things up
					temp.remove(1)									#even with an extra call to get_length.
				trimmed_temp = [x for x in temp if x<= 2**i]
				next_level.extend(trimmed_temp)
			cur_level = [x for x in next_level]			
		
		###Split the list (which is cur_level).  
		add_list = [x for x in cur_level if x%3 == 0]
		split_list = [x for x in cur_level if x%3 != 0]
		print "Subtree count: %d "%(len(split_list))
		
		###Add the mod3 = 0 class to prop_dict. 
		prop_dict = merge_props(prop_dict, get_stats(add_list))
		
		###  Send the rest of the list out as 'separate jobs'
		### Merge the separate jobs back into the property list.
		for sub_start_num in split_list:
			sub_prop_dict = get_node_list_props(sub_start_num,i)
			prop_dict = merge_props(sub_prop_dict,prop_dict)
		
		#####
		# End Section A
		#####
		"""
		#The code in Section A can be entirely replaced by this command if running in serial.
		prop_dict = get_node_list_props(start_num, i)		
		"""
		
		
		#Output the property dictionary data to log file.
		prop_keys = prop_dict.keys()
		cur_count = sum(prop_dict.values())
		
		print "%d nodes = %.2f bits of nodes for %d bits \n"%(cur_count,math.log(cur_count,2),i)
				
		#Now it's time to assemble some statistics
		write_str = "%3d BIT BOUND: \n \n"%(i)
		stats_file.write(write_str)
		write_str = "\t Number of nodes: %22d  %20.2f bits\n"%(cur_count, math.log(cur_count,2))
		stats_file.write(write_str)
		write_str = "\t Number of previously seen nodes: %6d  %20.2f bits\n"%(prev_count,math.log(prev_count ,2))
		stats_file.write(write_str)
		write_str = "\t Number of new nodes: %18d  %20.2f bits\n"%(cur_count-prev_count,math.log(cur_count-prev_count ,2))
		stats_file.write(write_str)
		write_str = "\t Percentage of new nodes: %14.2f \n"%(1.0*(cur_count-prev_count)/cur_count)
		stats_file.write(write_str)
	
		
		#Put together # of things in each congruence class
		class0_count = sum([prop_dict[x] for x in prop_keys if x[0] == 0])
		class1_count = sum([prop_dict[x] for x in prop_keys if x[0] == 1])
		class2_count = sum([prop_dict[x] for x in prop_keys if x[0] == 2])
	
		stats_file.write("\n")
		stats_file.write("\t NUMBER OF NODES IN CONGRUENCE CLASSES MODULO 3 \n\n")
		stats_file.write("\t \t 0 \t %8d \n"%(class0_count))
		stats_file.write("\t \t 1 \t %8d \n"%(class1_count))
		stats_file.write("\t \t 2 \t %8d \n"%(class2_count))
		
		#Put together # of things with even/odd descendents by congruence class
		
		class1_even_count = sum([prop_dict[x] for x in prop_keys if x[0] == 1 and x[3] == 0])
		class1_odd_count = sum([prop_dict[x] for x in prop_keys if x[0] == 1 and x[3] == 1])
		class2_even_count = sum([prop_dict[x] for x in prop_keys if x[0] == 2 and x[3] == 0])
		class2_odd_count = sum([prop_dict[x] for x in prop_keys if x[0] == 2 and x[3] == 1])
		
		stats_file.write("\n")
		stats_file.write("\t NUMBER OF NODES WITH EVEN/ODD DECENDANTS \n\n")
		stats_file.write("\t %8s \t %8s \t %8s \t %8s \n "%('PARITY', 'COUNT', '1COUNT', '2COUNT'))
		stats_file.write("\t %8s \t %8d \t %8d \t %8d \n "%('EVEN', class1_even_count + class2_even_count,class1_even_count,class2_even_count))
		stats_file.write("\t %8s \t %8d \t %8d \t %8d \n "%('ODD', class1_odd_count + class2_odd_count,class1_odd_count,class2_odd_count))
		
		stats_file.write("\n")
		stats_file.write("\t BREAKDOWN OF NODES\n\n")
		w_str = create_stats_table(prop_dict)
		stats_file.write(w_str)
		
		stats_file.write("\n")
		stats_file.write("\t NUMBER OF NODES OF A GIVEN LENGTH \n\n")
		stats_file.write("\t %8s \t %8s \t %8s \t %8s \t %8s \t %8s \t %8s \n"%('LENGTH','ACT. NODES','MAX POSS.', '% OF POSS.', '#0 MOD3','#1 MOD3','#2 MOD3'))
		for j in range(i):
			num_of_length0 = sum([prop_dict[x] for x in prop_keys if x[1] == j and x[0] == 0])
			num_of_length1 = sum([prop_dict[x] for x in prop_keys if x[1] == j and x[0] == 1])
			num_of_length2 = sum([prop_dict[x] for x in prop_keys if x[1] == j and x[0] == 2])
			num_of_length = num_of_length0 + num_of_length1 + num_of_length2
			
			max_poss = max_poss_of_length(j)
			stats_file.write("\t \t %d \t %8d \t %8d \t %3.5f \t %8d \t %8d \t %8d\n"%(j,num_of_length,max_poss,1.0*num_of_length/max_poss, num_of_length0, num_of_length1,num_of_length2))

		stats_file.write("\n")
		
		prev_count = cur_count

	stats_file.close()

	return 'done'

#############################################
#
#
#  pi.cloud SECTION
#
#
#############################################


import cloud 

#chromebox Hardware contraints 
NUM_CORES = 32		#MUST BE > 0!!! No cores, no computation.
MAX_BOUND_ON_MACHINE = 32


def cloud_call_of_get_node_list_props(data):

	start_list = data[0]
	lg2_bound = data[1]
	
	prop_dict = get_node_list_props_from_list(start_list,lg2_bound)
	return prop_dict
	
	
"""
NOTES on load leveling

From observation we have the following heuristics.  The 2^32 bound requires approximately 4 GB of 
memory.  Ignoring overhead, the amount of total compute time doubles each time the bound doubles. The 
amount of memory required for the entire computation also approximately doubles. (This second is 
basically observing that the tree width which controls the amount of memory needed for the computation
doubles.)  The second can be controlled by computing parts of the tree serially rather than trying to 
do it all in parallel.  

Example:  For 2^33, we can first break the job into 16 parts and then run the first 8 parts (which is 
approximately a 2^32 job maxing out memory) and then run the second 8 parts.  This doesn't actually 
double the compute time if the machine compute is saturated although it does add some overhead.
8385.854750  seconds for an actual run verus 2*(3305.208207 ) ~ 6620 'expected'.  

Another minor factor:  2^30 32bit int's per GB  means that when the bound goes over 2^32, some of 
the ints become long ints which will increase required memory on those ints and will increase compute 
time.  (We just added another limb.)

So if we have NUM_CORES and MAX_BOUND_ON_MACHINE  (which in the chromebox would be '8' with hyperthreading
and 32 the second being a parameter reflecting memory contraints) then if i>MAX_BOUND_ON_MACHINE we
need to split the job into (i-MAX_BOUND_ON_MACHINE + 1) parts run serially each containing NUM_CORES jobs.
This means we need to partition the list of numbers being farmed out into NUM_CORES*(i-MAX_BOUND_ON_MACHINE + 1)
lists where the work to do each list is hopefully equally balanced.

The tricky part of balancing the work of the lists is that different numbers require different times 
to finish.  However ultimately the hueristic that for every number not congruent to 0 modulo 3, eventually
the number of bounded descendent nodes will double each time the bound is increased means that if we 
have enough numbers the times should approximately balance out on sets of equal sizes.  The time of the 
computation is proportional to the number of nodes in the tree descending from that number which is 
proportional to 2**(bound - length_of_number) if the number is congruent to 1 mod 3 and  
2**(bound - length_of_number -1) if the number is congruent to 2 mod 3.  Therefore to a first approxmation
it is enough to approximately balance the sizes.  But a more accurate balancing should balance both 
the sizes and the numbers of 1 mod 3 versus 2 mod 3.
"""

def picloud_graph_stats_nograph(start_num, min_lg2_bound, max_lg2_bound):
	"""
	This function writes the statistics for the graphs without 
	creating the graphs.  It's an modification of graph_stats_nograph
	designed to use the cloud module for some parallelism.

	"""

	stats_file = open('graph_stats.txt',"w")
	prev_count = 1
	
	for i in range(min_lg2_bound, max_lg2_bound+1):
	
		prop_dict = {}
		
		start_time = time.time()
		start_clock = time.clock()
		
		### Do the initial levels creating a list of nodes to farm off to the cloud as we go
		cur_level = [start_num]
		farm_list = []
				
		FARM_BREAK_POINT = 14	#TUNE THIS BOUND FOR PARALLELISM.  Bigger means more nodes in farm_list and more compute time to start.
		for level in range(100):  #TUNE THIS BOUND FOR PARALLELISM  In practice make this large enough so that the subtree defined by the FARM_BREAK_POINT bound is completely computed.
			cur_prop_dict = get_stats(cur_level)
			prop_dict = merge_props(cur_prop_dict, prop_dict)
			next_level = []
			for target in cur_level:
				temp = compute_up_level(target, 2+ int((i - get_length(target))/2)) #Note:  How many terms we need
				if 1 in temp:										#depends on the length.  This speeds things up
					temp.remove(1)									#even with an extra call to get_length.
				trimmed_temp = [x for x in temp if x<= 2**i]
				next_level.extend(trimmed_temp)
			cur_level = [x for x in next_level if get_length(x) <FARM_BREAK_POINT]			
			farm_list.extend([x for x in next_level if get_length(x) >= FARM_BREAK_POINT])
		
		cur_level.extend(farm_list)
		###Split the list (which is cur_level).  
		add_list = [x for x in cur_level if x%3 == 0]
		split_list = [x for x in cur_level if x%3 != 0]
		split_list.sort()
		split_list1 = [x for x in split_list if x%3 == 1]
		split_list2 = [x for x in split_list if x%3 == 2]
		split_list2.reverse()
		
		print "Subtree count: %d "%(len(split_list))
		print split_list[0:20]

		###Add the mod3 = 0 class to prop_dict. 
		prop_dict = merge_props(prop_dict, get_stats(add_list))

		###Partition the split_list into sublists for jobs.		
		if i>MAX_BOUND_ON_MACHINE:
			num_partitions =  NUM_CORES*(i-MAX_BOUND_ON_MACHINE + 1)
		else:
			num_partitions = NUM_CORES
		
		temp = {}
		for k in range(num_partitions):	
			temp1 = [split_list1[n] for n in range(k,len(split_list1),num_partitions)]
			temp2 = [split_list2[n] for n in range(k,len(split_list2),num_partitions)]
			temp[k] = temp1 + temp2
		print "Partition %d has %d mod 1 nodes and %d mod 2 nodes"%(k,len(temp1),len(temp2))
		split_list = []
		for k in range(num_partitions):
			split_list.append(temp[k])


		###  Send the rest of the list out as separate jobs to the cloud.
		cloud_split_list = [ (x,i) for x in split_list]
		marker = 0
		while marker < num_partitions:
			print "Running cloud jobs %d to %d"%(marker,marker+NUM_CORES-1)
			jids = cloud.map(cloud_call_of_get_node_list_props,cloud_split_list[marker:marker + NUM_CORES],_profile=True, _type = "f2")  #Send the get_node_list jobs to cloud
			cloud_results = cloud.result(jids) #Collect the property dictionaries back from cloud
			marker = marker + NUM_CORES
			
			### Merge the separate jobs back into the property list.
			for c_dict in cloud_results:		#Merge cloud results together
				prop_dict = merge_props(c_dict,prop_dict)
			
		
		"""
		jids = cloud.map(cloud_call_of_get_node_list_props,cloud_split_list)  #Send the get_node_list jobs to cloud
		cloud_results = cloud.result(jids) #Collect the property dictionaries back from cloud
		
		### Merge the separate jobs back into the property list.
		for c_dict in cloud_results:		#Merge cloud results together
			prop_dict = merge_props(c_dict,prop_dict)
		"""

		
		prop_time = time.time()
		prop_clock = time.clock()
		
		#Output the property dictionary data to log file.
		prop_keys = prop_dict.keys()
		cur_count = sum(prop_dict.values())
		print "%d nodes = %.2f bits of nodes for %d bits \n"%(cur_count,math.log(cur_count,2),i)
				
		#Now it's time to assemble some statistics
		write_str = "%3d BIT BOUND: \n \n"%(i)
		stats_file.write(write_str)
		write_str = "\t Number of nodes: %22d  %20.2f bits\n"%(cur_count, math.log(cur_count,2))
		stats_file.write(write_str)
		write_str = "\t Number of previously seen nodes: %6d  %20.2f bits\n"%(prev_count,math.log(prev_count ,2))
		stats_file.write(write_str)
		write_str = "\t Number of new nodes: %18d  %20.2f bits\n"%(cur_count-prev_count,math.log(cur_count-prev_count ,2))
		stats_file.write(write_str)
		write_str = "\t Percentage of new nodes: %14.2f \n"%(1.0*(cur_count-prev_count)/cur_count)
		stats_file.write(write_str)
	
		
		#Put together # of things in each congruence class
		class0_count = sum([prop_dict[x] for x in prop_keys if x[0] == 0])
		class1_count = sum([prop_dict[x] for x in prop_keys if x[0] == 1])
		class2_count = sum([prop_dict[x] for x in prop_keys if x[0] == 2])
	
		stats_file.write("\n")
		stats_file.write("\t NUMBER OF NODES IN CONGRUENCE CLASSES MODULO 3 \n\n")
		stats_file.write("\t \t 0 \t %8d \n"%(class0_count))
		stats_file.write("\t \t 1 \t %8d \n"%(class1_count))
		stats_file.write("\t \t 2 \t %8d \n"%(class2_count))
		
		#Put together # of things with even/odd descendents by congruence class
		
		class1_even_count = sum([prop_dict[x] for x in prop_keys if x[0] == 1 and x[3] == 0])
		class1_odd_count = sum([prop_dict[x] for x in prop_keys if x[0] == 1 and x[3] == 1])
		class2_even_count = sum([prop_dict[x] for x in prop_keys if x[0] == 2 and x[3] == 0])
		class2_odd_count = sum([prop_dict[x] for x in prop_keys if x[0] == 2 and x[3] == 1])
		
		stats_file.write("\n")
		stats_file.write("\t NUMBER OF NODES WITH EVEN/ODD DECENDANTS \n\n")
		stats_file.write("\t %8s \t %8s \t %8s \t %8s \n "%('PARITY', 'COUNT', '1COUNT', '2COUNT'))
		stats_file.write("\t %8s \t %8d \t %8d \t %8d \n "%('EVEN', class1_even_count + class2_even_count,class1_even_count,class2_even_count))
		stats_file.write("\t %8s \t %8d \t %8d \t %8d \n "%('ODD', class1_odd_count + class2_odd_count,class1_odd_count,class2_odd_count))
		
		stats_file.write("\n")
		stats_file.write("\t BREAKDOWN OF NODES\n\n")
		w_str = create_stats_table(prop_dict)
		stats_file.write(w_str)
		
		stats_file.write("\n")
		stats_file.write("\t NUMBER OF NODES OF A GIVEN LENGTH \n\n")
		stats_file.write("\t %8s \t %8s \t %8s \t %8s \t %8s \t %8s \t %8s \n"%('LENGTH','ACT. NODES','MAX POSS.', '% OF POSS.', '#0 MOD3','#1 MOD3','#2 MOD3'))
		for j in range(i):
			num_of_length0 = sum([prop_dict[x] for x in prop_keys if x[1] == j and x[0] == 0])
			num_of_length1 = sum([prop_dict[x] for x in prop_keys if x[1] == j and x[0] == 1])
			num_of_length2 = sum([prop_dict[x] for x in prop_keys if x[1] == j and x[0] == 2])
			num_of_length = num_of_length0 + num_of_length1 + num_of_length2
			
			max_poss = max_poss_of_length(j)
			stats_file.write("\t \t %d \t %8d \t %8d \t %3.5f \t %8d \t %8d \t %8d\n"%(j,num_of_length,max_poss,1.0*num_of_length/max_poss, num_of_length0, num_of_length1,num_of_length2))

		stats_file.write("\n")
		
		#prev_seen_list = [x for x in seen_list]
		prev_count = cur_count
		
		stat_time = time.time()
		stat_clock = time.clock()

		#Note when the cloud is actually called, the CPU time will not reflect 'cloud' time.
		print "%30s %12s %12s"%(' ','CPU TIME', 'WALL TIME')
		print "%30s %12.6f %12.6f "%('Computing prop_dict', prop_clock - start_clock, prop_time-start_time)
		print "%30s %12.6f %12.6f "%('Outputing statistics', stat_clock - prop_clock, stat_time-prop_time)
		print "%30s %12.6f %12.6f \n"%('Totals', stat_clock - start_clock, stat_time-start_time)		
	stats_file.close()

	return 'done'


