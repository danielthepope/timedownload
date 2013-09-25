#!/usr/bin/env python
"""
timedownload v3.
Gets a text file from dropbox and executes commands based on it.
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
#userDirectory = '/home/pi/youtube'
logfile = '/home/pi/apps/timedownload/log.txt'
#listLocation = userDirectory
alternativeDownloadLocation = '/home/pi/youtube'
downloadLocation = '/mnt/usbdrive/youtube'
# Other variables
#youtube = 'cclive -f fmt18_360p '
youtube = 'youtube-dl -f 18 -t --no-progress '
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
    print commandList
    
    for line in commandList:
        instruction = parseCommand(line.strip())
        print instruction
        if instruction == "DELETE":
            commands = []
        elif instruction != "":
            commands.append(instruction)
    if commands != []:
        out = ""
        for command in commands:
            out = out + "\n" + command
        log("Commands to execute:" + out)
    else:
        log("Nothing to do.")
    
    return

def parseCommand(line):
    print line
    # Clear the command list if there is ----------
    if line.startswith('----------'):
        return "DELETE"
    # If the line begiuns with a # it is a comment. Ignore it.
    elif line.startswith('#') or line == '':
        return ""
    # If it is made up of several words, it is a command and should be
    # executed as is.
    elif len(line.split(' ')) > 1:
        return line
    # It it contains 'youtu', it should be treated as a youtube video.
    elif 'youtu' in line:
        ytcommands = line.replace('&','?').split('?')
        yturl = line
        for segment in ytcommands:
            if segment.startswith('v='):
                yturl = 'http://youtu.be/' + segment[2:]
                break
            else:
                continue
        return youtube + yturl
    # If it contains 'vimeo', download it as vimeo.
    elif 'vimeo' in line:
        return vimeo + line
    # It is a URL if after splitting it by '/', the last section
    #contains a '.'
    elif '.' in line.split('/')[-1]:
        return "wget " + line
    # Otherwise I have no idea what to do with it, just log it.
    else:
        log("I don't know what to do with '" + line + "'")
        return ""

def deleteList():
    if onlineList:
        osexec('/home/pi/apps/timedownload/addline', False)
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
    global downloadLocation
    try:
        os.chdir(downloadLocation)
    except:
        os.chdir(alternativeDownloadLocation)
    log("Updated directory: " + os.getcwd())
    for command in commands:
        osexec(command, True)
    return

def findNames():
    for command in commands:
        if 'youtu' in command:
            c = command.split(' ')[-1]
            log(c)
            osexec('youtube-dl -e ' + c, True)
            log('')

def osexec(command, tolog):
    if tolog:
        log(command)
        os.system(command + ' >> ' + logfile + ' 2>&1')
    else:
        print command
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
    
    osexec('tail -n1500 '+logfile+' > '+logfile+'2', False)
    osexec('rm '+logfile, False)
    osexec('mv '+logfile+'2 '+logfile, False)
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
            log("Bye.")
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
    if 'names' in sys.argv:
        getCommandList()
        findNames()
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
