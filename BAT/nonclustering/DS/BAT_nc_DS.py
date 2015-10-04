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

import os, string, time, sys, platform, socket, shutil, subprocess

def write_file(input_message, log_file_path):
    file_out = open(log_file_path, 'a')
    file_out.write(input_message)
    file_out.close()

def rename_label(conf_path, DS_app):
    content=open(conf_path,'r').read()
    label = "label = jchi_DS"
    new_label = "label = " + DS_app
    content=content.replace(label,new_label)
    f=open(conf_path,'w')
    f.write(content)
    f.close()

def create_serverclass_conf_content(DS_name, DS_app, conf_path):
    serverclass_conf = """
[serverClass:%s:app:%s]
restartSplunkWeb = 1
restartSplunkd = 1
stateOnClient = enabled

[serverClass:%s]
whitelist.0 = qasus-2008r2-57*
whitelist.1 = qasus-centos-38*
whitelist.2 = qasus-centos-39*
""" %(DS_name, DS_app, DS_name)

    write_file(serverclass_conf, conf_path)


version = "605"
rc_number = "0"
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
log_file = "BAT-DS-jchi-" + version + "-" + rc + ".log"
input_message = "Version = " + version + " RC: " + rc + "\n"
current_dir = os.getcwd()
log_file_path = os.path.join(current_dir, log_file)
input_message = input_message + "current_dir = " + current_dir + "\n"
write_file(input_message, log_file_path)
scenario_result = []

# Path parameters
server_name = socket.gethostname()
splunk_bin = os.path.join(splunk_home, "bin")
splunk_deployment = os.path.join(splunk_home, "etc", "deployment-apps")
input_message = "splunk_home = " + str(splunk_home) + "\n"
input_message = input_message + "splunk_bin = " + str(splunk_bin) + "\n"
input_message = input_message + "splunk_deployment = " + str(splunk_deployment) + "\n"
write_file(input_message, log_file_path)

input_message = "Modify deployment app name in folder and app.conf\n"
write_file(input_message, log_file_path)
DS_name = "jchi_DS_" + version + "_" + rc
DS_app = DS_name + "_app"
os.rename("jchi_DS", DS_app)
conf_path = os.path.join(current_dir, DS_app, "default", "app.conf")
rename_label(conf_path, DS_app)

input_message = "Copy DS app to " + splunk_deployment + "\n"
write_file(input_message, log_file_path)
src = os.path.join(current_dir, DS_app)
dst = os.path.join(splunk_home, "etc", "deployment-apps")
shutil.move(src, dst)

input_message = "Create data under DS app\n"
write_file(input_message, log_file_path)
size_script_path = os.path.join(splunk_home, "etc", "deployment-apps", DS_app, "local", "data")
os.chdir("%s" % size_script_path)
number_MB = "100"
size = str(pow(10, 6)*int(number_MB))
size_script = "size_simple_event.py"
input_log = "jchi-DS-" + version + "-" + rc + "-" + number_MB + "mb.log"
input_log_path = os.path.join(size_script_path, input_log)
os.system("""python "%s" -d "%s" -s %s >> "%s" """ % (size_script, input_log_path, size, log_file_path))
time.sleep(60)

input_message = "Modify serverclass.conf\n"
write_file(input_message, log_file_path)
conf_path = os.path.join(splunk_home, "etc", "system", "local", "serverclass.conf")
create_serverclass_conf_content(DS_name, DS_app, conf_path)

result = "Pass"
input_message = "CLI command: reload deploy-server -class <DS>\n"
write_file(input_message, log_file_path)
os.chdir("%s" % splunk_bin)
#SPL-75246 is not integrated into cupcake
if int(version) < 610:
    to_execute = """%s reload deploy-server -class %s -auth admin:changeme""" % (splunk_command, DS_name)
else:
    to_execute = """%s reload deploy-server -auth admin:changeme""" % (splunk_command)
p = subprocess.Popen(to_execute, env=os.environ, close_fds=False, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = p.communicate()
input_message = "command: " + to_execute + "\n"
input_message = input_message + "stderr = " + str(stderr)  + "\n"
input_message = input_message + "stdout = " + str(stdout)  + "\n"
write_file(input_message, log_file_path)
if not 'Reloading' in str(stdout):
    input_message = "***ERROR: The app is not deployed succesfully, please check deployment.\n"
    write_file(input_message, log_file_path)
    result = "Failed"
else:
    input_message = "The app is deployed succesfully. GREAT!!!\n"
    write_file(input_message, log_file_path)

time.sleep(180)
# Final comment :)
input_message = """
DS - Deployment BAT %s: %s
*****Congratulation!! The BAT_deployment server is finsihed!
Please check the %s on client. Thanks!
- Platform: %s
""" %(to_execute, result, DS_app, socket.gethostname())
write_file(input_message, log_file_path)

os.remove("%s" %(os.path.join(current_dir, sys.argv[0])))
