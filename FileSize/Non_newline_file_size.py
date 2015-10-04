import sys


f = file('100MB.log', 'r')
content =  f.read()
totalbytes = 0 

for line in content.split("\n"):
    totalbytes = len(line.rstrip("\n")) + totalbytes

'''
method 2: using count the character != \n 
for counter in content:
    if counter != "\n":
        totalbytes = totalbytes + 1
'''

print "Non-newline bytes:", totalbytes

