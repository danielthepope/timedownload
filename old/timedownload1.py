#!/usr/bin/env python
"""
Executes given commands at midnight, to avoid adding to download limits.
Requires clive.

Text file style
d [url] download a url, call it whatever it is after the last / (not implemented)
c [cmd] execute whatever command
v [url] download a vimeo video
y [url] download a youtube video
"""

from time import sleep, localtime, time
import ntplib, os, pwd, sys, datetime, urllib2, traceback, urllib

# parameters ###################################################################
delay1 = 3600 #This should be 1800, check every half hour
delay2 = 300 #This should be 300, every 5 minutes
commands = []
#userdir = pwd.getpwuid(os.getuid()).pw_dir #returns '/home/daniel'
userdir = '/home/pi/youtube'
listlocation = userdir
listname = 'downloadthis.txt'
onlineListLocation = 'https://dl.dropbox.com/u/13316703/downloadthis.txt'
downloadlocation = userdir
ntpaddress = 'europe.pool.ntp.org'
usentp = False #Set to True for computers without a clock
getParams = False
eraselist = True
shutdown = False
upd = True
exe = True
wait = True
onlineList = True
################################################################################

def waituntilmidnight():
    log("Waiting until midnight...")
    if usentp:
        timeserver = ntplib.NTPClient()
    while (True):
        if usentp:
            webtime = timeserver.request(ntpaddress, version=3).tx_time
            now = localtime(webtime)
        else:
            now = localtime(time())
        if (now.tm_hour > 7 and now.tm_hour < 23):
            print "The time is", now.tm_hour, ":", now.tm_min, ":", now.tm_sec
            print "Wait", delay1, "seconds"
            sleep(delay1)
        elif (now.tm_hour == 23):
            print "The time is", now.tm_hour, ":", now.tm_min, ":", now.tm_sec
            print "Wait", delay2, "seconds"
            sleep(delay2)
        else:
            log("DOWNLOAD TIME")
            break
        continue
    return

def getcommandlist():
    global commands
    log("Fetching command list...")
    if onlineList:
        listfile = urllib2.urlopen(onlineListLocation)
    else:
        os.chdir(listlocation)
        log("Updated directory: " + os.getcwd())
        listfile = open(listname,'r')
    commandlist = list(listfile.read().split("\n"))
    listfile.close()
    lines = []
    for line in commandlist:
        lines.append(line.split(" ",1))
    for line in lines:
        if line[0] == 'v':
            commands.append("clive -f best " + line[1])
        elif line[0] == 'y':
            commands.append("clive -f fmt18_360p " + line[1])
            #commands.append("clive -f best " + line[1])
        elif line[0] == 'c':
            commands.append(line[1])
        elif line[0] == 'd':
            commands.append("download " + line[1])
        elif line[0] == '----------':
            commands = []
    out = ""
    for command in commands:
        out = out + command + "\n"
    log("Commands to execute:\n" + out)
    return

def deletelist():
    log("Deleting list file...")
    if onlineList:
        osexec('/home/pi/apps/timedownload/addline')
        log("Emailed ifttt")
    else:
        os.chdir(listlocation)
        log("Updated directory: " + os.getcwd())
        listfile = open(listname,'w')
        listfile.close()
        log("Done.")
    return

def update():
    log("Updating computer...")
    osexec('sudo apt-get -y update')
    osexec('sudo apt-get -y upgrade')
    log("Done.")
    return

def executecommands():
    global commands
    os.chdir(downloadlocation)
    log("Updated directory: " + os.getcwd())
    for command in commands:
        log('executing "' + command + '"...')
        if command.startswith("download"):
            url = command.split(' ',1)[1]
            filename = url.split('/')[-1]
            urllib.urlretrieve(command.split(' ',1)[1],filename)
        else:
            osexec(command)
    log("List finished")
    commands = []
    return

def osexec(command):
    os.system(command)
    try:
        os.wait()
    except:
        return
    return

def log(message):
    print message
    if __name__ == '__main__':
        logfile = open("/home/pi/apps/timedownload/log.txt","a")
        logfile.write(str(datetime.datetime.now()) + ": " + message + "\n")
        logfile.close()
    return

def notify(message):
    if __name__ == '__main__':
        osexec('/home/pi/apps/timedownload/notify "' + message + '"')
    return

# Start here ###################################################################
def go():
    global getParams
    global wait
    global upd
    global exe
    global commands
    global shutdown
    global eraselist
    global onlineList
    try:
        if (getParams):
            print "Set parameters:"
            # if raw_input("Use NTP? (n) " == "y"):
            #     usentp = True
            if raw_input("Wait until midnight? (y) ") == "n":
                wait = False
            # if raw_input("Actually execute stuff? (y) " == "n"):
            #     exe = False
            if raw_input("Update computer while you're at it? (y) ") == "n":
                upd = False
            elif raw_input("So do you want to just update it? (n) ") == "y":
                exe = False
            if raw_input("Delete list afterwards? (y) ") == "n":
                eraselist = False
            if raw_input("Shut down afterwards? (n) ") == "y":
                shutdown = True

        if (wait):
            waituntilmidnight()
        if (upd):
            update()

        while(True):
            if (wait):
                waituntilmidnight()
            if (exe):
                getcommandlist()
            if (not(commands == []) and eraselist and onlineList):
                deletelist()
            if (exe):
                executecommands()
            if (not(commands == []) and eraselist and not onlineList):
                deletelist()
            if (shutdown):
                osexec('sudo shutdown -h now')
            sleep(delay1)
            #break #Comment out to keep running
    except:
        log("Eeeeb. Well, that didn't work." + traceback.format_exc())
        notify("Pi crashed :( Check the log")
        sys.exit()
    return

#if (raw_input("Go? (Y/n) ") == "n"):
    #    sys.exit()
if __name__ == '__main__':
    print "Press ctrl-c within 7 seconds to stop the running of this program."
    print "TIMEDOWNLOAD: A script to download stuff overnight while Plusnet is free"

    sleep(7)
    #notify("timedownload has started.")
    log("---------- \n---------- timedownload has started ----------")
    go()
