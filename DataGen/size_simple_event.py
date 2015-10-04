## file_simple_event.py
#  Author: Chen-Ning (Jenny) Chi
#  Date: 2011 Sep
###########################################################
## The program will generate & input simple event.
#  Support files & directory.
#  Could specify the new file to create the specified size events.
#  Could specify how many events are going to be input.
#  Could specify the inputting frequency.
###########################################################
HELP_MESSAGE = """
-help              : Print out possible parameters
-d [string]        : the data which we want to add new event. Default: test.log
-s [int]           : size of events. Default: 1MB 
-f [int]           : Sending frequency. Default: 10
"""

import sys, time, string, random

## Default settings
data = "camille3.log"
volume = pow(10, 6) * 2
frequency = 10


## Reading parameters
for cnt in range(len(sys.argv)):
	if string.find(sys.argv[cnt], "-h") == 0:
		print HELP_MESSAGE
		sys.exit(0)
	if string.find(sys.argv[cnt], "-d") == 0:
		data = str(sys.argv[cnt+1])
	if string.find(sys.argv[cnt], "-s") == 0:
		volume = int(sys.argv[cnt+1])
	if string.find(sys.argv[cnt], "-f") == 0:
		frenquency = int(sys.argv[cnt+1])


print "Input data to "+data
print "Total size of events: "+str(volume)+", frequency: "+str(frequency)

counter = 0
size = 0

while size < volume:
	
	counter = counter + 1
	input_message = ""
	input_message = "line " + str(counter) + " "
	input_message = input_message + time.asctime(time.localtime()) + " "
	input_message = input_message + "counter=" + str(counter) + ", "
	input_message = input_message + "state=" + str(random.randrange(0, 9, 1)) + ", "
	input_message = input_message + "ip=140.116." + str(random.randrange(0, 255, 1)) + "." + str(random.randrange(0, 255, 1)) + "\n"
    
	file_out = open(data, 'a')
	file_out.write(input_message)
	file_out.close()
	
	size = size + len(input_message)

	if (counter%frequency) == 0:
		print "Number of events: " +str(counter)+ ", total size: " +str(size)
#		time.sleep(1)
