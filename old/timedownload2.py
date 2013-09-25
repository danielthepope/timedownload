#!/usr/bin/env python
"""
Put a proper description here
"""

# Imports ######################################################################
from time import time, localtime, sleep
import sys, urllib2, os, datetime, traceback

# Setting parameters ###########################################################
enabled = True
eraseList = True
wait = True
shutdown = False
upd = True
onlineList = True
# File locations
onlineListLocation = 'https://dl.dropbox.com/u/13316703/downloadthis.txt'
userDirectory = '/home/pi/youtube'
logfile = '/home/pi/apps/timedownload/log.txt'
listLocation = userDirectory
downloadLocation = userDirectory
# Other variables
#youtube = 'cclive -f fmt18_360p '
youtube = 'youtube-dl -f 18 -t '
vimeo = 'cclive -f best '
commands = []

# Functions ####################################################################
def getCommandList():
    global commands
    if onlineList:
        listFile = urllib2.urlopen(onlineListLocation)
    else:
        stop()
    commandList = list(listFile.read().split("\n"))
    listFile.close()
    lines = []
    for line in commandList:
        lines.append(line.split(" ", 1))
    for line in lines:
        if line[0] == 'v':
            commands.append(vimeo + line[1])
        elif line[0] == 'y':
            ytcommands = line[1].replace('&','?').split('?')
            yturl = ''
            for segment in ytcommands:
                if segment.startswith('v='):
                    yturl = 'http://youtu.be/' + segment[2:]
                    break
                else:
                    continue
            if yturl == '':
                yturl = line[1]
            commands.append(youtube + yturl)
        elif line[0] == 'c':
            commands.append(line[1])
        elif line[0] == 'd':
            commands.append("wget " + line[1])
        elif line[0] == '----------':
            commands = []
    if commands != []:
        out = ""
        for command in commands:
            out = out + "\n" + command
        log("Commands to execute:" + out)
    return

def deleteList():
    if onlineList:
        osexec('/home/pi/apps/timedownload/addline', True)
        log("Emailed ifttt - added line to list file")
    else:
        stop()
    return

def update():
    log("Updating computer...")
    osexec('sudo apt-get -y update', False)
    osexec('sudo apt-get -y upgrade', False)
    osexec('sudo youtube-dl --update', False)
    log("Done.")
    return

def executeCommands():
    os.chdir(downloadLocation)
    log("Updated directory: " + os.getcwd())
    for command in commands:
        osexec(command, True)
    return

def osexec(command, log):
    if log:
        log(command)
        os.system(command + ' >> ' + logfile + ' 2>&1')
    else:
        os.system(command)
    try:
        os.wait()
    except:
        return
    return

def log(message):
    print message
    message = 'echo "' + str(datetime.datetime.now())[:19] + " " + str(message).replace('"',"'") + '" >> ' + logfile
    os.system(message)

def notify(message):
    if __name__ == '__main__':
        osexec('/home/pi/apps/timedownload/notify "' + message + '"', False)
    return

def stop():
    #Trim the log file, then exit
    osexec('tail -n1500 log.txt > log2.txt', False)
    osexec('rm log.txt', False)
    osexec('mv log2.txt log.txt', False)
    sys.exit()

# Let's go! ####################################################################
def go():
    #global
    try:
        # Let's get the list file.
        getCommandList()
        # As soon as the list has been fetched, we'll add a line to the end.
        if commands != []:
            deleteList()
            if upd:
                update()
            executeCommands()
            log("List finished. Enjoy!")
        else:
            log("Nothing to download. Bye")
        stop()
    except SystemExit:
        #This is fine, carry on.
        stop()
    except:
        log("Eeeeb. Well, that didn't work.\n" + traceback.format_exc())
        notify("Pi crashed :( Check the log")
        stop()
    return

# Actually do stuff ############################################################
if __name__ == '__main__' and enabled == True:
    if 'now' in sys.argv:
        wait = False
    if 'noupdate' in sys.argv:
        upd = False
    if '-n' in sys.argv:
        log("Just getting the URLs, not doing anything else.")
        getCommandList()
        log("See ya")
        stop()
    if wait:
        now = localtime(time())
        if now.tm_hour > 7:
            log("Why did you wake me? It's too early! I'm going back to bed.")
            stop()
        else: # Triggers between midnight and 7am
            log("Good evening! Let's do some stuff")
            go()
    else:
        log("What an unpleasant surprise. Fine, I'll get going.")
        go()
if __name__ == '__main__' and enabled == False:
    log("Timedownload is disabled.")
