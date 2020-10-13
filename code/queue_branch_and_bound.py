import Config
import pickle
import numpy as np
import copy
import Task
import Mvn
import Server
import Cloud_remote
import sys

def queue_of_task(index_task):
    for i in range(len(index_task)-1):
        if tasks[index_task[i]].get_wi()>tasks[index_task[i+1]].get_wi():
            middlemen_task=index_task[i]
            index_task[i]=index_task[i+1]
            index_task[i+1]=middlemen_task
    return index_task

#mở dữ liệu khởi tạo các thiết bị tính toán(20 mvns,1 mecserver,1 remotecloud) và tập các công việc (100 task)
with open("./data/fog_device.p","rb") as fog:
    mvns,mecServer,remoteCloud=pickle.load(fog)
with open("./data/task.p","rb") as data:
    tasks=pickle.load(data)

def fitness_function(individual):
    cost=0
    time=0
    mvn_s=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    server=[]
    remote_Cloud=[]
    for index,node in enumerate(individual):
        if(node==-1):
            server.append(index)
        elif(node==0):
            remote_Cloud.append(index)
        elif(node>0):
            
            mvn_s[node-1].append(index)
    for index,tasks_mvn in enumerate(mvn_s):
        delta_Time=0
        '''
            như đã chứng minh thì hàng đợi tối ưu về thời gian tính toán 
            khi các công việc nào có kích thước wi bé sẽ được xử lí trước.
            sắp xếp các công việc theo thứ tự tăng của khối lượng công việc cần tính toán.
        '''
        tasks_mvn=queue_of_task(tasks_mvn)
        for task in tasks_mvn:
            cost+=Config.cost_rate*abs(mvns[index].get_rm())*tasks[task].get_di()/(1000*Config.Rm)*8
            cost+=Config.cost_MVN*tasks[task].get_wi()/1000
            time+=delta_Time+tasks[task].get_di()/(1000*Config.Rm)*8+tasks[task].get_wi()/(mvns[index].get_frequency()*1000)
            delta_Time+=tasks[task].get_di()/(1000*Config.Rm)*8+tasks[task].get_wi()/(mvns[index].get_frequency()*1000)
    """sử dụng giải thuậ kkt dễ dàng chứng minh được:
        chia tài nguyên hợp lí mecServer.get_frequency()*np.sqrt(Config.delta_t*tasks[i-1].get_wi())/sum;
        sum bằng tổng của các căn bậc 2 của wi i là id của các mvns
    """
    sum1=0
    for i in server:
        sum1+=np.sqrt(Config.delta_t*tasks[i-1].get_wi())
    for i in server:
        time+=(1/1000)*tasks[i-1].get_wi()/(mecServer.get_frequency()*np.sqrt(Config.delta_t*tasks[i-1].get_wi())/sum1)
    sum2=0
    for i in remote_Cloud:
        sum2+=np.sqrt(Config.delta_t*tasks[i-1].get_wi())
        cost+=Config.cost_RC*tasks[i-1].get_wi()/1000
    for i in remote_Cloud:
        time+=(1/1000)*(tasks[i-1].get_di())/Config.R0+(1/1000)*tasks[i-1].get_wi()/(remoteCloud.get_frequency()*np.sqrt(Config.delta_t*tasks[i-1].get_wi())/sum2)
    return Config.delta_t*time+Config.delta_c*cost,time,cost

min_fitness = 10000
m=np.zeros(10)
kiemtra=np.zeros(5)

def branchandbound(i:int):
    if(i==10):
        global min_fitness
        c=np.array(m,dtype=int)
        x=fitness_function(c)[0]
        if min_fitness>x:
            min_fitness=x
            print(min_fitness)
            print(c)
        return 0
    for j in range(-1,3):
            m[i]=j
            branchandbound(i+1)
branchandbound(0)