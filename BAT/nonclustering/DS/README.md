DS for BAT on Linux/Windows
move all *.log into another folder (rm -rf *.log)
====================================

quick start:

    Download whole folder(DS) into
	 - linux: /home/jchi/BAT ("useradd -m jchi" + "passwd jchi")
	 - windows: c:\jchi\BAT

    Pre-usage:
	 * Please download the whole folder
		jchi_DS
		BAT_nc_DS.py
	
	 * Change Version(-v), rc_number(-rc), splunk_home(-home)
		ex: python BAT_nc_DS.py -v 605 -rc 1 -home /opt/centralsite/splunk
	

Linux: Use the python on linux
	cd /home/jchi/BAT/nonclustering/DS
	Python BAT_nc_DS.py

Windows: Use splunk python to run
	%SPLUNK_HOME%\bin\splunk.exe envvars > env.cmd
	env.cmd
    cd C:\jchi\BAT\nonclustering\DS
	python BAT_nc_DS.py


* BAT-DS-jchi-606-rc0.log: collect the log during this script
  

