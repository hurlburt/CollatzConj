"""
UPDATE:  June 2012, Created this file for creating graphs of the collatz conjecture 
relations using pydot.


This is a python script for displaying graphs of relationships for the 3n+1 conjecture also
known as the Collatz conjecture.

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
import pydot



NUM_LEVELS = 2
NODE_WIDTH = 2 #This is how many things to compute on the next level up.
START_NUMBER = 1
MODULUS = 3


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
		
"""		
#################################
#
# Create the simple graph
#
#################################		

graph = pydot.Dot(graph_type='graph')		

cur_level = [START_NUMBER]		
for i in range(NUM_LEVELS):
	next_level = []
	for target in cur_level:
		if target != 1:
			temp = compute_up_level(target, NODE_WIDTH)
		else:
			temp = compute_up_level(target, NODE_WIDTH + 1)
			temp.remove(1)
		for up_number in temp:
			if up_number != 1:
				edge = pydot.Edge(str(target),str(up_number))
				graph.add_edge(edge)
		next_level.extend(temp)
	cur_level = [x for x in next_level]

		
#################################
#
# Write the simple graph to a file
#
#################################		
		
graph.write_png('test_graph.png')
"""

"""
#################################
#
# Create the more complex version of the graph
#
#################################		
			
graph = pydot.Dot(graph_type='graph')	#reinitializing the graph structure

node_dict = {}
node_dict[START_NUMBER] = pydot.Node(str(START_NUMBER%MODULUS)+'\n'+str(START_NUMBER))
graph.add_node(node_dict[START_NUMBER])
cur_level = [START_NUMBER]		
for i in range(NUM_LEVELS):
	next_level = []
	for target in cur_level:
		if target != 1:
			temp = compute_up_level(target, NODE_WIDTH)
		else:
			temp = compute_up_level(target, NODE_WIDTH + 1)
			temp.remove(1)
		for up_number in temp:
			if up_number != 1:
				node_dict[up_number] = pydot.Node(str(up_number%MODULUS) + '\n'+str(up_number))
				graph.add_node(node_dict[up_number])
				edge = pydot.Edge(node_dict[target],node_dict[up_number])
				graph.add_edge(edge)
		next_level.extend(temp)
	cur_level = [x for x in next_level]

#################################
#
# Write the the more complex version of the graph to a file
#
#################################		
		
graph.write_png('test_graph2.png')

"""

#################################
#
# Functions for computing information about nodes
# used in coloring graphs or collecting statistics
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
		
def max_poss_of_length(j):
	if j==0:
		return 1
	else:
		return 2**(j-1)
		
def create_stats_table(list):
	"""
	Takes a list of numbers and processes them in terms of number and percentage that fall into 
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
	
	for i in range(1,3):
		sub_list = [x for x in list if x%3==i]
		for parity in range(2):		
			sub_sub_list = [x for x in sub_list if get_descendant_parity(x) == parity ]
			for color in range(-1,2):
				super_sub_list = [x for x in sub_sub_list if get_half(x) == color]
				w_str = w_str + "\t \t %8d \t %8s \t %8d \t %8d \t %3.5f\n"%(i,color_dict[color],parity,len(super_sub_list),1.0*len(super_sub_list)/len(sub_list))
			w_str = w_str + '\n'
		w_str = w_str + '\n'
	return w_str


#################################
#
# Function to create and write a graph containing all levels up
# to num_levels and all numbers below a bound whose reverse collatz
# sequence is bounded by the bound.
#
#################################	


def bounded_graph(num_levels, bound):
	"""
	This function finds all of the numbers in a 
	level whose reverse collatz sequence is bounded 
	by the bound.
	
	It creates a graph showing these numbers
	
	Note:  The graph created by bounded_graph(45, 2**13) is 
	particularly pretty.
	"""

	#Creating a color dictionary for the nodes
	color_dict = {}
	color_dict[1] = "blue"
	color_dict[0] = "green"
	color_dict[-1] = "red"
	
	graph = pydot.Dot(graph_type='graph')	#initializing the graph structure
	node_dict = {}
	node_dict[1] = pydot.Node(str(1%MODULUS)+'\n'+str(1))
	graph.add_node(node_dict[1])
	cur_level = [1]		
	
	#Estimating the num we need for compute_up_level using the fact 
	#that in the level the number increases by approximately 4 from one to the next.
	num_est = 2+math.ceil(math.log(bound,2))
	
	for i in range(num_levels):
		next_level = []
		for target in cur_level:
			temp = compute_up_level(target, num_est)
			if 1 in temp:
				temp.remove(1)
			trimmed_temp = [x for x in temp if x<= bound]
			for up_number in trimmed_temp:
				#node_dict[up_number] = pydot.Node(str(up_number%MODULUS) + '\n'+str(up_number))
				node_dict[up_number] = pydot.Node(str(int(get_length(up_number))) + '\n'+str(up_number), style="filled", fillcolor=color_dict[get_half(up_number)])
				#node_dict[up_number] = pydot.Node(str(int(get_length(up_number))) + '\n'+str(up_number), color=color_dict[get_half(up_number)])	
				graph.add_node(node_dict[up_number])
				edge = pydot.Edge(node_dict[target],node_dict[up_number])
				graph.add_edge(edge)
			next_level.extend(trimmed_temp)
		cur_level = [x for x in next_level]
		
	graph.write_png('test_graph3.png')
	print "%d nodes \n"%(len(node_dict.keys()))

	return 'done'

#################################
#
# Function to create and write a series of graphs, each containing all levels up
# to num_levels and all numbers below a bound whose reverse collatz
# sequence is bounded by the bound.
#
#################################	


def graph_series(start_num, min_lg2_bound, max_lg2_bound):
	"""
	This function creates a series of graphs each one consisting
	of all of the odd numbers whose reverse collatz sequence is less
	than 2**n where min_lg2_bound <=n <=max_lg2_bound.
	
	It also write a statistics file to graph_stats.txt.

	"""

	#Creating a color dictionary for the nodes
	color_dict = {}
	color_dict[1] = "blue"
	color_dict[0] = "green"
	color_dict[-1] = "red"
	
	stats_file = open('graph_stats.txt',"w")


	node_dict = {}
	node_dict[start_num] = pydot.Node(str(start_num%MODULUS)+'\n'+str(start_num))
	seen_list = [start_num]
	prev_seen_list = [start_num]
	
	graphs = {}
	for i in range(min_lg2_bound, max_lg2_bound+1):
		graphs[i] = pydot.Dot(graph_type='graph')	#initializing the graph structure
		graphs[i].add_node(node_dict[start_num])
				
		cur_level = [start_num]
		#Estimating the num we need for compute_up_level
		num_est = 2+i
		
		#Creating the ith graph
		while len(cur_level) > 0:
			next_level = []
			for target in cur_level:
				temp = compute_up_level(target, num_est)
				if 1 in temp:
					temp.remove(1)
				trimmed_temp = [x for x in temp if x<= 2**i]
				for up_number in trimmed_temp:
					if up_number in seen_list:
						graphs[i].add_node(node_dict[up_number])
						edge = pydot.Edge(node_dict[target],node_dict[up_number])
						graphs[i].add_edge(edge)
					else:
						node_dict[up_number] = pydot.Node(str(up_number%MODULUS) + ', ' + str(int(get_length(up_number))) + '\n'+str(up_number), style="filled", fillcolor=color_dict[get_half(up_number)])
						graphs[i].add_node(node_dict[up_number])
						edge = pydot.Edge(node_dict[target],node_dict[up_number])
						graphs[i].add_edge(edge)					
						
						#Now that we've added the filled node to the current graph, replace it with 
						#an unfilled node and put it on the seen list.
						seen_list.append(up_number)
						node_dict[up_number] = pydot.Node(str(up_number%MODULUS) + ', ' + str(int(get_length(up_number))) + '\n'+str(up_number), color=color_dict[get_half(up_number)])							
				next_level.extend(trimmed_temp)
			cur_level = [x for x in next_level]			
					
		file_name = "series_graph%d.png"%(i)
		graphs[i].write_png(file_name)
		print "%d nodes for %d bits \n"%(len(node_dict.keys()),i)
		
		#Now that we've written the graph, it's time to assemble some statistics
		write_str = "%3d BIT BOUND: \n \n"%(i)
		stats_file.write(write_str)
		write_str = "\t Number of nodes: %22d \n"%(len(seen_list))
		stats_file.write(write_str)
		write_str = "\t Number of previously seen nodes: %6d \n"%(len(prev_seen_list))
		stats_file.write(write_str)
		write_str = "\t Number of new nodes: %18d \n"%(len(seen_list)-len(prev_seen_list))
		stats_file.write(write_str)
	
		stats_file.write("\n")
		stats_file.write("\t NUMBER OF NODES IN CONGRUENCE CLASSES MODULO 3 \n\n")
		stats_file.write("\t \t 0 \t %8d \n"%(len([x for x in seen_list if x%3==0])))
		stats_file.write("\t \t 1 \t %8d \n"%(len([x for x in seen_list if x%3==1])))
		stats_file.write("\t \t 2 \t %8d \n"%(len([x for x in seen_list if x%3==2])))
		
		stats_file.write("\n")
		stats_file.write("\t NUMBER OF NODES OF A GIVEN LENGTH \n\n")
		stats_file.write("\t %8s \t %8s \t %8s \t\n"%('LENGTH','ACT. NODES','MAX POSS.'))
		for j in range(i):
			num_of_length = len([x for x in seen_list if get_length(x)==j])
			stats_file.write("\t \t %d \t %8d \t %8d \n"%(j,num_of_length,max_poss_of_length(j)))

		stats_file.write("\n")
				
		prev_seen_list = [x for x in seen_list]
		
	stats_file.close()

	return 'done'

#################################
#
# Write the stats without writing the graphs. pydot gets 
# overwhelmed somewhere around the 16 bit bound... but it 
# is still possible and simple to compute the underlying information
# for the graph and collect statistics.
#
#################################	


def graph_stats_nograph(start_num, min_lg2_bound, max_lg2_bound):
	"""
	This function writes the statistics for the graphs in the above
	function without creating the graphs.  Entire purpose is to 
	deal with the fact that at the bound of 15 or 16 things become
	unwieldy on a macbook.

	"""

	stats_file = open('graph_stats.txt',"w")

	prev_seen_list = [start_num]
	
	for i in range(min_lg2_bound, max_lg2_bound+1):
		cur_level = [start_num]
		seen_list = [start_num]

		#Estimating the num we need for compute_up_level
		num_est = 2+i
		
		#Creating the ith graph
		while len(cur_level) > 0:
			next_level = []
			for target in cur_level:
				temp = compute_up_level(target, num_est)
				if 1 in temp:
					temp.remove(1)
				trimmed_temp = [x for x in temp if x<= 2**i]
				seen_list.extend(trimmed_temp)
				next_level.extend(trimmed_temp)
			cur_level = [x for x in next_level]			
					
		print "%d nodes for %d bits \n"%(len(seen_list),i)
		
		#Create useful sub_lists of seen_list once rather than multiple times
		class0_seen_list = [x for x in seen_list if x%3==0]
		class1_seen_list = [x for x in seen_list if x%3==1]
		class2_seen_list = [x for x in seen_list if x%3==2]
		even_desc1 = [x for x in class1_seen_list if get_descendant_parity(x) == 0]
		odd_desc1 = [x for x in class1_seen_list if get_descendant_parity(x) == 1]
		even_desc2 = [x for x in class2_seen_list if get_descendant_parity(x) == 0]
		odd_desc2 = [x for x in class2_seen_list if get_descendant_parity(x) == 1]
		
				
		#Now it's time to assemble some statistics
		write_str = "%3d BIT BOUND: \n \n"%(i)
		stats_file.write(write_str)
		write_str = "\t Number of nodes: %22d  %20.2f bits\n"%(len(seen_list), math.log(len(seen_list),2))
		stats_file.write(write_str)
		write_str = "\t Number of previously seen nodes: %6d  %20.2f bits\n"%(len(prev_seen_list),math.log(len(prev_seen_list) ,2))
		stats_file.write(write_str)
		write_str = "\t Number of new nodes: %18d  %20.2f bits\n"%(len(seen_list)-len(prev_seen_list),math.log(len(seen_list)-len(prev_seen_list) ,2))
		stats_file.write(write_str)
		write_str = "\t Percentage of new nodes: %14.2f \n"%(1.0*(len(seen_list)-len(prev_seen_list))/len(seen_list))
		stats_file.write(write_str)
	
		stats_file.write("\n")
		stats_file.write("\t NUMBER OF NODES IN CONGRUENCE CLASSES MODULO 3 \n\n")
		stats_file.write("\t \t 0 \t %8d \n"%(len(class0_seen_list)))
		stats_file.write("\t \t 1 \t %8d \n"%(len(class1_seen_list)))
		stats_file.write("\t \t 2 \t %8d \n"%(len(class2_seen_list)))
		
		stats_file.write("\n")
		stats_file.write("\t NUMBER OF NODES WITH EVEN/ODD DECENDANTS \n\n")
		stats_file.write("\t %8s \t %8s \t %8s \t %8s \n "%('PARITY', 'COUNT', '1COUNT', '2COUNT'))
		stats_file.write("\t %8s \t %8d \t %8d \t %8d \n "%('EVEN', len(even_desc1) + len(even_desc2),len(even_desc1),len(even_desc2)))
		stats_file.write("\t %8s \t %8d \t %8d \t %8d \n "%('ODD', len(odd_desc1) + len(odd_desc2),len(odd_desc1),len(odd_desc2)))
		
		stats_file.write("\n")
		stats_file.write("\t BREAKDOWN OF NODES\n\n")
		w_str = create_stats_table(seen_list)
		stats_file.write(w_str)
		
		stats_file.write("\n")
		stats_file.write("\t NUMBER OF NODES OF A GIVEN LENGTH \n\n")
		stats_file.write("\t %8s \t %8s \t %8s \t %8s \t %8s \t %8s \t %8s \n"%('LENGTH','ACT. NODES','MAX POSS.', '% OF POSS.', '#0 MOD3','#1 MOD3','#2 MOD3'))
		for j in range(i):
			of_length = [x for x in seen_list if get_length(x)==j]
			num_of_length = len(of_length)
			max_poss = max_poss_of_length(j)
			stats_file.write("\t \t %d \t %8d \t %8d \t %3.5f \t %8d \t %8d \t %8d\n"%(j,num_of_length,max_poss,1.0*num_of_length/max_poss, len([x for x in of_length if x%3==0]), len([x for x in of_length if x%3==1]), len([x for x in of_length if x%3==2])))

		stats_file.write("\n")
		
		prev_seen_list = [x for x in seen_list]

	stats_file.close()

	return 'done'

