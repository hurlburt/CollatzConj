"""
This is a python script for displaying ideas about the 3n+1 conjecture also
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

	
"""
import math



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
		
		
def create_up_level_dict(num_levels, bound):
	"""
	This function finds all of the numbers in a 
	level whose reverse collatz sequence is bounded 
	by the bound.
	
	It creates a dictionary whose key is the level 
	and whose value is these numbers.
	"""
	level_dict = {}
	level_dict[0] = [1]
	
	#Estimating the num we need for compute_up_level using the fact 
	#that in the level the number increases by approximately 4 from one to the next.
	num_est = 2+math.ceil(math.log(bound,2))
	print "num_est is: ", num_est
	cur_level = 0
	while cur_level < num_levels:
		next_level = cur_level + 1
		if next_level not in level_dict:
			level_dict[next_level] = []
		for target in level_dict[cur_level]:
			level = compute_up_level(target,num_est)
			if 1 in level:
				level.remove(1)
			level_dict[next_level].extend([x for x in level if x <= bound])
			
		cur_level = next_level
		
	
	return level_dict
	
def collatz_seq(n):
	"""
	Prints out the collatz sequence of n
	"""
	#Compute the collatz sequence.
	seq = [n]
	a = n
	#print "%d, "%(n)
	while a != 1:
		if a%2 == 0:
			a = a/2
		else:
			a = 3*a + 1
		#print "%d, "%(a)
		seq.append(a)
	return seq
	
def look_collatz(n):
	
	max_val = 0
	for i in range(1,n,2):
		seq = [x for x in collatz_seq(i) if x%2 == 1]
		print "%6d %6d   %s "%(i, len(seq)-1,str(seq))
		if len(seq)-1>max_val:
			max_val = len(seq)-1
	
	return max_val
	
def small_look_collatz(n):

	max_val = 0
	for i in range(1,n,2):
		seq = [x for x in collatz_seq(i) if x%2 == 1]
		if len(seq)-1>max_val:
			max_val = len(seq)-1
	
	return max_val
	
def small_look_data_file(n):
	"""
	Given n, write out a data file containing 
	i, l   where i is an odd number and l is the level of i
	for all i < n odd.
	"""
	
	file_handle = open('level_data.txt', 'w')
	gfile_handle = open('max_level_data.txt', 'w')
	max_level = 0
	for i in range(1,n,2):
		seq = [x for x in collatz_seq(i) if x%2 == 1]
		level = len(seq) - 1
		if level > max_level:
			max_level = level
		out_str = "%d \t %d \n"%(i,level)
		file_handle.write(out_str)
		max_out_str = "%d \t %d \n"%(i,max_level)
		gfile_handle.write(max_out_str)
	file_handle.close()
	gfile_handle.close()
	return 'done'
	

def display_level(target):

	print "The target is %d  = %s \n"%(target,bin(target))
	for i in compute_up_level(target,12):
		print "i is %d = %s \n"%(i,bin(i))
		print "Those just above i are ", compute_up_level(i,3)
		print [bin(x) for x in compute_up_level(i,3)]
		print "\n"

	return 'done'

def display_level_count(target):

	print "The target is %d  = %s, length: %d \n"%(target,bin(target),len(bin(target))-2)
	for i in compute_up_level(target,12):
		print "i is %d = %s, length: %d \n"%(i,bin(i),len(bin(i))-2)
		print "Those just above i are ", compute_up_level(i,3)
		print [(bin(x),len(bin(x))-2) for x in compute_up_level(i,3)]
		print "\n"

	return 'done'	
	

def	switch_base(num,base):
	"""
	IMPORTANT:  base MUST BE GREATER THAN 1! 
	
	For now we will assume that base <= 10.  (We don't have digits otherwise)
	
	Note:  Numbers are returned in "endian" meaning that the least significant
	digit is first!
	"""
	
	converted_str = ''
	rem = num
	coverted = 0
	power = 0
	while rem>0:
		modulus = base**(power+1)
		cur = rem%modulus
		digit = cur/(base**power)
		converted_str = converted_str + str(digit)
		power = power + 1
		rem = rem - cur
	
	return converted_str
	
	
def display_multi_base(target):


	print "The target is %d  = %s, (base 3)%s, (base 9)%s \n"%(target,bin(target),switch_base(target,3),switch_base(target,9))
	for i in compute_up_level(target,9):
		print "i is %d = %s, (base 3)%s, (base 9)%s \n"%(i,bin(i),switch_base(i,3),switch_base(i,9))
		print "Those just above i are ", compute_up_level(i,3)
		print [bin(x) for x in compute_up_level(i,3)]
		print [switch_base(x,3) for x in compute_up_level(i,3)]
		print [switch_base(x,3) for x in compute_up_level(i,9)]
		print "\n"

	return 'done'




def display_bins(topbin):

	for i in range(1,topbin+1):
		a = 2**i
		b = 2**i + 2**(i-1)
		c = 2**(i+1)
		print "%8d %8d %8d"%(a,b,c)
		print range(a+1,b,2), range(b+1,c,2)
	return 'done'
	
	
	


