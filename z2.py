import json
from collections import namedtuple

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
# zprocess1 = PCB(UID=1, name='考研', total_time=12 * 60, start_time='2024-1-1', dead_line='2024-12-20', Status='Ready',
#                 Priority=100, Total_run_time_day=0, Is_Regular='YES')
# zprocess2 = PCB(UID=2, name='项目报告', total_time=18, start_time='2024-2-1', dead_line='2024-2-15', Status='Ready',
#                 Priority=80, Total_run_time_day=0, Is_Regular='NO')
# zprocess3 = PCB(UID=3, name='玩原审', total_time=30, start_time='2024-1-1', dead_line=None, Status='Ready',
#                 Priority=50, Total_run_time_day=0, Is_Regular='YES')
# zprocess4 = PCB(UID=4, name='紧急会议', total_time=60, start_time=None, dead_line='2024-1-5 10:00', Status='Ready',
#                 Priority=200, Total_run_time_day=0, Is_Regular='NO')
# zprocess5 = PCB(UID=4, name='研究PWN', total_time=60, start_time=None, dead_line='2024-1-5 10:00', Status='Ready',
#                 Priority=50, Total_run_time_day=0, Is_Regular='YES')

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


delete = '0'
stime = -1

load = read_from_file('./appdata.txt')
PCB_B_list.extend(load)

PCB_B_list.sort(key=lambda x: x.Priority, reverse=True)
while stime <= 8 * 60:
    bk = 2
    stime += 1
    if PCB_B_list:  # 如果列表不为空
        if PCB_B_list[0].Total_run_time_day >= 30:
            PCB_B_list[0] = PCB_B_list[0]._replace(Status='Ready',Total_run_time_day=0)
            # PCB_B_list[0] = PCB_B_list[1]
            # PCB_B_list[0] = tmp
            PCB_B_list.sort(key=lambda x: x.Priority, reverse=True)
        if stime % bk == 0:
            delete = input("del? (输入 1 删除第一个 PCB): ")  # 获取用户输入
        if delete == '1':
            if PCB_B_list:  # 确保列表不为空
                PCB_B_list.pop(0)  # 删除第一个 PCB
                delete = '0'
        if PCB_B_list:  # 再次检查列表，以防在删除后为空
            first = PCB_B_list.pop(0)  # 弹出第一个 PCB 并处理它
            first = first._replace(Status='Run',Priority=first.Priority * 0.978,Total_run_time_day=first.Total_run_time_day + 1)
            for i, p in enumerate(PCB_B_list):
                PCB_B_list[i] = p._replace(Status='Ready',Priority=p.Priority * 1.01)
            PCB_B_list.insert(0, first)
        if stime % bk == 0:
            print("     time:" + str(stime // 60) + ":" + str(stime % 60))
            for p in PCB_B_list:
                print(str(p.name) + " 优先级 " + str("%.1f" % p.Priority) +" 运行时间 " + str(p.Total_run_time_day) )

# delete = '0'
#
#
# load = read_from_file('./appdata.txt')
# PCB_B_list.extend(load)
#
#
# stime = -1
# PCB_B_list.sort(key=lambda x: x.Priority, reverse=True)
# while stime <= 8 * 60:
#     stime += 1
#     if PCB_B_list:  # 如果列表不为空
#         if PCB_B_list[0].Total_run_time_day >= 30:
#             PCB_B_list[0] = PCB_B_list[0]._replace(Status='Ready',Total_run_time_day=0)
#             PCB_B_list.sort(key=lambda x: x.Priority, reverse=True)
#         if delete == '1':
#             if PCB_B_list:  # 确保列表不为空
#                 PCB_B_list.pop(0)  # 删除第一个 PCB
#                 delete = '0'
#         if PCB_B_list:  # 再次检查列表，以防在删除后为空
#             first = PCB_B_list.pop(0)  # 弹出第一个 PCB 并处理它
#             first = first._replace(Status='Run',Priority=first.Priority * 0.978,Total_run_time_day=first.Total_run_time_day + 1)
#             for i, p in enumerate(PCB_B_list):
#                 PCB_B_list[i] = p._replace(Status='Ready',Priority=p.Priority * 1.01)
#             PCB_B_list.insert(0, first)
#         if stime > 8*60-2:
#             print("     time:" + str(stime // 60) + ":" + str(stime % 60))
#             for p in PCB_B_list:
#                 print(str(p.name) + " 优先级 " + str("%.1f" % p.Priority) +" 运行时间 " + str(p.Total_run_time_day) )


# 任务：
# 1,GUI，绑定按钮、表格、数字时钟、显示系统
# 2,写出功能：创建新pcb，调整文件读取，
# 3，做出线程，做出线程安全，做出非阻塞
# 3，优化GUI











            # while stime <= 8 * 60:
#     stime += 1
#     if not PCB_B_list:
#         pass
#     if PCB_B_list:
#         # print("PCB_B_list")
#         # print(PCB_B_list)
#         i = 0
#         if stime % 10 == 0:
#             delete = input("del?")
#             # print("delete")
#             # print(delete)
#         if delete == '1':
#             PCB_B_list.pop(0)
#         first = PCB_B_list.pop()
#         # print("first")
#         # print(first)
#         # print("PCB_B_list")
#         # print(PCB_B_list)
#         first = first._replace(Status='Run')
#         first = first._replace(Priority=first.Priority * 0.978)
#         first = first._replace(Total_run_time_day=first.Total_run_time_day + 1)
#         for p in PCB_B_list:
#             p = p._replace(Status='Ready')
#             p = p._replace(Priority=p.Priority * 1.01)
#             PCB_B_list[i] = p  # 保存PCB的修改
#             i += 1
#         PCB_B_list.insert(0, first)
#
#     # print
#     if stime % 10 == 0:
#         print("     time:" + str(stime // 60) + ":" + str(stime % 60))
#         for p in PCB_B_list:
#             print(str(p.name) + str(p.Priority))
