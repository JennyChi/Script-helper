import sys, time, string, random

input_message = ""
b = time.mktime(time.localtime()) - 12*60
input_message = time.asctime(time.localtime(b))
print "Time: " +input_message

