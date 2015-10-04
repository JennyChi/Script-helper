Memory Leak testing for BAT on Linux/Windows
move all *.log into another folder (rm -rf *.log)
====================================

quick start:

    Download whole folder(nonclustering) into
	 - linux: /home/jchi/BAT ("useradd -m jchi" + "passwd jchi")
	 - windows: c:\jchi\BAT

    Pre-usage:
	 * Please download the whole folder
		sample.xml
		sample1.json
		file_simple_event.py
		size_simple_event.py
		BAT_nc.py
	
	 * Change Version(-v), rc_number(-rc), splunk_home(-home), splunkd_port(-splunkd_port)
		ex: python BAT_nc.py -v 613 -rc 1 -home /opt/centralsite/splunk -splunkd_port 8089
	

Linux: Use the python on linux
	cd /home/jchi/BAT/nonclustering
	Python BAT_nc.py

Windows: Use splunk python to run
	%SPLUNK_HOME%\bin\splunk.exe envvars > env.cmd
	env.cmd
    cd C:\jchi\BAT\nonclustering
	python BAT_nc.py


* upgradeBAT-jchi-604-rc1.log: record every log during automation
  jchi_604_rc1_1.log: for volume_index_1, index: jchi_604_rc1_1
  jchi_604_rc1_2.log: for volume_index_2, index: jchi_604_rc1_2
  jchi_604_rc1.log: for regular index, index: jchi_604_rc1
  
