import sys, time, string, random, os

data = "memory-20120525.log"

for i in range(1,10):
    os.system("date >> %s" %data )
    os.system("prstat -s size 1 1 >> %s" %data )
    time.sleep(1)