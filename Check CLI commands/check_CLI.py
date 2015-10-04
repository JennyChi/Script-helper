import sys, time, string, random, os

# arg: ref http://docs.splunk.com/Documentation/Splunk/<version>/Admin/CLIadmincommands
arg = ['cluster-config', 'cluster-generation', 'cluster-peers', 'cluster-buckets', 'deploy-clients', 'exec', 'forward-server', 'index', 'licenser-groups', 'licenser-localslave', 'licenser-messages', 'licenser-pools', 'licenser-slaves', 'licenser-stacks', 'licenses', 'jobs', 'master-info', 'monitor', 'peer-info', 'peer-buckets', 'saved-search', 'search-server', 'source', 'sourcetype', 'tcp', 'udp', 'user']
data = "CLI_list_report.log"

for i in range(len(arg)):
#     ./splunk list jobs -auth admin:changeme
    command = './splunk list' + ' ' + arg[i] + ' ' +'-auth admin:changeme'
    file_out = open(data, 'a')
    file_out.write(command + "\n")
    file_out.close()
    os.system("%s >> %s" %(command, data))