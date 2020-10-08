#!/usr/bin/python3
import serial
import time
import cv2
import numpy as np
from functools import cmp_to_key
import kociemba
# 终端绘制魔方
def draw_cube(cube_str, color = ['Y', 'R', 'B', 'W', 'O', 'G']):
    color_dist = {'Y':'43', 'R':'41', 'B':'44', 'W':'47', 'O':'45', 'G':'42'}
    cube_colors = {}
    cube_colors['U'] = color_dist[color[0]]
    cube_colors['R'] = color_dist[color[1]]
    cube_colors['F'] = color_dist[color[2]]
    cube_colors['D'] = color_dist[color[3]]
    cube_colors['L'] = color_dist[color[4]]
    cube_colors['B'] = color_dist[color[5]]
    #print(''.join(cube_str))
    # URFDLB -> YRBWOG
    cube_map = [99, 99, 99, 0,  1,  2,  99, 99, 99, 99, 99, 99, 98,
                99, 99, 99, 3,  4,  5,  99, 99, 99, 99, 99, 99, 98,
                99, 99, 99, 6,  7,  8,  99, 99, 99, 99, 99, 99, 98,
                36, 37, 38, 18, 19, 20, 9,  10, 11, 45, 46, 47, 98,
                39, 40, 41, 21, 22, 23, 12, 13, 14, 48, 49, 50, 98,
                42, 43, 44, 24, 25, 26, 15, 16, 17, 51, 52, 53, 98,
                99, 99, 99, 27, 28, 29, 99, 99, 99, 99, 99, 99, 98,
                99, 99, 99, 30, 31, 32, 99, 99, 99, 99, 99, 99, 98,
                99, 99, 99, 33, 34, 35, 99, 99, 99, 99, 99, 99, 98]
    for x in cube_map:
        if x == 99:
            print("\033[40m  ", end='')
        elif x == 98:
            print("\033[0m")
        else:
            code = cube_str[x]
            color = cube_colors[code]
            print("\033[" + color + "m  ", end='')
# 等待电机停转
def block_until_stop(num_list):
    #等待运动完成
    time.sleep(0.2)#0.1不可靠
    for num in num_list:
        while is_moving(num):
            pass
def block_until_stop_and_preview_camera(num_list):
    #等待运动完成
    time.sleep(0.2)#0.1不可靠
    for num in num_list:
        while is_moving(num):
            ret,preview = cap.read()
            cv2.imshow("preview", preview)
            cv2.waitKey(1)
            pass
# 等待所有电机停转
def block_until_all_stop():
    time.sleep(0.2)#0.1不可靠
    for i in range(1,9):
        while is_moving(i):
            pass
# 设定电机的目标位置
def move_none_block(num, pos):
    if pos > 32766 or pos < -32766:
        raise Exception("pos > 32766 or pos < -32766")
    if pos >= 0:
        cmd = new_cmd(num, 3, [ 0x2A, pos & 0xFF, (pos >> 8) & 0x7F ])
    else:
        pos = - pos
        cmd = new_cmd(num, 3, [ 0x2A, pos & 0xFF, (pos >> 8) & 0x7F | 0x80])
    ser.write(cmd)
    recv = ser.read(6)
    if len(recv) != 6:
        print("Error: move_none_block(): uart timeout error")
# 判断电机是否转动
def is_moving(num):
    cmd = new_cmd(num,2,[0x42,1])
    ser.write(cmd)
    recv = ser.read(7)
    if len(recv) == 7:
        return recv[5] == 1
    else:
        print("Error: uart timeout error")
        return True
# 编码指令
def new_cmd(id_num, instruction, parameters):
    length = len(parameters) + 2
    checksum = id_num + length + instruction
    for x in parameters:
        checksum += x
    checksum = ~checksum & 0xFF
    cmd_list = [0xFF, 0xFF, id_num, length, instruction] + parameters + [checksum]
    return bytes(cmd_list)
# 十六进制打印
def print_hex(str1):
    print("[",end="")
    for x in str1:
        print(hex(x),end=",")
    print("\b]")
# 0 - 4095
def get_pos_now(num):
    cmd = new_cmd(num,2,[0x38,2])
    ser.write(cmd)
    recv = ser.read(8)
    pos = recv[5] | (recv[6] << 8)
    return pos
# -32766 - 36766
def get_pos_target(num):
    cmd = new_cmd(num,2,[0x2A,2])
    ser.write(cmd)
    recv = ser.read(8)
    pos = recv[5] | (recv[6] << 8)
    if pos & 0x8000 != 0:
        pos = - (pos & 0x7FFF) 
    return pos
 
# 控制机械爪旋转
def init_servo_pos_tab(servo_pos_tab):
    for i in (2, 4, 6, 8):
        servo_pos_tab[i] = get_pos_target(i)
        #if servo_pos_tab[i] == 0: # 刚刚上电
        #    servo_pos_tab[i] = get_pos_now(i)
        #    if servo_pos_tab[i] >= 4000:
        #        servo_pos_tab[i] = 0
    print("init_servo_pos_tab")
    print(servo_pos_tab[2], servo_pos_tab[4], servo_pos_tab[6], servo_pos_tab[8])
    
    if (abs(servo_pos_tab[2]) > 20000 or abs(servo_pos_tab[4]) > 20000 or
            abs(servo_pos_tab[6]) > 20000 or abs(servo_pos_tab[8]) > 20000):
        servo_pos_tab[2] = 0
        servo_pos_tab[4] = 0
        servo_pos_tab[6] = 0
        servo_pos_tab[8] = 0
    
    move_none_block(1, 2048)
    move_none_block(3, 1850)
    move_none_block(5, 2048)
    move_none_block(7, 1850)
    
    time.sleep(0.3)
    claw_left_right(4, True)
    claw_left_right(8, True)
    claw_up_down(2, True)
    claw_up_down(6, True)
    block_until_all_stop()

# 0 2048  
def claw_up_down(num, skip_pos_check = False):
    if num not in (2,4,6,8):
        print("servo number must be 2 4 6 8")
        return
    now = servo_pos_tab[num]
    if now % 4096 == 0 or now % 4096 == 2048: # 已经是想要的位置蓝
        if skip_pos_check:
            target = now // 2048 * 2048
        else:
            return
    elif now % 1024 != 0: # 没有对齐
        if abs(now % 4096 - 0) < abs(now % 4096 - 2048):
            target = now // 4096 * 4096 + 0
        else:
            target = now // 4096 * 4096 + 2048
    else:
        if now > 0: # 防止超越正负七圈的限制
            target = now - 1024
        else:
            target = now + 1024
    servo_pos_tab[num] = target
    print(num,target)
    move_none_block(num, target)
    
# 1024 3072
def claw_left_right(num, skip_pos_check = False):
    if num not in (2,4,6,8):
        raise Exception("servo number must be 2 4 6 8")
    now = servo_pos_tab[num]
    if now % 4096 == 1024 or now % 4096 == 3072: # 已经是想要的位置蓝
        if skip_pos_check:
            target = now // 2048 * 2048 + 1024
        else:
            return
    elif now % 1024 != 0: # 没有对齐
        if abs(now % 4096 - 1024) < abs(now % 4096 - 3072):
            target = now // 4096 * 4096 + 1024
        else:
            target = now // 4096 * 4096 + 3072
    else:
        if now > 0: # 防止超越正负七圈的限制
            target = now - 1024
        else:
            target = now + 1024
    servo_pos_tab[num] = target
    print(num,target)
    move_none_block(num, target)

def claw_cw(num):
    if num not in (2,4,6,8):
        raise Exception("servo number must be 2 4 6 8")
    now = servo_pos_tab[num]
    target = now - 1024
    servo_pos_tab[num] = target
    print(num,target)
    move_none_block(num, target)
    
def claw_ccw(num):
    if num not in (2,4,6,8):
        raise Exception("servo number must be 2 4 6 8")
    now = servo_pos_tab[num]
    target = now + 1024
    servo_pos_tab[num] = target
    print(num,target)
    move_none_block(num, target)
    
def claw_route_any(num, angle):
    if num not in (2,4,6,8):
        raise Exception("servo number must be 2 4 6 8")
    now = servo_pos_tab[num]
    target = now + angle
    servo_pos_tab[num] = target
    print(num, target)
    move_none_block(num, target)
    
def claw_180(num):
    if num not in (2,4,6,8):
        raise Exception("servo number must be 2 4 6 8")
    now = servo_pos_tab[num]
    if now > 0:
        target = now - 2048
    else:
        target = now + 2048
    servo_pos_tab[num] = target
    print(num,target)
    move_none_block(num, target)
    
#     
# def set_zero(num):
#     for i in range (1, 9):
#         cmd = new_cmd(i, 3, [0x28,128])
#         ser.write(cmd)
#         recv = ser.read(6)
    
def all_servo_power_off():
    for i in range (1, 9):
        cmd = new_cmd(i, 3, [0x28,0])
        ser.write(cmd)
        recv = ser.read(6)
def all_servo_power_on():
    for i in range (1, 9):
        cmd = new_cmd(i, 3, [0x28,1])
        ser.write(cmd)
        recv = ser.read(6)
# 抓起魔方 1.27s
def pick_up_cube():
    move_none_block(3, 1650)
    move_none_block(7, 1650)
    #block_until_stop([3, 7])
    time.sleep(0.15)
    claw_cw(4)
    claw_ccw(8)
    #block_until_stop([4, 8])
    time.sleep(0.5)
    move_none_block(5, 1650)
    move_none_block(1, 1650)
    #block_until_stop([1, 5])
    time.sleep(0.15)
    move_none_block(3, 1600)# 校准位置
    move_none_block(7, 1600)
    move_none_block(5, 1600)
    move_none_block(1, 1600)
    block_until_stop([1, 5, 3, 7])
    move_none_block(3, 1650)
    move_none_block(7, 1650)
    move_none_block(5, 1650)
    move_none_block(1, 1650)
# 放下魔方
def put_dwon_cube():
    move_none_block(3, 1600)
    move_none_block(7, 1600)
    #block_until_stop([3,7])
    time.sleep(0.1)
    move_none_block(1, 2048)
    move_none_block(5, 2048)
    #block_until_stop([1,5])
    time.sleep(0.15)
    
    claw_ccw(4)
    claw_cw(8)
    block_until_stop([4,8])
    move_none_block(3, 1850)
    move_none_block(7, 1850)
    block_until_stop([3,7])

# 翻转魔方
def flip_cube(cmd_str):
    cube_cmd_dict = {"Y'":[3, 7, 1, 5, 4, 8],
                     "Y" :[3, 7, 1, 5, 8, 4],
                     "X'":[1, 5, 3, 7, 2, 6],
                     "X" :[1, 5, 3, 7, 6, 2]}
    t = cube_cmd_dict[cmd_str]
    
    move_none_block(t[0], 1600)# 抓的紧一些
    move_none_block(t[1], 1600)
    #block_until_stop([t[0], t[1]])
    move_none_block(t[2], 1900)# 不接触魔方
    move_none_block(t[3], 1900)
    #block_until_stop([t[2],t[3]])
    time.sleep(0.25)
    claw_ccw(t[4])
    claw_cw(t[5])
    time.sleep(0.65)
    #block_until_stop([t[4],t[5]]) #0.92-0.93s
    
    move_none_block(t[2], 1650)
    move_none_block(t[3], 1650)
    #block_until_stop([t[2], t[3]])
    time.sleep(0.15)
    move_none_block(t[0], 1900)
    move_none_block(t[1], 1900)
    #block_until_stop([t[0],t[1]])
    time.sleep(0.15)
    claw_up_down(t[4])
    claw_up_down(t[5])
    #block_until_stop([t[4], t[5]])
    time.sleep(0.5)
    move_none_block(t[0], 1650)
    move_none_block(t[1], 1650)
    time.sleep(0.15)
    #block_until_stop([t[0], t[1]])

# 拍照部分
def get_cube_image():
    move_none_block(3, 1600)# 抓的紧一些
    move_none_block(7, 1600)
    #block_until_stop_and_preview_camera([3,7])
    time.sleep(0.15)
    move_none_block(1, 1900)
    move_none_block(5, 1900)
    #block_until_stop_and_preview_camera([1,5])
    time.sleep(0.15)
    for i in (0,1,2,3):
        claw_ccw(4)
        claw_cw(8)
        block_until_stop_and_preview_camera([4,8])
        cap.grab()
        ret,img[i] = cap.retrieve()

    move_none_block(1, 1600)
    move_none_block(5, 1600)
    #block_until_stop_and_preview_camera([1,5])
    time.sleep(0.15)
    move_none_block(3, 1900)
    move_none_block(7, 1900)
    #block_until_stop_and_preview_camera([3,7])
    time.sleep(0.15)
    
    for i in (4,5,6,7):
        claw_ccw(2)
        claw_cw(6)
        block_until_stop_and_preview_camera([2,6])
        cap.grab()
        ret,img[i] = cap.retrieve()
    
    move_none_block(1, 1650)
    move_none_block(3, 1650)
    move_none_block(5, 1650)
    move_none_block(7, 1650)
    time.sleep(0.15)

# 拧魔方
def claw_route(cmd_str):
    fix = 35 #根据魔方和机械抓之间的间隙设置,乐高积木版本设置为100,3D打印版本间隙小,不用这个设计也能工作
    cube_cmd_dict = {"F":[1, 2], "R":[3, 4], "B":[5, 6], "L":[7, 8]}
    t = cube_cmd_dict[cmd_str[0]]
    frag_180 = False
    if len(cmd_str) == 1:
        move_1 = - 1024 - fix
        move_2 = fix
    elif cmd_str[1] == "'":
        move_1 = 1024 + fix
        move_2 = -fix
    elif cmd_str[1] == "2":
        frag_180 = True
        now = servo_pos_tab[ t[1] ]
        if now > 0:
            move_1 = - 2048 - fix
            move_2 = fix
        else:
            move_1 = 2048 + fix
            move_2 = -fix
    
    claw_route_any(t[1], move_1)
    block_until_stop([t[1]]) # 90: 0.92s 180: 1.29s
    claw_route_any(t[1], move_2)# 不用等待,和其他动作一起完成
    if not frag_180:
        move_none_block(t[0], 1900) # 远离一点点
        #block_until_stop([t[0]])
        time.sleep(0.15)
        claw_up_down(t[1])
        #block_until_stop([t[1]])
        time.sleep(0.5)
        move_none_block(t[0], 1650)
        #block_until_stop([t[0]])
        time.sleep(0.15)
# 两侧同时拧魔方
def claw_route_2(cmd_str_a, cmd_str_b):
    fix = 35
    cube_cmd_dict = {"F":[1, 2], "R":[3, 4], "B":[5, 6], "L":[7, 8]}
    t_a = cube_cmd_dict[cmd_str_a[0]]
    t_b = cube_cmd_dict[cmd_str_b[0]]
    t_ab = cmd_str_a[0] + cmd_str_b[0]
    if t_ab != 'FB' and t_ab != 'BF' and t_ab != 'LR' and t_ab != 'RL' :
        print("can not do this. ", cmd_str_a, cmd_str_b)
        return
    
    frag_180_a = False
    if len(cmd_str_a) == 1:
        move_1_a = - 1024 - fix
        move_2_a = fix
    elif cmd_str_a[1] == "'":
        move_1_a = 1024 + fix
        move_2_a = -fix
    elif cmd_str_a[1] == "2":
        frag_180_a = True
        now = servo_pos_tab[ t_a[1] ]
        if now > 0:
            move_1_a = - 2048 - fix
            move_2_a = fix
        else:
            move_1_a = 2048 + fix
            move_2_a = -fix
    
    frag_180_b = False
    if len(cmd_str_b) == 1:
        move_1_b = - 1024 - fix
        move_2_b = fix
    elif cmd_str_b[1] == "'":
        move_1_b = 1024 + fix
        move_2_b = -fix
    elif cmd_str_b[1] == "2":
        frag_180_b = True
        now = servo_pos_tab[ t_b[1] ]
        if now > 0:
            move_1_b = - 2048 - fix
            move_2_b = fix
        else:
            move_1_b = 2048 + fix
            move_2_b = -fix
    
    claw_route_any(t_a[1], move_1_a)
    claw_route_any(t_b[1], move_1_b)
    # 两组动作都是180或者90度,等待动作完成
    if not (frag_180_a ^ frag_180_b):
        block_until_stop([t_a[1], t_b[1]])
        claw_route_any(t_a[1], move_2_a)
        claw_route_any(t_b[1], move_2_b)
    else:
    # 两组动作一组180一组90度,等待90度动作完成
        if not frag_180_a:
            block_until_stop([t_a[1]])
            claw_route_any(t_a[1], move_2_a)
        if not frag_180_b:
            block_until_stop([t_b[1]])
            claw_route_any(t_b[1], move_2_b)
    # 两组都是180度,不用归位
    if frag_180_a and frag_180_b:
        #block_until_stop([t_a[1], t_b[1]])
        return
    if not frag_180_a:
        move_none_block(t_a[0], 1900)
    if not frag_180_b:
        move_none_block(t_b[0], 1900) # 远离一点点
    #block_until_stop([t_a[0], t_b[0]])
    time.sleep(0.15)
    if not frag_180_a:
        claw_up_down(t_a[1])
    if not frag_180_b:
        claw_up_down(t_b[1])
    #block_until_stop([t_a[1], t_b[1]])
    time.sleep(0.5)
    if not frag_180_a:
        move_none_block(t_a[0], 1650)
    if not frag_180_b:
        move_none_block(t_b[0], 1650)
    
    if frag_180_a ^ frag_180_b:
        if frag_180_a:
            claw_route_any(t_a[1], move_2_a)
        if frag_180_b:
            claw_route_any(t_b[1], move_2_b)
    #block_until_stop([t_a[0], t_b[0]])
    time.sleep(0.15)
def four_point_transform(image, rect):
    # 获取坐标点，并将它们分离开来
    # 图像尺寸
    maxWidth = 256
    maxHeight = 256
    # 构建新图片的4个坐标点
    edge = 2
    dst = np.array([
        [edge, edge],
        [maxWidth - 1 - edge, edge],
        [maxWidth - 1 - edge, maxHeight - 1 - edge],
        [edge, maxHeight - 1 - edge]], dtype = "float32")

    # 获取仿射变换矩阵并应用它
    M = cv2.getPerspectiveTransform(rect, dst)
    # 进行仿射变换
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    # 返回变换后的结果
    return warped

def mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(x,y)
    
def mark_cube_one_point(img, x_center, y_center, text):
    half_size = 12
    color_line = (0,0,0)
    color = [0,0,0]
    dot_count = 0
    for y in range(x_center-half_size, x_center+half_size,1):
        for x in range(y_center-half_size, y_center+half_size,1):
            color[0] += img[x,y,0]
            color[1] += img[x,y,1]
            color[2] += img[x,y,2]
            dot_count += 1
    color[0] = int(color[0]/dot_count)
    color[1] = int(color[1]/dot_count)
    color[2] = int(color[2]/dot_count)
    cv2.rectangle(img, (x_center-half_size, y_center-half_size),
                  (x_center+half_size, y_center+half_size), color_line)
    if text != -1:
        cv2.putText(img, str(text), (x_center+half_size+1,y_center+half_size),
                    cv2.FONT_HERSHEY_DUPLEX, 0.5, color_line)
    return color

def rgb2hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    m = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        if g >= b:
            h = ((g-b)/m)*60
        else:
            h = ((g-b)/m)*60 + 360
    elif mx == g:
        h = ((b-r)/m)*60 + 120
    elif mx == b:
        h = ((r-g)/m)*60 + 240
    if mx == 0:
        s = 0
    else:
        s = m/mx
    v = mx
    # h,s,v,值的范围分别是0-360, 0-1, 0-1
    return h, s, v

def mark_cube(img,face):
    color_line = (0,0,0)
    colors = [0,0,0,0,0,0,0,0,0]
    # 0 1 2
    # 3 4 5
    # 6 7 8
    colors[0] = mark_cube_one_point(img,42,42,face[0])
    colors[1] = mark_cube_one_point(img,128,42,face[1])
    colors[2] = mark_cube_one_point(img,214,42,face[2])
    colors[3] = mark_cube_one_point(img,42,128,face[3])
    colors[4] = mark_cube_one_point(img,128,128,face[4])
    colors[5] = mark_cube_one_point(img,214,128,face[5])
    colors[6] = mark_cube_one_point(img,42,214,face[6])
    colors[7] = mark_cube_one_point(img,128,214,face[7])
    colors[8] = mark_cube_one_point(img,214,214,face[8])
    
    hsv = [0] * 9
    for i in range(0,9):
        h,s,v = rgb2hsv(colors[i][2], colors[i][1], colors[i][0]);
        hsv[i] = [h,s,v,face[i]]
        
    return hsv

def serial_ping(num):
    cmd = new_cmd(num,1,[])
    ser.write(cmd)
    recv = ser.read(6)
    if len(recv) != 6:
        print("Error: self_test(): uart timeout error")
        return False
    else:
        return True
# 进行通信自检,上电后的第一次通信低概率是失败的,原因未知
def self_test():
    t1 = time.time()
    succ = True
    for x in range (0,10):
        for i in range(1,9):
            if serial_ping(i) == False:
                print("Error: self_test fail, loop = %d, servo ID = %d, retry..."%(x, i))
                succ = False
    if not succ:
        for x in range (0,10):
            for i in range(1,9):
                if serial_ping(i) == False:
                    print("Error: self_test fail, loop = %d, servo ID = %d"%(x, i))
                    quit()
    t2 = time.time()
    print("self test.  time=%.2f"%(t2-t1))
    
def class_color(hsv_9x5):
    min_std_shift = 0;
    min_std = 1000; # 0 - 360
    hsv_9x5_only_h = []
    for x in hsv_9x5:
        hsv_9x5_only_h.append(x[0])
    
    for shift in range(0,9):
        hsv_9x5_shift = list(hsv_9x5_only_h)
        for i in range(0, shift):
            hsv_9x5_shift[i] += 360
        hsv_9x5_shift = hsv_9x5_shift[shift:45] + hsv_9x5_shift[0:shift]
        
        std = [0] * 5
        for i in range(0,5):
            std[i] = np.std(hsv_9x5_shift[i * 9 : i * 9 + 9])
        std_mean = np.mean(std)
        
        if std_mean < min_std:
            min_std_shift = shift
            min_std = std_mean
            
    print("min_std_shift =",min_std_shift,"min_std =",min_std)
    return hsv_9x5[min_std_shift:45] + hsv_9x5[0:min_std_shift] 

# 转换kociemba返回的字符串
def flip_cube_update_state(now, cmd_str):
    ret = list(now)
    if cmd_str == 0:
        ret[0] = now[2]
        ret[2] = now[3]
        ret[3] = now[5]
        ret[5] = now[0]
    elif cmd_str == 1:
        ret[1] = now[0]
        ret[3] = now[1]
        ret[4] = now[3]
        ret[0] = now[4]
    return ret

def flip_cube_trans_cmd(now, cmd_str):
    if cmd_str[0] == now[4]:
        ret = "L" + cmd_str[1:]
    elif cmd_str[0] == now[2]:
        ret = "F" + cmd_str[1:]
    elif cmd_str[0] == now[1]:
        ret = "R" + cmd_str[1:]
    elif cmd_str[0] == now[5]:
        ret = "B" + cmd_str[1:]
    else:
        ret = ""
    return ret

def flip_cube_get_step(now, solve, step_int):
    filp_count = 0
    for step in solve:
        if step[0] == now[0] or step[0] == now[3]:
            d = step_int & 1
            step_int >>= 1
            filp_count += 1
            now = flip_cube_update_state(now, d)
    return filp_count

def flip_cube_find_min_step(solve):
    stat_now = ('U', 'R', 'F', 'D', 'L', 'B')
    min_count = flip_cube_get_step(stat_now, solve, 0)
    min_count_step_int = 0
    while True:
        for i in range (0, 2 ** min_count):
            count = flip_cube_get_step(stat_now, solve, i)
            if count < min_count:
                min_count = count
                min_count_step_int = i
                break
        else:
            break
        print("flip_cube_find_min_step: ", min_count, bin(min_count_step_int))

    step_int = min_count_step_int
    now = list(('U', 'R', 'F', 'D', 'L', 'B'))
    new_solve = []
    for step in solve:
        if step[0] == now[0] or step[0] == now[3]:
            d = step_int & 1
            step_int >>= 1
            #print(d)
            now = flip_cube_update_state(now, d)
            new_solve.append(["Y", "X"][d])
            new_solve.append(flip_cube_trans_cmd(now, step))
        else:
            new_solve.append(flip_cube_trans_cmd(now, step))
            
    return new_solve

#自定义比较函数
def comp_s(x,y):
    if x[1] > y[1]:
         return 1
    elif x[1] < y[1]:
        return -1
    else:
        return 0
def comp_h(x,y):
    if x[0] > y[0]:
        return 1
    elif x[0] < y[0]:
        return -1
    else :
        return 0
    
ser = serial.Serial("/dev/ttyAMA1", 115200, timeout=0.5)

### test start ###
# servo_pos_tab = [0] * 9
# init_servo_pos_tab(servo_pos_tab)
# pick_up_cube()
# for x in ("X", "Y", "X'", "Y'"):
#     flip_cube(x)
# for x in ("F", "R", "B" ,"L","F'", "R'", "B'" ,"L'","F2", "R2", "B2" ,"L2"):   
#     claw_route(x)  
# claw_route_2("F","B")
# claw_route_2("R","L")
# claw_route_2("F2","B")
# claw_route_2("R","L2")
# put_dwon_cube()
# all_servo_power_off()
# quit()
### test end

cap = cv2.VideoCapture(0)
if cap.isOpened() != True:
    print("camera error")
    quit()
    
self_test()
all_servo_power_on()
servo_pos_tab = [0] * 9

#截取需要的部分 TODO:开发图像识别算法,自动判断
# A -- B
# |    |
# D -- C
a = [166,90]
b = [468,96]
c = [466,397]
d = [164,390]
pts1 = np.array([b, c, d, a], dtype = "float32")
null_img = np.zeros((256, 256, 3), np.uint8)

while True:
    init_servo_pos_tab(servo_pos_tab)
    while True:
        ret,preview = cap.read()
        cv2.imshow("preview", preview)
        
        img0 = four_point_transform(preview, pts1)
        row1 = np.hstack((img0, null_img, null_img, null_img))
        row2 = np.hstack((null_img, null_img, null_img, null_img))
        img_disp = np.vstack((row1, row2))
        cv2.imshow("img", img_disp)
    
        key = cv2.waitKey(1)
        if key == 27:
            all_servo_power_off()
            cv2.destroyAllWindows()
            ser.close()
            quit()
        elif key != 255:
            break
    
    time_start = time.time()
    pick_up_cube()
    img = [0]*8
    get_cube_image()
    time_image = time.time()
    for i in range (0,8):
        img[i] = four_point_transform(img[i], pts1)

    #记录hsv颜色
    hsv_6_face = []
    hsv_6_face_54 = []
    hsv_6_face.extend(mark_cube(img[0], [47,50,53,46,49,52,45,48,51]))
    hsv_6_face.extend(mark_cube(img[1], [33,-1,27,34,31,28,35,-1,29]))
    hsv_6_face.extend(mark_cube(img[2], [24,21,18,25,22,19,26,23,20]))
    hsv_6_face.extend(mark_cube(img[3], [ 6,-1, 0, 7, 4, 1, 8,-1, 2]))
    hsv_6_face.extend(mark_cube(img[4], [ 9,10,11,12,13,14,15,16,17]))
    hsv_6_face.extend(mark_cube(img[5], [-1,32,-1,-1,-1,-1,-1,30,-1]))
    hsv_6_face.extend(mark_cube(img[6], [44,43,42,41,40,39,38,37,36]))
    hsv_6_face.extend(mark_cube(img[7], [-1, 3,-1,-1,-1,-1,-1, 5,-1]))
    
    # 显示处理好的图片
    row1 = np.hstack((img[0], img[1], img[2], img[3]))
    row2 = np.hstack((img[4], img[5], img[6], img[7]))
    img_disp = np.vstack((row1, row2))
    cv2.imshow("img", img_disp)
    k = cv2.waitKey(1)
        
    #剔除无用数据
    for item in hsv_6_face:
        if item[3] != -1:
            hsv_6_face_54.append(item)
    #print(hsv_6_face_54)
    #print(len(hsv_6_face_54))

    #根据饱和度挑出白色
    #cube_string = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
    cube_string = ['?']*54
    cube_string_kociemba = ['?']*54
    hsv_6_face_54 = sorted(hsv_6_face_54, key=cmp_to_key(comp_s))
    for i in hsv_6_face_54[0:9]:
        cube_string[i[3]] = 'W'
    #根据色调分离其他颜色
    hsv_6_face_54 = sorted(hsv_6_face_54[9:], key=cmp_to_key(comp_h))
    hsv_6_face_54 = class_color(hsv_6_face_54)
    for i in hsv_6_face_54[0:9]:
        cube_string[i[3]] = 'O'
    for i in hsv_6_face_54[9:18]:
        cube_string[i[3]] = 'Y'
    for i in hsv_6_face_54[18:27]:
        cube_string[i[3]] = 'G'
    for i in hsv_6_face_54[27:36]:
        cube_string[i[3]] = 'B'
    for i in hsv_6_face_54[36:45]:
        cube_string[i[3]] = 'R'
    print(''.join(cube_string))
    # RGBWOY -> URFDLB
    u_color = cube_string[4]
    r_color = cube_string[13]
    f_color = cube_string[22]
    d_color = cube_string[31]
    l_color = cube_string[40]
    b_color = cube_string[49]
    for i in range(0,54):
        if cube_string[i] == u_color:
            cube_string_kociemba[i] = 'U'
        elif cube_string[i] == r_color:
            cube_string_kociemba[i] = 'R'
        elif cube_string[i] == f_color:
            cube_string_kociemba[i] = 'F'
        elif cube_string[i] == d_color:
            cube_string_kociemba[i] = 'D'
        elif cube_string[i] == l_color:
            cube_string_kociemba[i] = 'L'
        elif cube_string[i] == b_color:
            cube_string_kociemba[i] = 'B'
    cube_string_kociemba = ''.join(cube_string_kociemba)
    len_solve = 0
    if "?" in cube_string_kociemba:
        print("Error: wrong cube partton")
        solve = []
    else:
        draw_cube(cube_string_kociemba, [u_color,r_color,f_color,d_color,l_color,b_color])
        print(cube_string_kociemba)
        
        if cube_string_kociemba != "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB":
            try:
                solve = kociemba.solve(cube_string_kociemba, max_depth=21)
                len_solve = len(solve.split(" "))
                print(solve)
                solve = flip_cube_find_min_step(solve.split(" "))
                print(solve)
            except Exception as e:
                #f_obj = open(file_name+".err","w")
                #f_obj.write(repr(e))
                #f_obj.close()
                print(repr(e))
                solve = []
        else:
            print("solved cube")
            solve = []
    time_calc = time.time()
            
    i = 0
    while i < len(solve):
        if i + 1 < len(solve):
            t_ab = solve[i][0] + solve[i+1][0]
            if t_ab != 'FB' and t_ab != 'BF' and t_ab != 'LR' and t_ab != 'RL' :
                step = solve[i]
                if step in ("X", "Y", "X'", "Y'"):
                    flip_cube(step)
                else:
                    claw_route(step)
                i =  i + 1
            else:
                claw_route_2(solve[i], solve[i+1])
                i =  i + 2
        else: # 剩下最后一步
            step = solve[i]
            if step in ("X", "Y", "X'", "Y'"):
                flip_cube(step)
            else:
                claw_route(step)
            i =  i + 1
    put_dwon_cube()
    time_end = time.time()
    print("总耗时 %.2fs"%(time_end - time_start))
    print("拍照耗时 %.2fs"%(time_image - time_start))
    print("计算耗时 %.2fs"%(time_calc - time_image))
    print("拧魔方耗时 %.2fs"%(time_end - time_calc))
    print("步骤数量 %d"%(len_solve))

