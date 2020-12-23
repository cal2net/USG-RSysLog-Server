import argparse
import os
import shutil
import json

dest = None

def main():
    parser = argparse.ArgumentParser(description="Installer for USG Remote Syslog  Service")
    parser.add_argument('location', help='Location for the installation to occur')

    args = parser.parse_args()
    print("Installation location is: " + args.location)

    if os.path.isdir(args.location):
        print("location is valid")


    else:
        print("location doesn't exist: " + args.location)
        print("creating location")
        try:
            os.mkdir(args.location)
        except OSError:
            print("Couldn't make installation directory.. Exiting")
            return 1
        else:
            print("Directory create going to copy files now.")

    copyfiles(args.location)
    updateServiceFile(args.location)


def copyfiles(location):
    bindir = location+"/src"
    logdir = location+"/logs"
    cwd = os.getcwd()
    print(cwd)
    try:
        if not os.path.isdir(bindir):
            os.mkdir(bindir)

        if not os.path.isdir(logdir):
            os.mkdir(logdir)

        shutil.copyfile(cwd +"/src/USGRSysLogServer.py", bindir+"/USGRSysLogServer.py")
\        shutil.copyfile(cwd +"/src/rsyslog.json", bindir+"/rsyslog.json")

        shutil.copyfile(cwd +"/requirements.txt", location+"/requirements.txt")
        shutil.copyfile(cwd +"/usg-rsyslog.sh", location+"/usg-rsyslog.sh")
        shutil.copyfile(cwd +"/usg-rsyslog.service", location+"/usg-rsyslog.service")


    except OSError:
        print("Error in copying files: ")
    else:
        print("Files were copied successfully")


def updateServiceFile(location):
    print("updating the service file with new location information")
    file = location +"/src/rsyslog.json"
    servfile = location+"/usg-rsyslog.service"

    js = {}

    with open(file,'r') as f:
        js = json.loads(f.read())

    print("Updating json file to installation location")

    if "logging_config" in js and "handlers" in js["logging_config"] and  "file" in js["logging_config"]["handlers"] and "filename" in js["logging_config"]["handlers"]["file"]:
        js["logging_config"]["handlers"]["file"]["filename"] = location+"/logs/RsysLog-service.log"


    print("Writing new updated file")
    with open(file,'w') as fb:
        json.dump(js, fb, indent=4, sort_keys=True)


    print("Updateing the systemctl service file")
    sfrows = None
    with open(servfile, "r") as f:
        sfrows = f.readlines()

    l=1
    while l < len(sfrows):

        line = sfrows[l]
        if "WorkingDirectory=" in line:
            sfrows[l] = "WorkingDirectory="+ location

        if "ExecStart=" in line:
            sfrows[l] = "ExecStart="+ location +"/usg-rsyslog.sh"


        l=l+1


    m=0
    with open(servfile, "w") as f:
        while m < len(sfrows):
            f.write(sfrows[m])
            m=m+1

    print("Finished with service file")

if __name__ == "__main__":
    main()
