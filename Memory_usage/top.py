import sys, time, string, random, os

data = "memory-top.log"
os.system("date >> %s" %data )
os.system("top -d 1 -b -c -n 600 >> %s" %data )
