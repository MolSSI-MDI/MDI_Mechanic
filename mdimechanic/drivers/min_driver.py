import mdi
from mdi import MDI_NAME_LENGTH, MDI_COMMAND_LENGTH
import pandas as pd
import re
import sys

command = None
nreceive = None
rtype = None
nsend = None
stype = None

iarg = 1
while iarg < len(sys.argv):
    arg = sys.argv[iarg]

    if arg == "-mdi":
        # Initialize MDI
        if len(sys.argv) <= iarg+1:
            raise Exception("Argument to -mdi option not found")
        mdi.MDI_Init(sys.argv[iarg+1])
        iarg += 1
    elif arg == "-command":
        # Set the command
        if len(sys.argv) <= iarg+1:
            raise Exception("Argument to -command option not found")
        command_input = sys.argv[iarg+1]
        iarg += 1
    elif arg == "-nreceive":
        # Set the number of elements to receive
        if len(sys.argv) <= iarg+1:
            raise Exception("Argument to -nreceive option not found")
        nreceive = sys.argv[iarg+1]
        iarg += 1
    elif arg == "-nsend":
        # Set the number of elements to send
        if len(sys.argv) <= iarg+1:
            raise Exception("Argument to -nsend option not found")
        nsend = sys.argv[iarg+1]
        iarg += 1
    elif arg == "-rtype":
        # Set the type of elements to receive
        if len(sys.argv) <= iarg+1:
            raise Exception("Argument to -rtype option not found")
        rtype = sys.argv[iarg+1]
        iarg += 1
    elif arg == "-stype":
        # Set the type of elements to receive
        if len(sys.argv) <= iarg+1:
            raise Exception("Argument to -stype option not found")
        stype = sys.argv[iarg+1]
        iarg += 1
    else:
        raise Exception("Unrecognized argument")

    iarg += 1

# Connect to the engine
comm = mdi.MDI_Accept_Communicator()

# Get the name of the engine, which will be checked and verified at the end
mdi.MDI_Send_Command("<NAME", comm)
initial_name = mdi.MDI_Recv(mdi.MDI_NAME_LENGTH, mdi.MDI_CHAR, comm)

recv_type = None
if nreceive is not None:
    # Get the number of elements to receive
    nreceive_split = re.split("\+|\-|\*\*|\*|\/\/|\/|\%| ",nreceive)
    for word in nreceive_split:
        if len(word) > 0 and word[0] == '<':
            # This is a command, so send it to the engine
            # Assume that the command receives a single integer
            mdi.MDI_Send_Command(word, comm)
            value = mdi.MDI_Recv(1, mdi.MDI_INT, comm)
            
            nreceive = nreceive.replace(word, str(value), 1)
    
    recv_num = pd.eval(nreceive)
    
    # Confirm that the receive type is valid
    if rtype == "MDI_CHAR":
        recv_type = mdi.MDI_CHAR
    elif rtype == "MDI_INT":
        recv_type = mdi.MDI_INT
    elif rtype == "MDI_DOUBLE":
        recv_type = mdi.MDI_DOUBLE
    elif rtype == "MDI_BYTE":
        recv_type = mdi.MDI_BYTE
    else:
        raise Exception("Invalid receive type")
        
send_type = None
if nsend is not None:
    # Get the number of elements to send
    nsend_split = re.split("\+|\-|\*\*|\*|\/\/|\/|\%| ",nsend)
    for word in nsend_split:
        if len(word) > 0 and word[0] == '<':
            # This is a command, so send it to the engine
            # Assume that the command receives a single integer
            mdi.MDI_Send_Command(word, comm)
            value = mdi.MDI_Recv(1, mdi.MDI_INT, comm)
            
            nsend = nsend.replace(word, str(value), 1)
    
    send_num = pd.eval(nsend)
    
    # Confirm that the receive type is valid
    if stype == "MDI_CHAR":
        send_type = mdi.MDI_CHAR
    elif stype == "MDI_INT":
        send_type = mdi.MDI_INT
    elif stype == "MDI_DOUBLE":
        send_type = mdi.MDI_DOUBLE
    elif stype == "MDI_BYTE":
        send_type = mdi.MDI_BYTE
    else:
        raise Exception("Invalid send type")


# Send all commands
command_string = str(command_input)
command_list = command_string.split()

# Send the command(s) to be tested
for command in command_list:
    mdi.MDI_Send_Command(command, comm)

# Send or receive any data associated with the final command
if nreceive is not None:
    recv_data = mdi.MDI_Recv(recv_num, recv_type, comm)
    
    # Write the received data to a file 
    f = open("/repo/.mdimechanic/.temp/min_driver.dat", "w")
    f.write(str(recv_data))
    f.close()
if nsend is not None:
    if send_type == mdi.MDI_INT:
        data = [ 0 for i in range(send_num) ]
    elif send_type == mdi.MDI_DOUBLE:
        data = [ 0.0 for i in range(send_num) ]
    elif send_type == mdi.MDI_CHAR:
        data = ""
        for i in range(send_num):
            data += " "
    else:
        raise Exception("Invalid send type")
    mdi.MDI_Send(data, send_num, send_type, comm)

# Verify that the engine is still responsive
mdi.MDI_Send_Command("<NAME", comm)
final_name = mdi.MDI_Recv(mdi.MDI_NAME_LENGTH, mdi.MDI_CHAR, comm)
assert initial_name == final_name

# Some nodes might not support the "EXIT" command, so write a file indicating success now
# Write the received data to a file
f = open("/repo/.mdimechanic/.temp/min_driver.err", "w")
f.write("0")
f.close()

mdi.MDI_Send_Command("EXIT", comm)
