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
    with open('SSHSnapshotAfter.txt', 'r') as file1:
        with open('SSHSnapshotBefore.txt', 'r') as file2:
            diff = set(file1).difference(file2)
    diff.discard('\n')
    if diff != "":
        with open('Changes.txt', 'w') as file_out:
            for line in diff:
                file_out.write(line)

try:
    username = "username"
    password = "password"
    address = "10.150.254.212"
    before = "SSHSnapshotBefore.txt"
    show = "SSHSnapshotShow.txt"
    after = "SSHSnapshotAfter.txt"
    ApplyCommands(address,username,password,show,before)
    ApplyCommands(address,username,password,show,after)
    CheckCommandsDiff()
    
finally:
    pass

