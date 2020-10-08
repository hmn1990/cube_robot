#!/usr/bin/python3
import serial
import time

def block_until_stop(num):
    #等待运动完成
    time.sleep(0.2)#0.1不可靠
    while is_moving(num):
        pass
    
def block_until_all_stop():
    #等待运动完成
    time.sleep(0.2)#0.1不可靠
    for i in range(1,9):
        while is_moving(i):
            pass

def move_none_block(num,pos):
    if pos >= 0:
        cmd = new_cmd(num, 3, [ 0x2A, pos & 0xFF, (pos >> 8) & 0x7F ])
    else:
        pos = - pos
        cmd = new_cmd(num, 3, [ 0x2A, pos & 0xFF, (pos >> 8) & 0x7F | 0x80])
    ser.write(cmd)
    recv = ser.read(6)
    
def is_moving(num):
    cmd = new_cmd(num,2,[0x42,1])
    ser.write(cmd)
    recv = ser.read(7)
    if len(recv) == 7:
        return recv[5] == 1
    else:
        print("Error: uart timeout error")
        return True

def move(num,pos):
    move_none_block(num,pos)
    block_until_stop(num)

def new_cmd(id_num, instruction, parameters):
    length = len(parameters) + 2
    checksum = id_num + length + instruction
    for x in parameters:
        checksum += x
    checksum = ~checksum & 0xFF
    cmd_list = [0xFF, 0xFF, id_num, length, instruction] + parameters + [checksum]
    return bytes(cmd_list)

def print_hex(str1):
    print("[",end="")
    for x in str1:
        print(hex(x),end=",")
    print("\b]")
    
def get_pos(num):
    cmd = new_cmd(num,2,[0x38,2])
    ser.write(cmd)
    recv = ser.read(8)
    print(num, recv[5] | (recv[6] << 8) )
    
def set_zero(num):
        cmd = new_cmd(num, 3, [0x28,128])
        ser.write(cmd)
        recv = ser.read(6)
    
def all_servo_power_off():
    for i in range (1, 9):
        cmd = new_cmd(i, 3, [0x28,0])
        ser.write(cmd)
        recv = ser.read(6)

ser = serial.Serial("/dev/ttyAMA1", 115200, timeout=0.5)

# move_none_block(1, 1500)
# move_none_block(3, 2000)
# move_none_block(5, 1500)
# move_none_block(7, 2000)
# move_none_block(4, 1024)
# move_none_block(8, 1024)
# move_none_block(2, 2048)
# move_none_block(6, 2048)
# block_until_all_stop()
# time.sleep(5)
# 
# move_none_block(1, 1500)
# move_none_block(5, 1500)
# block_until_all_stop()
# move_none_block(2, 1024)
# move_none_block(6, 3072)
# block_until_all_stop()
# move_none_block(3, 1500)
# move_none_block(7, 1500)
# block_until_all_stop()
# 
# time.sleep(5)
# move_none_block(1, 2000)
# move_none_block(3, 2000)
# move_none_block(5, 2000)
# move_none_block(7, 2000)
# block_until_all_stop()

all_servo_power_off()
for i in (1,2,3,4,5,6,7,8):
     set_zero(i)
for i in range(1,9):
    get_pos(i)
ser.close()
