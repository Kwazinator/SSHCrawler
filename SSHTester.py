import paramiko
import time

def ApplyCommands(address,username,password,commands,output):
    with open(commands, 'r') as myfile:
        data = myfile.read()
    data = data.splitlines()
    f = open(output, 'w')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    ssh.connect(address, 22, username, password)
    chan = ssh.invoke_shell()
    time.sleep(1)
    str = ""
    for lines in data:
        chan.send(lines + "\n")
        print(lines)
        print("Waiting for response from server")
        while 1:
            time.sleep(3)
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
                break
        f.write(str)
    myfile.close()

def CheckCommandsDiff():
    with open('Aftershowoutput.txt', 'r') as file1:
        with open('beforeshowoutput.txt', 'r') as file2:
            diff = set(file1).difference(file2)
    diff.discard('\n')
    with open('Changes.txt', 'w') as file_out:
        for line in diff:
            file_out.write(line)

def CheckCommandsLines():
    diff = ""
    diff2 = ""
    with open('Aftershowoutput.txt', 'r') as file1:
        with open('beforeshowoutput.txt', 'r') as file2:
            data1 = file1.read()
            data2 = file2.read()
            str = data1.splitlines()
            str2 = data2.splitlines()
            if len(str) <= len(str2):
                for index, line in enumerate(str):
                    if (line != str2[index]):
                        diff = diff + line + '\n'
                        diff2 = diff2 + str2[index] + '\n'
            else:
                for index, line in enumerate(str2):
                    if(line != str[index]):
                        diff2 = diff2 + line +'\n'
                        diff = diff + str[index] + '\n'
    with open('Changes2.txt', 'w') as file_out:
        for line in diff2:
            file_out.write(line)
    with open('Changes.txt', 'w') as file_out:
        for line in diff:
            file_out.write(line)

def OutputResults(type):
    print("*****************************************************************")
    print("------------------------SSH-Changes-Output-----------------------")
    print("*****************************************************************")
    if type == "interfaces":
        print("Before")
        file1 = open('Changes2.txt', 'r')
        for line1 in file1:
            print(line1)
        print("After")
        file2 = open('Changes.txt', 'r')
        for line2 in file2:
            print(line2)
        file1.close()
        file2.close()
    elif type == "diff":
        print("Differences:")
        file1 = open('Changes.txt', 'r')
        for line in file1:
            print(line)
        file1.close()

try:
    type = "interfaces"
    address = "10.150.254.212"
    username = "username"
    password = "password"
    commands = "commands.txt"
    commandoutput = "output.txt"
    show = "show.txt"
    beforeshow = "beforeshowoutput.txt"
    aftershow = "Aftershowoutput.txt"
    print("put changes in commands.txt")
    print("put show commands in show.txt")
    print("\n")
    print("starting preshow commands:" + '\n')
    ApplyCommands(address, username, password, show, beforeshow)
    print("finished preshow commands")
    time.sleep(4)
    print("starting command executions:" + '\n')
    ApplyCommands(address, username, password, commands, commandoutput)
    print("finished command executions")
    time.sleep(4)
    print("starting aftershow commands:" + '\n')
    ApplyCommands(address, username, password, show, aftershow)
    if type == "interfaces":
        CheckCommandsLines()
    elif type == "diff":
        CheckCommandsDiff()
    OutputResults(type)
    print("done")
finally:
    pass
