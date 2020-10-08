#!/usr/bin/python3
import serial
import time

def block_until_stop(num):
    #等待运动完成
    time.sleep(0.2)#0.1不可靠
    while is_moving(num):
        pass
    
def move_none_block(num,pos):
    if pos >= 0:
        cmd = new_cmd(num, 3, [ 0x2A, pos & 0xFF, (pos >> 8) & 0x7F ])
    else:
        pos = - pos
        cmd = new_cmd(num, 3, [ 0x2A, pos & 0xFF, (pos >> 8) & 0x7F | 0x80])
    print_hex(cmd)
    ser.write(cmd)
    recv = ser.read(6)
    
def set_limit(num, limit):
    cmd = new_cmd(num, 3, [ 0x30, limit & 0xFF, (limit >> 8) & 0x7F ])
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

def all_servo_power_off():
    for i in range (1, 9):
        cmd = new_cmd(i, 3, [0x28,0])
        ser.write(cmd)
        recv = ser.read(6)

ser = serial.Serial("/dev/ttyAMA1", 115200, timeout=0.5)
for i in range(1,9):
    set_limit(i,1000)
#运动到最远处,然后校准
# set_limit(1,120)
# set_limit(3,120)
# set_limit(5,120)
# set_limit(7,120)
# move_none_block(1,4095)
# move_none_block(3,4095)
# move_none_block(5,4095)
# move_none_block(7,4095)
# time.sleep(2)


# move(2,0)
# print("move to -1024")
# move(2,-1024)
# 1800 机械爪接触一点,可以拧
# 1700 刚刚贴合魔方,魔方可以滑动
# 1600 贴合魔方,更紧,夹紧后不易乱动
# 2048 远离魔方,极限位置


for i in range(1,9):
    move_none_block(i,2048)

time.sleep(10)
all_servo_power_off()
for i in range(1,9):
    get_pos(i)
ser.close()


# t1 = time.time()
# t2 = time.time()
# print("XXXX time 1.  time=%.2f"%(t2-t1))