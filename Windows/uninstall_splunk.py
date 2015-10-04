import os, string, sys, time

def find_splunk_version(splunk_etc):
    os.chdir("%s" % splunk_etc)
    f = open("splunk.version", "r")
    searchlines = f.readlines()
    f.close()

    version = 0
    build = 0
    for i, line in enumerate(searchlines):
        if "VERSION" in line: 
            tuple = line.split("=", 1)
            version = tuple[1].strip()
#            print("haha: %s" %version)
        elif "BUILD" in line:
            tuple = line.split("=", 1)
            build = tuple[1].strip()
#            print("haha: %s" %build)
    return version, build

def uninstall_splunk(version, build, package_dir, current_dir):
    os.chdir("%s" % package_dir)
    splunk_package = "splunk-" + version + "-" + build + "-x64-release.msi"
    print ("%s" %splunk_package)
    os.system("msiexec.exe /x %s /qn" % splunk_package)
    os.chdir("%s" % current_dir)


# Default settings on windows	
package_dir = os.path.join( "C:" + os.sep, "Users", "Administrator", "Downloads")
splunk_home = os.path.join( "C:" + os.sep, "Program Files", "Splunk")
splunk_etc = os.path.join( "C:" + os.sep, "Program Files", "Splunk", "etc")
current_dir = os.getcwd()
	
# Detect splunk exists on this machine or not
if os.path.exists(splunk_home):
    print("splunk exists, going to uninstall splunk")
    print("%s" % (time.asctime(time.localtime())))
else:
    print("splunk doesn't exist on this machine, what do you want me to do? :)")
    sys.exit(0)

# Find splunk version and build by \etc\splunk.version
version, build = find_splunk_version(splunk_etc)
print("splunk version is: %s" %version)
print("splunk build is: %s" %build)

# Uninstall splunk
print("Start to uninstall splunk")
uninstall_splunk(version, build, package_dir, current_dir)

if os.path.exists(splunk_home):
    print("splunk uninstall failed, SPLUNK_HOME still exists")
else:
    print("splunk uninstall completely, SPLUNK_HOME doens't  exist")

print("%s" % (time.asctime(time.localtime())))
