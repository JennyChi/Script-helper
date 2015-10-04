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
-splunkd_port [string]           : splunk port, ex: 8089
"""

import os, string, time, sys, platform, urllib2, socket, subprocess, re

def write_file(input_message, log_file_path):
    file_out = open(log_file_path, 'a')
    file_out.write(input_message)
    file_out.close()

def create_savedsearches_conf_content(rindex, conf_path, rlog_sourcetype):
    savedsearch_name_rc = rindex + "_rc"
    saved_searches_rc = """
[%s]
auto_summarize = 1
auto_summarize.dispatch.earliest_time = -1d@h
auto_summarize.timespan = 1m
auto_summarize.cron_schedule = */3 * * * *
request.ui_dispatch_app = search
request.ui_dispatch_view = search
search = index=%s sourcetype=%s | stats count
""" %(savedsearch_name_rc, rindex, rlog_sourcetype)

    savedsearch_name_alert = rindex + "_alert"
    saved_searches_alert = """
[%s]
action.rss = 1
alert.digest_mode = False
alert.suppress = 0
alert.track = 1
counttype = number of events
cron_schedule = * * * * *
dispatch.earliest_time = -1m@m
dispatch.latest_time = now
enableSched = 1
quantity = 0
relation = greater than
request.ui_dispatch_app = search
request.ui_dispatch_view = search
search = index=%s | stats count
""" %(savedsearch_name_alert, rindex)

    saved_searches = saved_searches_rc + saved_searches_alert
    write_file(saved_searches, conf_path)   
    return savedsearch_name_rc, savedsearch_name_alert

def create_limits_conf_content(conf_path):
    stanza = "[summarize]"
    param = "hot_bucket_min_new_events = 500"
    
    stanza_found = False
    param_found = False
    if (os.path.exists(conf_path) == True):
        f = open(conf_path, "r")
        searchlines = f.readlines()
        f.close()
        for i, line in enumerate(searchlines):
            if stanza in line:
                stanza_found = True
            if param in line:
                param_found = True

# according to splunk docs http://docs.splunk.com/Documentation/Splunk/6.0.2/Admin/Limitsconf
# hot_bucket_min_new_events only exists in [summarize]
    content=open(conf_path,'a')
    if (stanza_found == True) and (param_found == True):
        limit_content = ""
    elif (stanza_found == True):
        content=open(conf_path,'r').read()
        limit_content = "\n" +  param
        content=content.replace(stanza,stanza+limit_content)
        f=open(conf_path,'w')
        f.write(content)
        f.close()
    else:
        content=open(conf_path,'a')
        limit_content = "\n" + stanza + "\n" + param
        content.write(limit_content)
        content.close()

def create_props_conf_content(conf_path, version, rc):
    index_folder = version + "_" + rc
    xml_stanza = "jchi_xml_" + index_folder
    prop_xml_content = """
[%s]
BREAK_ONLY_BEFORE = (?!)
NO_BINARY_CHECK = 1
SHOULD_LINEMERGE = true
pulldown_type = 1
""" % (xml_stanza) 

    json_stanza = "jchi_json_" + index_folder
    prop_json_content = """
[%s]
BREAK_ONLY_BEFORE = (?!)
NO_BINARY_CHECK = 1
SHOULD_LINEMERGE = true
pulldown_type = 1
"""  % (json_stanza)

    prop_content = prop_xml_content + prop_json_content
    write_file(prop_content, conf_path)
    return 	xml_stanza, json_stanza

def update_server_content(conf_path, log_file_path):
    param = "allowRemoteLogin"   
    param_found = False
    f = open(conf_path, "r")
    searchlines = f.readlines()
    f.close()
    for i, line in enumerate(searchlines):
        if param in line:
            param_found = True
            break
    if param_found == False:
        search="[general]"
        add="\nallowRemoteLogin = always"
        content=open(conf_path,'r').read()
        content=content.replace(search,search+add)
        f=open(conf_path,'w')
        f.write(content)
        f.close()

        # Restart splunk
        os.chdir("%s" % splunk_bin)
        os.system("""%s restart >> "%s" """ % (splunk_command, log_file_path))
        input_message = "update_server_content complete: restart splunk\n"
        write_file(input_message, log_file_path)

def indexing_scenario(current_dir, index, index_folder_path, number_MB, log_file_path):
    event_script = "size_simple_event.py"
    event_script_path = os.path.join(current_dir, event_script)
    input_log = index + ".log"
    input_log_path = os.path.join(current_dir, input_log)
    input_message = "indexing_scenario: \n"
    input_message = input_message + "event_script_path: " + event_script_path + " AND input_log_path: " + input_log_path + "\n"
    write_file(input_message, log_file_path)
    sourcetype = index
    size = str(pow(10, 6)*int(number_MB))
    os.system("""python "%s" -d "%s" -s %s >> "%s" """ % (event_script_path, input_log_path, size, log_file_path))
    os.system("""%s add monitor "%s" -sourcetype %s -index %s -auth admin:changeme >> "%s" """ % (splunk_command, input_log_path, sourcetype, index, log_file_path))
    time.sleep(10)

    aTry = 1
    maxTry = 10
    bucket_start = "db_"
    index_path = os.path.join(splunk_home, index_folder_path, index)
    target_db = find_folder_name_start_with(index_path, bucket_start)
    while (aTry <= maxTry) and (target_db == ""):
        input_message = time.asctime(time.localtime()) + " " + str(aTry) + "try: no warm bucket(db_) found in" + index + ". Wait 1 minutes\n"
        write_file(input_message, log_file_path)
        time.sleep(60)
        target_db = find_folder_name_start_with(index_path, bucket_start)
        aTry += 1
    return target_db

def Get_REST_endpoint_eventCount(url, user, password, rest_log_path):
    password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, url, user, password)

    auth = urllib2.HTTPBasicAuthHandler(password_manager)
    opener = urllib2.build_opener(auth)
    urllib2.install_opener(opener)

    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    webpage = response.read().decode('utf-8')

    file_out = open(rest_log_path, 'w')
    file_out.write(webpage)
    file_out.close()

    f = open(rest_log_path, "r")
    searchlines = f.readlines()
    f.close()
    for i, line in enumerate(searchlines):
        if "totalEventCount" in line: 
            tuple = line.split(">", 1)
            tuple_1 = tuple[1].split("<", 1)
            event_count = int(tuple_1[0])
            break
    return event_count

def Get_REST_endpoint_index(url, user, password):
    password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, url, user, password)

    auth = urllib2.HTTPBasicAuthHandler(password_manager)
    opener = urllib2.build_opener(auth)
    urllib2.install_opener(opener)

    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    webpage = response.read().decode('utf-8')

    found = False
    if response.getcode() == 200:
        found = True
    return found

def find_folder_name_start_with(folder_path, template):
    target_folder_name = ""
    dirContent = os.listdir(folder_path)
    for item in dirContent:
        if item.startswith(str(template)):
            target_folder_name = item
            break
    return target_folder_name

def find_folder_name_with_pattern(folder_path, start, template):
    target_folder_name = ""
    dirContent = os.listdir(folder_path)
    for item in dirContent:
        if (re.search(str(template), item) != None) and (item.startswith(str(start))):
            target_folder_name = item
            break
    return target_folder_name


version = "604"
rc_number = "1"
if platform.system() == 'Windows':
    splunk_home = os.path.join( "C:" + os.sep, "Program Files", "Splunk")
    splunkd_port = "8089"
    splunk_command = "splunk"
else: # linux
#    splunk_home = os.path.join(os.path.sep, "opt", "centralsite", "splunk")
#   For testing this script, please check the /home/jchi/603-rc1/splunk exists
    private_test = version + "-rc" + rc_number
    splunk_home = os.path.join(os.path.sep, "home", "jchi", private_test, "splunk")
    splunkd_port = "8089"
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
    if str.find(sys.argv[cnt], "-splunkd_port") == 0:
        splunkd_port = str(sys.argv[cnt+1])
rc = "rc" + rc_number
log_file = "BAT-c-jchi-" + version + "-" + rc + ".log"
input_message = "Version = " + version + " RC: " + rc + "\n"
current_dir = os.getcwd()
log_file_path = os.path.join(current_dir, log_file)
rest_log = version + "-" + rc + "-rest-index.log"
rest_log_path = os.path.join(current_dir, rest_log)
xml_log = version + "-" + rc + "-xml.log"
xml_log_path = os.path.join(current_dir, xml_log)
json_log = version + "-" + rc + "-json.log"
json_log_path = os.path.join(current_dir, json_log)
input_message = "current_dir = " + current_dir + "\n"
input_message = input_message + "rest_log_path = " + rest_log_path + "\n"
input_message = input_message + "xml_log_path = " + xml_log_path + "\n"
input_message = input_message + "json_log_path = " + json_log_path + "\n"
write_file(input_message, log_file_path)
scenario_result = []

# Path parameters
server_name = socket.gethostname()
splunk_bin = os.path.join(splunk_home, "bin")
splunk_db = os.path.join(splunk_home, "var", "lib", "splunk")
splunk_search_app = os.path.join(splunk_home, "etc", "apps", "search", "local")
if not os.path.exists(splunk_search_app):
    os.mkdir(splunk_search_app)
input_message = "splunk_home = " + str(splunk_home) + "\n"
input_message = input_message + "splunk_bin = " + str(splunk_bin) + "\n"
input_message = input_message + "splunk_search_app = " + str(splunk_search_app) + "\n"
write_file(input_message, log_file_path)
expected_event_count = 0
rlog_sourcetype = "jchi_" + version + "_" + rc

# Add conf content

input_message = "Modify /etc/system/local/server.conf files, allowRemoteLogin\n"
write_file(input_message, log_file_path)
conf_path = os.path.join(splunk_home, "etc", "system", "local", "server.conf")
update_server_content(conf_path, log_file_path)

input_message = "Check indexes parameter based on master: \n"
index_folder = version + "_" + rc
hot_volume_path = os.path.join(index_folder, "hot")
cold_volume_path = os.path.join(index_folder, "cold")
input_message = input_message + "hot_volume_path: " + str(hot_volume_path) + "\n"
input_message = input_message + "cold_volume_path: " + str(cold_volume_path) + "\n"
write_file(input_message, log_file_path)
vindex1 = "jchi_" + index_folder + "_1"
vindex2 = "jchi_" + index_folder + "_2"
rindex = "jchi_" + index_folder
v1_url = "https://" + server_name + ":" + splunkd_port + "/servicesNS/nobody/_cluster/data/indexes/" + vindex1
v2_url = "https://" + server_name + ":" + splunkd_port + "/servicesNS/nobody/_cluster/data/indexes/" + vindex2
rindex_url = "https://" + server_name + ":" + splunkd_port + "/servicesNS/nobody/_cluster/data/indexes/" + rindex
user = "admin"
password = "changeme"
if not Get_REST_endpoint_index(v1_url, user, password):
    input_message = "vindex1 not found = " + vindex1 + "\n Please check the clustering apply is completed"
    write_file(input_message, log_file_path)
    sys.exit(0)
if not Get_REST_endpoint_index(v2_url, user, password):
    input_message = "vindex2 not found = " + vindex1 + "\n Please check the clustering apply is completed"
    write_file(input_message, log_file_path)
    sys.exit(0)
if not Get_REST_endpoint_index(rindex_url, user, password):
    input_message = "rindex not found = " + vindex1 + "\n Please check the clustering apply is completed"
    write_file(input_message, log_file_path)
    sys.exit(0)

input_message = input_message + "vindex1 found: " + str(vindex1) + "\n"
input_message = input_message + "vindex2 found: " + str(vindex2) + "\n"
input_message = input_message + "rindex found: " + str(rindex) + "\n"
write_file(input_message, log_file_path)

input_message = "Modify /etc/apps/search/local/savedsearches.conf files\n"
write_file(input_message, log_file_path)
conf_path = os.path.join(splunk_search_app, "savedsearches.conf")
savedsearch_name_rc, savedsearch_name_alert = create_savedsearches_conf_content(rindex, conf_path, rlog_sourcetype)

input_message = "Modify /etc/system/local/limits.conf files\n"
write_file(input_message, log_file_path)
conf_path = os.path.join(splunk_home, "etc", "system", "local", "limits.conf")
create_limits_conf_content(conf_path)

input_message = "Modify /etc/system/local/props.conf files\n"
write_file(input_message, log_file_path)
conf_path = os.path.join(splunk_home, "etc", "system", "local", "props.conf")
xml_stanza, json_stanza = create_props_conf_content(conf_path, version, rc)

os.chdir("%s" % splunk_bin)
xml_input_file = os.path.join(current_dir, "sample.xml")
json_input_file = os.path.join(current_dir, "sample1.json")
input_message = "Remove sample.xml if they existing\n"
write_file(input_message, log_file_path)
os.system("""%s remove monitor "%s" -auth admin:changeme >> "%s" """ % (splunk_command, xml_input_file, log_file_path))
time.sleep(10)
input_message = "Remove sample1.json if they existing\n"
write_file(input_message, log_file_path)
os.system("""%s remove monitor "%s" -auth admin:changeme >> "%s" """ % (splunk_command, json_input_file, log_file_path))
time.sleep(10)
# Restart splunk
os.system("""%s restart >> "%s" """ % (splunk_command, log_file_path))
input_message = "Complete: restart splunk\n"
write_file(input_message, log_file_path)

# Add xml and json index
index = rindex
sourcetype = xml_stanza
os.system("""%s add monitor "%s" -sourcetype %s -index %s -auth admin:changeme >> "%s" """ % (splunk_command, xml_input_file, sourcetype, index, log_file_path))
time.sleep(10)
input_message = "Add xml file, the sourcetype is " + sourcetype +"\n"
write_file(input_message, log_file_path)
sourcetype = json_stanza
os.system("""%s add monitor "%s" -sourcetype %s -index %s -auth admin:changeme >> "%s" """ % (splunk_command, json_input_file, sourcetype, index, log_file_path))
time.sleep(10)
input_message = "Add json file, the sourcetype is " + sourcetype +"\n"
write_file(input_message, log_file_path)

# Add python file_simple_event.py -d jchi_test.log -n 600
event_script = "file_simple_event.py"
event_script_path = os.path.join(current_dir, event_script)
input_log = rlog_sourcetype + ".log"
input_log_path = os.path.join(current_dir, input_log)
input_message = "event_script_path: " + event_script_path + " input_log_path: " + input_log_path + "\n"
write_file(input_message, log_file_path)
sourcetype = rlog_sourcetype
event_count = "600"
expected_event_count = expected_event_count + int(event_count)
os.system("""python "%s" -d "%s" -n %s >> "%s" """ % (event_script_path, input_log_path, event_count, log_file_path))
os.system("""%s add monitor "%s" -sourcetype %s -index %s -auth admin:changeme >> "%s" """ % (splunk_command, input_log_path, sourcetype, index, log_file_path))
time.sleep(10)

# BAT scenario 1: indexing
result = "Pass"
input_message = "\n===== BAT scenario 1: indexing =====\n"
write_file(input_message, log_file_path)
target_db_v1 = indexing_scenario(current_dir, vindex1, hot_volume_path, "2", log_file_path)
if target_db_v1 == "":
    input_message = "***ERROR: no warm bucket found in volume_1 homePath: " + vindex1 + ".\n"
    write_file(input_message, log_file_path)
    result = "Failed"

target_db_v2 = indexing_scenario(current_dir, vindex2, cold_volume_path, "5", log_file_path)
if target_db_v2 == "":
    input_message = "***ERROR: no warm bucket found in volume_2 coldPath: " + vindex2 + ".\n"
    write_file(input_message, log_file_path)
    result = "Failed"
elif find_folder_name_start_with(os.path.join(splunk_home, cold_volume_path, vindex1), "db_") == "" :
    input_message = "***ERROR: volume_2 coladPath has warm buclet, BUT no warm bucket found in volume_1 coldPath.\n"
    write_file(input_message, log_file_path)
    result = "Failed"
scenario_result.append("===== BAT scenario 1: indexing: " + result)
	
# BAT scenario 2: searches
result = "Pass"
input_message = "\n===== BAT scenario 2: searches =====\n"
write_file(input_message, log_file_path)
v1_count = Get_REST_endpoint_eventCount(v1_url, "admin", "changeme", rest_log_path)
input_message = "v1_count: " + str(v1_count) + "\n"
write_file(input_message, log_file_path)
v2_count = Get_REST_endpoint_eventCount(v2_url, "admin", "changeme", rest_log_path)
input_message = "v2_count: " + str(v2_count) + "\n"
write_file(input_message, log_file_path)
total_v1_v2 = int(v1_count) + int(v2_count)
input_message = "total_v1_v2: " + str(total_v1_v2) + "\n"
write_file(input_message, log_file_path)
time.sleep(60)
search_command = "(index=" + vindex1 + ") OR (index=" + vindex2 + ") | stats count"
os.system("""%s search "%s" -auth admin:changeme >> "%s" """ % (splunk_command, search_command, log_file_path))
f = open(log_file_path,'rb')
lines = f.readlines()
match = None
match = re.search(str(total_v1_v2), lines[-1])
if match == None:
    input_message = "***ERROR: search failed:" + search_command + "\n"
    write_file(input_message, log_file_path)
    result = "Failed"
scenario_result.append("===== BAT scenario 2: searches: " + result)

# BAT scenario 3: JSON/XML
result = "Pass"
input_message = "\n===== BAT scenario 3: JSON/XML =====\n"
write_file(input_message, log_file_path)
xml_json_list = ["cofaxCDS", "cofaxEmail", "cofaxAdmin", "fileServlet", "cofaxTools"]
xml_list_found = [0, 0, 0, 0, 0]
json_list_found = [0, 0, 0, 0, 0]
input_message = "\n== XML ==\n"
write_file(input_message, log_file_path)
for i in range(len(xml_json_list)):
    search_command = "index=" + rindex + " sourcetype=" + xml_stanza + " | spath input=_raw output=servlet-name path=web-app.servlet{" + str(i+1) + "}.servlet-name | top servlet-name"
    input_message = "search_command: " + search_command + "\n"
    write_file(input_message, log_file_path)
    os.system("""%s search "%s" -auth admin:changeme >> "%s" """ % (splunk_command, search_command, xml_log_path))
    f = open(xml_log_path, "r")
    match = None
    for line in f:
        match = re.search(xml_json_list[i], line)
        if match != None:
            input_message = "Correct: xml servlet-name{" + str(i+1) + "}: " + xml_json_list[i] + "\n"
            write_file(input_message, log_file_path)
            xml_list_found[i] = 1
            break
    if match == None:
        input_message = "***ERROR XML: search failed on: " + str(i+1) + "th servlet-name\n"
        write_file(input_message, log_file_path)
        result = "Failed"
input_message = "\n== JSON ===\n"
write_file(input_message, log_file_path)
for i in range(len(xml_json_list)):
    search_command = "index=" + rindex + " sourcetype=" + json_stanza + " | spath input=_raw output=foo path=web-app.servlet{" + str(i) + "}.servlet-name | table foo"
    input_message = "search_command: " + search_command + "\n"
    write_file(input_message, log_file_path)
    os.system("""%s search "%s" -auth admin:changeme >> "%s" """ % (splunk_command, search_command, json_log_path))
    f = open(json_log_path, "r")
    match = None
    for line in f:
        match = re.search(xml_json_list[i], line)
        if match != None:
            input_message = "Correct: json servlet-name{" + str(i) + "}: " + xml_json_list[i] + "\n"
            write_file(input_message, log_file_path)
            json_list_found[i] = 1
            break
    if match == None:
        input_message = "***ERROR JSON: search failed on: " + str(i) + "th servlet-name\n"
        write_file(input_message, log_file_path)
        result = "Failed"

if ((sum(xml_list_found) != 5) or (sum(json_list_found) != 5)):
    result = "Failed"
scenario_result.append("===== BAT scenario 3: JSON/XML: " + result)

# BAT scenario 5: Report Acceleration
result = "Pass"
input_message = "\n===== BAT scenario 5: Report Acceleration =====\n"
write_file(input_message, log_file_path)
# Add python file_simple_event.py -d jchi_test.log -n 600
index = rindex
event_count = "600"
expected_event_count = expected_event_count + int(event_count)
os.system("""python "%s" -d "%s" -n %s >> "%s" """ % (event_script_path, input_log_path, event_count, log_file_path))
# savedsearches.conf: auto_summarize.cron_schedule = */3 * * * *
time.sleep(180)
# Check the Summary is created
template = "info_"
summary_path = os.path.join(splunk_db, rindex, "summary")
summary_chunk_path = ""
for root, dirs, files in os.walk(summary_path):
    for name in files:
        if name.startswith(str(template)):
            summary_chunk_path = os.path.join(root, name)
            break
input_message = "summary_chunk_path:" + os.path.abspath(summary_chunk_path) + "\n"
write_file(input_message, log_file_path)
if summary_chunk_path == "":
    input_message = "***ERROR: No report acceleration generated. Please check this summary later by yourself\n"
    write_file(input_message, log_file_path)
    result = "Failed"

os.system("""%s search "| savedsearch %s" -auth admin:changeme >> "%s" """ %(splunk_command, savedsearch_name_rc, log_file_path))
f = open(log_file_path,'rb')
lines = f.readlines()
match = None
match = re.search(str(expected_event_count), lines[-1])
if match == None:
    input_message = "***ERROR: savedsearch returns wrong result, please check the result bu yourself\n"
    write_file(input_message, log_file_path)
    result = "Failed"
scenario_result.append("===== BAT scenario 5: Report Acceleration: " + result)

# BAT sceanrio 6: online fsck
result = "Pass"
input_message = "\n===== BAT sceanrio 6: online/offline fsck =====\n"
write_file(input_message, log_file_path)
# Corrupt Sources.data
index_homepath = os.path.join(splunk_db, rindex, "db")
hot_bucket_name = find_folder_name_start_with(index_homepath, "hot")
hot_bucket_path = os.path.join(index_homepath, hot_bucket_name)
input_message = "The hot bucket whose Sources.data will be removed is: " + hot_bucket_name  + "\n"
input_message = input_message + "hot_bucket_path = " + hot_bucket_path  + "\n"
write_file(input_message, log_file_path)
sources_data_path = os.path.join(hot_bucket_path, "Sources.data")

# Remove Sources.data
os.remove("%s" %(sources_data_path))

# Detect Corrupt
os.chdir("%s" % splunk_bin)
to_execute = """%s cmd splunkd fsck scan --one-bucket --bucket-path="%s" --include-hots >> %s""" % (splunk_command, hot_bucket_path, log_file_path)
p = subprocess.Popen(to_execute, env=os.environ, close_fds=False, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = p.communicate()
input_message = splunk_command + " cmd splunkd fsck scan --one-bucket --bucket-path=<bucket_path> --include-hots\n"
input_message = input_message + "stderr = " + str(stderr)  + "\n"
write_file(input_message, log_file_path)
if not 'Corruption' in str(stderr):
    input_message = "***ERROR: The corruption is not succesful, please check online fsck command.\n"
    write_file(input_message, log_file_path)
    result = "Failed"
else:
    input_message = "The corruption is succesful, go to repair Sources.data.\n"
    write_file(input_message, log_file_path)

# In clustering, we need to use fsck command to repair the corrupted Sources.dat
# Beacuse when we stop splunk in clustering, the bucket will rolled into warm, then restart can'r trigger online fsck
input_message = "In clustering, we need to use fsck command to repair the corrupted Sources.dat\n"
input_message = input_message + "Beacuse when we stop splunk in clustering, the bucket will rolled into warm, then restart can'r trigger online fsck\n"
write_file(input_message, log_file_path)

# Repair Sources.data
to_execute = """%s cmd splunkd fsck repair --one-bucket --bucket-path="%s" --include-hots >> %s""" % (splunk_command, hot_bucket_path, log_file_path)
p = subprocess.Popen(to_execute, env=os.environ, close_fds=False, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = p.communicate()
input_message = splunk_command + " cmd splunkd fsck repair --one-bucket --bucket-path=<bucket_path> --include-hots\n"
input_message = input_message + "stderr = " + str(stderr)  + "\n"
write_file(input_message, log_file_path)

# Check Sources.data repaired and exists
aTry = 1
maxTry = 3
while (aTry <= maxTry) and (os.path.exists(sources_data_path) == False):
    input_message = time.asctime(time.localtime()) + " " + str(aTry) + "try: fsck repair is NOT completely. Wait 5 minutes\n"
    write_file(input_message, log_file_path)
    time.sleep(300)
    aTry += 1    
if aTry <= maxTry:
    input_message = "The fsck repair is succesful. Good.\n"
else:
    input_message = "The online fsck repair is NOT succesful. WHY!!!!\n"
    input_message = input_message + "Please check fsck repair by yourself.\n"
write_file(input_message, log_file_path)
scenario_result.append("===== BAT sceanrio 6: online/offline fsck: " + result)


# Final comment :)
input_message = "\n\n The result of each scenario\n"
for i in range(len(scenario_result)):
    input_message = input_message + scenario_result[i] + "\n"
write_file(input_message, log_file_path)

input_message = """
*****Congratulation!! The BAT is finsihed!
Please check the follow item by yourself on UI
1. BAT scenario 4: Sparkline, please run the following search command on UI
	- index=_internal sourcetype=splunkd_access | timechart count(source) by sourcetype
	- index=_internal sourcetype=splunkd_access | stats sparkline(count(source)) by sourcetype
2. Run saved search %s on UI, and check the job said the search used summaries
3. Check saved search %s on UI, and check alert trace
Please sing-off the jira as
*BAT OK to SignOff*
*Linux/Windows*
- Area: Indexing/Search/JSON&XML/Sparkline/Alerting/Report Acceleration/Online fsck
- Central site clustering linux/windows platform: %s
- Browser: 
""" %(savedsearch_name_rc, savedsearch_name_alert, server_name)
write_file(input_message, log_file_path)

os.remove("%s" %(os.path.join(current_dir, sys.argv[0])))
