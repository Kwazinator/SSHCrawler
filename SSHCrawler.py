import paramiko
import time
import threading


def ApplyCommands2(address, username, password, pinglist, failedpings, n):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        ssh.connect(address, 22, username, password)
        chan = ssh.invoke_shell()
        time.sleep(3)
        failedlist = ""
        print("Completed SSH to node: " + address + "\n")
        for commands in pinglist:
            str = ""
            chan.send(commands + "\n")
            while 1:
                time.sleep(15)
                str = str + chan.recv(65535).decode('utf-8')
                str2 = str.splitlines()
                if "lines" in str2[len(str2) - 1]:
                    chan.send(" ")
                elif "--More--" in str2[len(str2) - 1]:
                    chan.send(" ")
                elif "<--- More --->" in str2[len(str2) - 1]:
                    chan.send(" ")
                elif "---(more" in str2[len(str2) - 1]:
                    chan.send(" ")
                else:
                    failedlist += CheckCommandsDiff(str2, commands)
                    break
        if failedlist != "":
            failedpings[n] = failedlist
        return failedlist
    except:
        failedpings[n] = "Error in connecting to device"
        print("Error in connecting to device")
        return "Error in connecting to device"


'''Check any Commands here or add any new Syntax for Juniper equipment etc.'''
def CheckCommandsDiff(string, pings):
    stringtocheck = string
    for line in stringtocheck:
        if "request timed out" in line:
            return getIP(pings)
        elif "Invalid" in stringtocheck:
            print("X")
        elif "Unable" in stringtocheck:
            print("X")
        elif ", 0 packets received" in line:
            '''Check to see most recent ip pinged and place it into the '''
            print(".")
            return getIP(pings)
        elif "time=" in line:
            print("!")
        elif "!!!" in line:
            print("!")
        elif "Success rate is 0 percent" in line:
            print(".")
            return getIP(pings)
    return ""


def getIP(pings):
    setflag = 0
    start = 0
    index = 0
    for char in pings:
        if char in "1234567890" and (setflag == 0):
            setflag = 1
            start = index
        if char in " " and (setflag == 1):
            return pings[start:index] + "\n"
        elif index == len(pings) - 1 and setflag == 1:
            return pings[start:index+1] + "\n"
        index += 1
    return "no ip detected"


try:
    username = "username"
    password = "password"
    listofaddress = "addresses.txt"
    pingcommands = "pingcommands.txt"
    before = "Beforeshow.txt"
    with open(listofaddress, 'r') as myfile:
        data = myfile.read()
    addresses = data.splitlines()
    with open(pingcommands, 'r') as myfile:
        data = myfile.read()
    pinglist = data.splitlines()
    threadArray = [threading.Thread for x in range(30)]
    failedpings = ["" for x in range(len(addresses))]
    failedlist = "********************************************************************" + "\n"
    failedlist += "--------------------------Ping Test Results-------------------------" + "\n"
    failedlist += "********************************************************************" + "\n"
    numAddresses = 0
    for address in addresses:
        try:
            threadArray[numAddresses] = threading.Thread(target=ApplyCommands2, args=(address, username, password, pinglist, failedpings, numAddresses))
            numAddresses += 1
        finally:
            pass
    numAddresses -= 1
    f = 0
    for address in addresses:
        threadArray[f].start()
        f += 1
    f = 0
    for address in addresses:
        threadArray[f].join()
        f += 1
    num = 0
    for stringtoprint in failedpings:
        failedlist += "failed pings for node at " + addresses[num] + ":" + "\n"
        if stringtoprint == "":
            failedlist += "none" + "\n\n"
        else:
            failedlist += stringtoprint + "\n"
        num += 1
    print(failedlist)
finally:
    pass