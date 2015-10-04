import sys, time, string, random, os

data = "memory-ps.log"

for i in range(1,600):
    os.system("date >> %s" %data )
    os.system("ps -auxx | grep splunk >> %s" %data )
    time.sleep(1)
