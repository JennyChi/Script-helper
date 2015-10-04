## upgradeBAT_nc.py
#  Author: Chen-Ning (Jenny) Chi
#  Date: 2014 Apr
###########################################################
## The program is for windows memory leak testing. 
#  Scenario:  Upgrade BAT
#  Modify indexes.conf, inputs.conf and license - monitor the memory usage file
#  Check data indexed completely
#  Preparation
# 	- Check the test date (1GB.log) in C:\jchi\testdata
#	- Please uninstall splunk instance
#  Check file
#	- log file, memory record: exists in folder where this script is
###########################################################
HELP_MESSAGE = """
-help                            : print out possible parameters
-v [string]                      : version of splunk, ex: 604
-rc [string]                     : rc number of splunk, ex: 1
-home [string]                   : $SPLUNK_HOME path, ex: /opt/centralsite/splunk
"""

import os, string, time, sys, subprocess, re, platform, socket

def write_file(input_message, log_file_path):
    file_out = open(log_file_path, 'a')
    file_out.write(input_message)
    file_out.close()

def overwrite_file(input_message, log_file_path):
    file_out = open(log_file_path, 'w')
    file_out.write(input_message)
    file_out.close()

def create_indexes_conf_content(conf_path, version, rc):
    index_folder = version + "_" + rc
    hot_volume = "volume:hot-" + index_folder
    hot_volume_path = os.path.join(index_folder, "hot")
    path = os.path.join("$SPLUNK_HOME", hot_volume_path)
    volume_hot = """
[%s]
path = %s
maxVolumeDataSizeMB = 5
""" %(hot_volume, path)

    cold_volume = "volume:cold-" + index_folder
    cold_volume_path = os.path.join(index_folder, "cold")
    path = os.path.join("$SPLUNK_HOME", cold_volume_path)
    volume_cold = """
[%s]
path = %s
maxVolumeDataSizeMB = 50
""" %(cold_volume, path)

    vindex1 = "jchi_" + index_folder + "_1"
    v1_homePath = os.path.join(hot_volume, vindex1)
    v1_coldPath = os.path.join(cold_volume, vindex1)
    v1_thawedPath = os.path.join("$SPLUNK_HOME", index_folder, "thawed", vindex1)
    volume_1 = """
[%s]
homePath = %s
coldPath = %s
thawedPath = %s
maxDataSize = 1
repFactor = auto
""" %(vindex1, v1_homePath, v1_coldPath, v1_thawedPath)

    vindex2 = "jchi_" + index_folder + "_2"
    v2_homePath = os.path.join(hot_volume, vindex2)
    v2_coldPath = os.path.join(cold_volume, vindex2)
    v2_thawedPath = os.path.join("$SPLUNK_HOME", index_folder, "thawed", vindex2)
    volume_2= """
[%s]
homePath = %s
coldPath = %s
thawedPath = %s
maxDataSize = 2
repFactor = auto
""" %(vindex2, v2_homePath, v2_coldPath, v2_thawedPath)

    rindex = "jchi_" + index_folder
    homePath = os.path.join("$SPLUNK_DB", rindex, "db")
    coldPath = os.path.join("$SPLUNK_DB", rindex, "colddb")
    thawedPath = os.path.join("$SPLUNK_DB", rindex, "thaweddb")
    regular_index = """
[%s]
homePath = %s
coldPath = %s
thawedPath = %s
repFactor = auto
""" %(rindex, homePath, coldPath, thawedPath)

    index_content = volume_hot + volume_cold + volume_1 + volume_2 + regular_index
    write_file(index_content, conf_path)   
    return hot_volume_path, cold_volume_path, vindex1, vindex2, rindex

def clustering_command(to_execute):
    p = subprocess.Popen(to_execute, env=os.environ, close_fds=False, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    input_message = "clustering_command: " + to_execute + "\n"
    input_message = input_message + "stdout = " + str(stdout)  + "\n"
    input_message = input_message + "stderr = " + str(stderr)  + "\n"
    return input_message

version = "604"
rc_number = "3"
if platform.system() == 'Windows':
    splunk_home = os.path.join( "C:" + os.sep, "Program Files", "Splunk")
    splunk_command = "splunk"
else: # linux
#    splunk_home = os.path.join(os.path.sep, "opt", "centralsite", "splunk")
#   For testing this script, please check the /home/jchi/603-rc1/splunk exists
    private_test = version + "-rc" + rc_number
    splunk_home = os.path.join(os.path.sep, "home", "jchi", private_test, "splunk")
    splunk_command = "./splunk"

## Reading parameters
for cnt in range(len(sys.argv)):
    if str.find(sys.argv[cnt], "-help") == 0:
        print HELP_MESSAGE
        sys.exit(0)
    if str.find(sys.argv[cnt], "-v") == 0:
        version = str(sys.argv[cnt+1])
    if str.find(sys.argv[cnt], "-rc") == 0:
        rc_number = str(sys.argv[cnt+1])
    if str.find(sys.argv[cnt], "-home") == 0:
        splunk_home = str(sys.argv[cnt+1])
rc = "rc" + rc_number
log_file = "BAT-c-jchi-" + version + "-" + rc + ".log"
input_message = "Version = " + version + " RC: " + rc + "\n"
current_dir = os.getcwd()
log_file_path = os.path.join(current_dir, log_file)
clustering_log = version + "-" + rc + "-clustering-index.log"
clustering_file_path = os.path.join(current_dir, clustering_log)
input_message = "current_dir = " + current_dir + "\n"
write_file(input_message, log_file_path)

# Path parameters
splunk_bin = os.path.join(splunk_home, "bin")
splunk_cluster = os.path.join(splunk_home, "etc", "master-apps", "_cluster", "local")
if not os.path.exists(splunk_cluster):
    os.mkdir(splunk_cluster)
input_message = "splunk_home = " + str(splunk_home) + "\n"
input_message = input_message + "splunk_bin = " + str(splunk_bin) + "\n"
input_message = input_message + "splunk_cluster = " + str(splunk_cluster) + "\n"
write_file(input_message, log_file_path)

# Add conf content
input_message = "Modify /etc/master-apps/_cluster/local/indexes.conf files\n"
write_file(input_message, log_file_path)
conf_path = os.path.join(splunk_cluster, "indexes.conf")
hot_volume_path, cold_volume_path, vindex1, vindex2, rindex = create_indexes_conf_content(conf_path, version, rc)

input_message = "Indexes parameter based on master\n"
input_message = input_message + "hot_volume_path: " + str(hot_volume_path) + "\n"
input_message = input_message + "cold_volume_path: " + str(cold_volume_path) + "\n"
input_message = input_message + "vindex1: " + str(vindex1) + "\n"
input_message = input_message + "vindex2: " + str(vindex2) + "\n"
input_message = input_message + "rindex: " + str(rindex) + "\n"
write_file(input_message, log_file_path)

os.chdir("%s" % splunk_bin)
to_execute = """%s apply cluster-bundle --answer-yes -auth admin:changeme""" % (splunk_command)
input_message = clustering_command(to_execute)
write_file(input_message, log_file_path)

aTry = 1
maxTry = 6
restart_found = True
while (aTry <= maxTry) and (restart_found == True):
    time.sleep(300)
    input_message = "\n\n" + time.asctime(time.localtime()) + " " + str(aTry) + "th try to check cluster-bundle-status. Wait 5 minutes\n"
    write_file(input_message, log_file_path)
    to_execute = """%s show cluster-bundle-status -auth admin:changeme""" % (splunk_command)
    input_message = clustering_command(to_execute)
    overwrite_file(input_message, clustering_file_path)
    f = open(clustering_file_path, "r")
    match = None
    for line in f:
        match = re.search("Restart", line)
        if match != None:
            break
    if match == None:
        restart_found = False

if restart_found == False:
    input_message = "Complete: apply cluster-bundle\n"
else:
    input_message = "Please check cluster-bundle by yourself.\n"
write_file(input_message, log_file_path)


input_message = """
*****Congratulation!! The BAT_master is finsihed!
Please do the rest testing on salve. Thanks!
- Platform: %s
""" %(socket.gethostname())
write_file(input_message, log_file_path)

os.remove("%s" %(os.path.join(current_dir, sys.argv[0])))
