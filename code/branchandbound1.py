import Config
import pickle
import numpy as np
import copy
import Task
import Mvn
import Server
import Cloud_remote
import sys
import time as tm
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
with open("./data/task1.p","rb") as data:
    tasks=pickle.load(data)

def fitness_function(individual,sobus):
    cost=0
    time=0
    for index,node in enumerate(individual):
        if index==0 and node>0:
            time+=node*(1/1000)*1000/(mecServer.get_frequency()/node)
        elif index==sobus+1 and node>0:
            time+=node*(1/1000)*1000/(remoteCloud.get_frequency()/node)+node*(1/1000)*(2000)/Config.R0
            cost+=node*Config.cost_RC*1000/1000
        elif index>=1 and index<=sobus:
            time+=((node+1)*node/2)*(1/1000)*1000/(mvns[index-1].get_frequency())+node*(1/1000)*(2000)/Config.Rm
            cost+=node*Config.cost_MVN*1000/1000
    return Config.delta_t*time+Config.delta_c*cost,time,cost
def kiemtra(individual,sobus):
    time=0
    kiemtra=[]
    for index,node in enumerate(individual):
        if index>=1 and index<=sobus:
            time=((node+1)*node/2)*(1/1000)*1000/(mvns[index-1].get_frequency())+node*(1/1000)*(2000)/Config.Rm
            kiemtra.append(time)
    for index,i in enumerate(kiemtra):
        if mvns[index].get_delta_time()<i:
            return False
    return True


min_fitness = 10000
m=np.zeros(6)

def branchandbound(i:int,du:int,sobus):
    if(i==sobus+1):
        m[sobus+1]=du
        global min_fitness
        c=np.array(m,dtype=int)
        x=fitness_function(c,sobus)
        if min_fitness>x[0]:
            min_fitness=x[0]
            print(x)
            print(c)

        return 0

    elif i==0:
        for j in range(0,du+1):
            m[i]=j
            if(fitness_function(m[:i+1],sobus)[0]+0.5*(du-j)*(1/1000)*1000/(remoteCloud.get_frequency())+(du-j)*(1/1000)*(2000)/Config.R0+0.5*(du-j)*Config.cost_MVN*1000/1000<min_fitness) and kiemtra(m[:i+1],sobus):

                branchandbound(i+1,du-j,sobus)
    else:
        for j in range(0,2):
            m[i]=j
            if(fitness_function(m[:i+1],sobus)[0]+0.5*(du-j)*(1/1000)*1000/(remoteCloud.get_frequency())+(du-j)*(1/1000)*(2000)/Config.R0+0.5*(du-j)*Config.cost_MVN*1000/1000<min_fitness) and kiemtra(m[:i+1],sobus):

                branchandbound(i+1,du-j,sobus)

first = tm.time()
branchandbound(0,100,3)
print(str(tm.time()-first))
