Memory Leak testing for BAT on Linux/Windows
====================================

quick start:

    Download whole folder(clustering) into
	 - linux: /home/jchi/BAT ("useradd -m jchi" + "passwd jchi")
	 - windows: c:\jchi\BAT

    Pre-usage:
	 * Please download 
		master -> master
			- BAT_master.py
			- Change Version(-v), rc_number(-rc), splunk_home(-home)
			  ex: python BAT_master.py -v 613 -rc 1 -home /opt/centralsite-clustering-cupcake/splunk
		slave -> slave
			- BAT_slave.py
			  sample.xml
			  sample1.json
			  file_simple_event.py
			  size_simple_event.py
			- Change Version(-v), rc_number(-rc), splunk_home(-home), splunkd_port(-splunkd_port)
			  ex: python BAT_slave.py -v 613 -rc 1 -home /opt/centralsite-clustering-cupcake/splunk -splunkd_port 55089
	


Master (The same behavior as Slave)
	Linux: Use the python on linux
		cd /home/jchi/BAT/clustering/master
		Python BAT_master.py

	Windows: Use splunk python to run
		%SPLUNK_HOME%\bin\splunk.exe envvars > env.cmd
		env.cmd
		cd C:\jchi\BAT\clustering\master
		python BAT_master.py


Slave
* upgradeBAT-jchi-604-rc1.log: record every log during automation
  jchi_604_rc1_1.log: for volume_index_1, index: jchi_604_rc1_1
  jchi_604_rc1_2.log: for volume_index_2, index: jchi_604_rc1_2
  jchi_604_rc1.log: for regular index, index: jchi_604_rc1
  
* If json/xml testing fail, then please use "./splunk clean eventdata -index jchi_613_rc1" to clean up the indexed data, and let the data re-index again.
