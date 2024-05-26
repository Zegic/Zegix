import json
import queue
import time
import datetime
from collections import namedtuple
from typing import List
import math

print("hello this is ZGXOS and you can call me Zegix")
print()

# 设计一下python程序怎么写
#
# 需求：
# 应该具有读写磁盘、获取系统时间等功能
# 设计：
# 进程信息：进程名字、进程的线程（子进程）、进程总计需要的时间、进程是否为周期服务、进程截止的时间、
# 调度信息：优先级，开始的时间，结束的时间
# 操作：对进程有挂起，阻塞。zos则创新，操作有，全机暂停，
# 时间片：5min？30min？
# 调度算法：
# 采用轮转调度算法，
# 采用优先级调度算法，动态优先级，随等待时间的提高，优先权逐渐提高。进程运行中，优先级逐渐变低，防止长进程长时间抢占cpu
# 采用多队列调度算法，设置不同的就绪队列，不同队列采用不同算法，进程和队列之间优先级不同。
# 进程切换时机，时间片未用完而进程完成，进程未完成但时间片用完
# 改版多级反馈队列调度算法
# 设置2个就绪队列，时间为：A 10min，B 30min
# 队列内按优先级排序，所有【即时、中断】任务在A队列，A队列为先进先服务。时间片结束后，进入B队列
# 紧急和中断，进入A队列。不允许抢占cpu。BC队列的任务即使优先级超过了当前cpu运行的任务，也不允许立即抢占cpu
# 优先级设置：手动设置部分进程优先级，其他进程，根据截止时间增加优先级，
#         松弛度=截止日期-运行时间，比如今天周一，周五考试，需要三天时间准备，则松弛度=1天
# 系统调度计算最小单位：分钟


# 重新设计
# A队列为即时队列，采用先来先服务，时间片用完后轮转至队伍末尾。当A中的进程被用户操作为“挂起、阻塞”时，移交B
# B队列为普通队列，采用优先级调度，时间片用完后根据优先级继续计算。优先级算法应该保证不会饥饿，又能保证任务尽量做完。
# 设立计数器：今日调度程序运行时间、每个任务的总运行时间

PCB = namedtuple('PCB', [
    'UID',  # 进程UID
    'name',  # 进程名字，如“考研”
    'total_time',  # 进程所需总时间 ，按分钟单位
    'start_time',  # 进程开始的时间
    'dead_line',  # 进程截止日期
    'Status',  # 进程状态，如挂起、阻塞、就绪、运行、终止
    'Priority',  # 优先级，0最小，一般50，最大100，即时程序999
    'Total_run_time_day',  # 今天的运行时间，会影响优先级调度
    'Is_Regular'])  # 是否周期任务
# test
zprocess1 = PCB(UID=1, name='考研', total_time=12 * 60, start_time='2024-1-1', dead_line='2024-12-20', Status='Ready',
                Priority=100, Total_run_time_day=0, Is_Regular='YES')
zprocess2 = PCB(UID=2, name='项目报告', total_time=18, start_time='2024-2-1', dead_line='2024-2-15', Status='Ready',
                Priority=80, Total_run_time_day=0, Is_Regular='NO')
zprocess3 = PCB(UID=3, name='玩原审', total_time=30, start_time='2024-1-1', dead_line=None, Status='Ready',
                Priority=50, Total_run_time_day=0, Is_Regular='YES')
zprocess4 = PCB(UID=4, name='紧急会议', total_time=60, start_time=None, dead_line='2024-1-5 10:00', Status='Ready',
                Priority=200, Total_run_time_day=0, Is_Regular='NO')
zprocess5 = PCB(UID=4, name='研究PWN', total_time=60, start_time=None, dead_line='2024-1-5 10:00', Status='Ready',
                Priority=50, Total_run_time_day=0, Is_Regular='YES')

PCB_A_list = []
PCB_B_list = []


def write_to_file(filename, pcbs):
    with open(filename, 'w') as f:
        for pcb in pcbs:
            # 将PCB实例转换为字典，因为json不能直接处理namedtuple
            pcb_dict = pcb._asdict()
            json.dump(pcb_dict, f)
            f.write('\n')  # 在每个PCB字典后添加换行符以便分隔


def read_from_file(filename):
    pcbs = []
    with open(filename, 'r') as f:
        for line in f:
            # 从文件中读取并解析字典
            pcb_dict = json.loads(line)
            # 使用PCB namedtuple从字典创建实例
            pcb = PCB(**pcb_dict)
            pcbs.append(pcb)
    return pcbs





def a_add(pcb):
    PCB_A_list.append(pcb)


def a_print():
    stra = ''
    for q in PCB_A_list:
        stra = stra + '\n' + q
    print(stra)


def a_update():
    if PCB_A_list:
        a = PCB_A_list
    return


def b_update():
    # PCB_B_list.sort(key=lambda x: x.Priority, reverse=True)
    if not PCB_B_list:
        pass
    if PCB_B_list:
        i = 0
        PCB_B_list.sort(key=lambda x: x.Priority, reverse=True)
        for p in PCB_B_list:
            if i == 0:
                p = p._replace(Priority=p.Priority * 0.978)
            if i != 0:
                p = p._replace(Priority=p.Priority * 1.01)
            p = p._replace(Total_run_time_day=p.Total_run_time_day + 1)
            PCB_B_list[i] = p
            i += 1


def b_add(pcb):
    PCB_B_list.append(pcb)


def b_print():
    stb = ''
    PCB_B_list.sort(key=lambda x: x.Priority, reverse=True)
    for p in PCB_B_list:
        stb = stb + '\n' + p
    print(stb)

# def p_print():
#     print(str(p.name) + str(p.Priority))
#     print("     time:" + str(time // 60) + ":" + str(time % 60))

#
# def __init__(self, UID, name, total_time, start_time, dead_line, Status, Priority, Total_run_time_day, Is_Regular):
#     self.UID = UID
#     self.name = name
#     self.total_time = total_time
#     self.start_time = start_time
#     self.dead_line = dead_line
#     self.Status = Status
#     self.Priority = Priority
#     self.Total_run_time_day = Total_run_time_day
#     self.Is_Regular = Is_Regular


# def sort_and_insert_pcb(pcb_list: List[PCB], new_pcb: PCB):
#     # 插入新的PCB并重新排序列表
#     pcb_list.append(new_pcb)
#     pcb_list.sort(key=lambda x: x.Priority, reverse=True)  # 按照优先级从高到低排序
#
#
# PCB_A_list = []  # 5min
# PCB_B_list = []  # 15min
# PCB_C_list = []  # 30min
# sort_and_insert_pcb(PCB_B_list, zprocess1)
# sort_and_insert_pcb(PCB_B_list, zprocess2)
# sort_and_insert_pcb(PCB_B_list, zprocess3)
# sort_and_insert_pcb(PCB_B_list, zprocess4)


# def process_scheduling(time):
#     # if stime % 5 == 0:
#     #     print_time += print_and_remove_A(stime)
#     # if stime % 15 == 0:
#     #     print_time += print_and_remove_B(stime)
#     # if stime % 30 == 0:
#     #     print_time += print_and_remove_C(stime)
#     # if print_time != 0:
#     #     print("time:" + str(stime // 60) + ":" + str(stime % 60))
#     # PCB = namedtuple('PCB', [
#     #     'UID',  # 进程UID
#     #     'name',  # 进程名字，如“考研”
#     #     'total_time',  # 进程所需总时间 ，按分钟单位
#     #     'start_time',  # 进程开始的时间
#     #     'dead_line',  # 进程截止日期
#     #     'Status',  # 进程状态，如挂起、阻塞、就绪、运行、终止
#     #     'Priority',  # 优先级，0最小，一般50，最大100，即时程序999
#     #     'Total_run_time_day',  # 今天的运行时间，会影响优先级调度
#     #     'Is_Regular'])  # 是否周期任务
#     idxa = 0
#     idxb = 0
#     idxc = 0
#     for pcba in PCB_A_list:
#         PCB_A_list.sort(key=lambda x: x.Priority, reverse=True)
#         # print("time:" + str(stime // 60) + ":" + str(stime % 60))
#         # print(pcba)
#         if idxa != 0:  # pcba.Status == 'Ready' and
#             pcba = pcba._replace(Priority=pcba.Priority + 1)
#         if idxa == 0:
#             pcba = pcba._replace(Priority=pcba.Priority - 1)
#         pcba = pcba._replace(Total_run_time_day=pcba.Total_run_time_day + 1)
#         PCB_A_list[idxa] = pcba
#         if pcba.Total_run_time_day > 5:
#             PCB_B_list.append(PCB_A_list[idxa])
#             del PCB_A_list[idxa]
#         idxa += 1
#     for pcbb in PCB_B_list:
#         PCB_B_list.sort(key=lambda x: x.Priority, reverse=True)
#         pcbb = pcbb._replace(Total_run_time_day=pcbb.Total_run_time_day + 1)
#         PCB_B_list[idxb] = pcbb
#         if pcbb.Total_run_time_day > 20:
#             PCB_C_list.append(PCB_B_list[idxb])
#             del PCB_B_list[idxb]
#         idxb += 1
#     for pcbc in PCB_C_list:
#         PCB_C_list.sort(key=lambda x: x.Priority, reverse=True)
#         # print(PCB_C_list[idxc])
#         pcbc = pcbc._replace(Total_run_time_day=pcbc.Total_run_time_day + 1)
#         PCB_C_list[idxc] = pcbc
#         # if pcbc.Total_run_time_day >= pcbc.total_time:
#         #     del PCB_C_list[0]    #测试用所以删除，实则需要用户自己删除
#         idxc += 1
#     # print("A"+str(PCB_A_list)+"B"+str(PCB_B_list)+"C"+str(PCB_C_list))
#     if time % 4 == 0:
#         print("     time:" + str(time // 60) + ":" + str(time % 60))
#     for p in PCB_A_list:
#         print("A:" + str(p.name) + str(p.Priority))
#     for p in PCB_B_list:
#         print("B:" + str(p.name) + str(p.Priority))
#     for p in PCB_C_list:
#         print("C:" + str(p.name) + str(p.Priority))

#     'UID',  # 进程UID
#     'name',  # 进程名字，如“考研”
#     'total_time',  # 进程所需总时间 ，按分钟单位
#     'start_time',  # 进程开始的时间
#     'dead_line',  # 进程截止日期
#     'Status',  # 进程状态，如挂起、阻塞、就绪、运行、终止
#     'Priority',  # 优先级，0最小，一般50，最大100，即时程序999
#     'Total_run_time_day',  # 今天的运行时间，会影响优先级调度
#     'Is_Regular'])  # 是否周期任务


# zprocess = zprocess._replace(Priority=zprocess.Priority/2)
#
# def proc_sche_A(time):
#     if not PCB_A_list:
#         proc_sche_B(time)
#     if PCB_A_list:
#         i = 0
#         PCB_A_list.sort(key=lambda x: x.Priority, reverse=True)
#         for p in PCB_A_list:
#             if i == 0:
#                 p = p._replace(Priority=p.Priority*0.978)
#             if i != 0:
#                 p = p._replace(Priority=p.Priority*1.01)
#             p = p._replace(Total_run_time_day=p.Total_run_time_day + 1)
#             PCB_A_list[i] = p
#             i += 1
#
#         print("     time:" + str(time // 60) + ":" + str(time % 60))
#         for p in PCB_A_list:
#             print(str(p.name) + str(p.Priority))
#         for p in PCB_B_list:
#             print(str(p.name) + str(p.Priority))
#         for p in PCB_C_list:
#             print(str(p.name) + str(p.Priority))
# def proc_sche_B(time):
#     if not PCB_B_list:
#         pass
#     if PCB_B_list:
#         i = 0
#         PCB_B_list.sort(key=lambda x: x.Priority, reverse=True)
#         for p in PCB_B_list:
#
#             if i == 0:
#                 p = p._replace(Priority=p.Priority*0.978)
#             if i != 0:
#                 p = p._replace(Priority=p.Priority*1.01)
#             p = p._replace(Total_run_time_day=p.Total_run_time_day + 1)
#             PCB_B_list[i] = p
#             i += 1
#         print("     time:" + str(time // 60) + ":" + str(time % 60))
#         for p in PCB_B_list:
#             print(str(p.name) + str(p.Priority))
#         for p in PCB_C_list:
#             print(str(p.name) + str(p.Priority))
#
# # def proc_sche_C(time):
# #     if not proc_sche_C:
# #         pass
# #     if proc_sche_C:
# #         i = 0
# #         PCB_B_list.sort(key=lambda x: x.Priority, reverse=True)
# #         for p in PCB_B_list:
# #
# #             if i == 0:
# #                 p = p._replace(Priority=p.Priority * 0.978)
# #             if i != 0:
# #                 p = p._replace(Priority=p.Priority * 1.01)
# #             p = p._replace(Total_run_time_day=p.Total_run_time_day + 1)
# #             PCB_B_list[i] = p
# #             i += 1
# #
# #         # time_pian = 1
# #         # if time % time_pian == 0:
# #         print("     time:" + str(time // 60) + ":" + str(time % 60))
# #         for p in PCB_C_list:
# #             print(str(p.name) + str(p.Priority))
#
#
# # stime = -1
# # while stime <= (24 * 60) / 5:
# #     stime += 1
# #     rtime = stime * 5
# #     # process_scheduling(stime)
# #     proc_sche_A(rtime)
# #     # print("time:" + str(stime // 60) + ":" + str(stime % 60))
#
#
# # 模拟时间运动，每个1表示1分钟
#
#
# def print_list():
#     pass
#
#
# def check_time(wanted_time):
#     time.sleep(1)
#     current_time = datetime.datetime.now()
#     if current_time >= wanted_time:
#         return True
#     else:
#         return False
# def main():






stime = -1

# process_scheduling(stime)
# proc_sche_A(rtime)

# a_add(zprocess4)
# b_add(zprocess1)
# b_add(zprocess2)
# b_add(zprocess3)
# b_add(zprocess5)
print(zprocess1)
write_to_file('./appdata.txt', [zprocess1,zprocess2,zprocess3,zprocess4,zprocess5])
l = read_from_file('./appdata.txt')
for pcb in l:
    PCB_B_list.append(pcb)
    print(PCB_B_list)

# while stime <= (24 * 60) / 5:
#     stime += 1
#     rtime = stime * 5

# if

# a_print()
# b_print()