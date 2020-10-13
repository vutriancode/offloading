import Config
import pickle
import numpy as np
import copy
import Task
import Mvn
import Server
import Cloud_remote
import sys
import time
#khoi tao ca the init individual
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


'''
Với mỗi một khởi tạo kích thước ma trận(1,length of tasks).
giá trị của mỗi một node của ma trận là giá trị từ [-1,0,...,Mvs.size()].
hàm check() để kiểm tra mỗi cá thể có thỏa mãn yêu cầu của bài toán hay không. 
'''
def check(individual):
    mvn_s=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    isAccept=True

    for index,node in enumerate(individual):
        if(node>0):
            mvn_s[node-1].append(index)
    
    for index,mvn in enumerate(mvn_s):
        time=0
        for id_of_task in mvn:
            time+=tasks[id_of_task].get_di()/(1000*Config.Rm)*8+tasks[id_of_task].get_res()/(1000*Config.Rm1)*8+tasks[id_of_task].get_wi()/(mvns[index].get_frequency()*1000)
        if(time>mvns[index].get_delta_time()):    
            isAccept=False
    return isAccept
'''
tính giá trị hàm fitness của bài toán
@parameter:individual là một một cá thể trong quần thể
'''

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
            cost+=Config.cost_MVN*tasks[task].get_wi()/1000
            time+=delta_Time+tasks[task].get_di()/(1000*Config.Rm)*8+tasks[task].get_res()/(1000*Config.Rm1)*8+tasks[task].get_wi()/(mvns[index].get_frequency()*1000)
            delta_Time+=tasks[task].get_di()/(1000*Config.Rm)*8+tasks[task].get_res()/(1000*Config.Rm1)*8+tasks[task].get_wi()/(mvns[index].get_frequency()*1000)
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
        time+=(1/1000)*(tasks[i-1].get_di()+tasks[i-1].get_res())/Config.R0+(1/1000)*tasks[i-1].get_wi()/(remoteCloud.get_frequency()*np.sqrt(Config.delta_t*tasks[i-1].get_wi())/sum2)
    return Config.delta_t*time+Config.delta_c*cost,time,cost
def hill_climbling(initation,number_of_task:int,number_of_node:int):
    files=open("./result/h_10.csv","w")
    global_fitness_min=float('inf')
    result=[]
    for i in range(initation):
        result_local=[]
        node=np.random.randint(0,number_of_node,number_of_task)-1
        local_fitness_min=fitness_function(node)
        h=True
        while h==True:
            h=False
            for j in range(0,number_of_task):
                a=node[j]
                for k in range(0,number_of_node):
                    if k-1!=a:
                        node[j]=k-1
                        m=fitness_function(node)
                        if m[0]<local_fitness_min[0]:
                            local_fitness_min=m
                            h=True
                            result_local.append(m)
                            break
                        else:
                            node[j]=a
                if h==True:
                    break
        for iii in range(3):
            if iii%3==0:
                files.write("fitness,")
            if iii%3==1:
                files.write("time,")
            if iii%3==2:
                files.write("cost,")
            for kkk in result_local:

                files.write(str(kkk[iii])+",")
            files.write("\n")

        if local_fitness_min[0]<global_fitness_min:
            global_fitness_min=local_fitness_min[0]

    return global_fitness_min 


print(hill_climbling(1,100,22))

