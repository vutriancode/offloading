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
import concurrent.futures


#khoi tao ca the init individual
# def queue_of_task(index_task):
#     for i in range(len(index_task)-1):
#         if tasks[index_task[i]].get_wi()>tasks[index_task[i+1]].get_wi():
#             middlemen_task=index_task[i]
#             index_task[i]=index_task[i+1]
#             index_task[i+1]=middlemen_task
#     return index_task
def tournament(population):
    a=np.random.randint(len(population),size=5)
    a=np.array(population)[a]
    minp=min(a,key=lambda x:fitness_function(x)[0])    
    return minp
def queue_of_task(index_task,index):
    for i in range(len(index_task)-1):
        for j in range(1,len(index_task)):
            if tasks[index_task[i]].get_di()/(1000*Config.Rm)*8+tasks[index_task[i]].get_res()/(1000*Config.Rm1)*8+tasks[index_task[i]].get_wi()/(mvns[index].get_frequency()*1000)\
                >tasks[index_task[j]].get_di()/(1000*Config.Rm)*8+tasks[index_task[j]].get_res()/(1000*Config.Rm1)*8+tasks[index_task[j]].get_wi()/(mvns[index].get_frequency()*1000):
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
    number_task_on_server=0
    number_task_on_cloud=0
    number_task_on_mvn=0
    cost=0
    time=0
    mvn_s=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    server=[]
    remote_Cloud=[]
    for index,node in enumerate(individual):
        if(node==-1):
            server.append(index)
            number_task_on_server+=1
        elif(node==0):
            remote_Cloud.append(index)
            number_task_on_cloud+=1
        elif(node>0):
            
            mvn_s[node-1].append(index)
            number_task_on_mvn+=1
    for index,tasks_mvn in enumerate(mvn_s):
        delta_Time=0
        '''
            như đã chứng minh thì hàng đợi tối ưu về thời gian tính toán 
            khi các công việc nào có kích thước wi bé sẽ được xử lí trước.
            sắp xếp các công việc theo thứ tự tăng của khối lượng công việc cần tính toán.
        '''
        tasks_mvn=queue_of_task(tasks_mvn,index)
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
    return Config.delta_t*time+Config.delta_c*cost,time,cost,number_task_on_cloud,number_task_on_server,number_task_on_mvn
    
initialization=[]
"""
Sử dụng thuật toán GA cho bài toán.
@para init_size_population:số lượng cá thể khởi tạo cho quần thể ban đầu
@para number_loop: số vòng lặp để tìm giá trị tối ưu
@para cut_poins: số điểm cắt khi lai ghép
"""
files=open("./result/tlm_1_100_1000_13_10.csv","w")

def GA(init_size_population:int,number_loop:int,total_server:int,total_task:int,cut_points:int):
    aaa=list()
    #khởi tạo quần thể
    initialization=[]
    first = time.time()
    for i in range(init_size_population):
        individual=np.random.randint(total_server,size=total_task)-1
        while (not check(individual)):
            individual=np.random.randint(total_server,size=total_task)-1
        initialization.append(individual)
    optimize_value=fitness_function(initialization[0])[0]
    optimize_individual=initialization[0]
    opt=[]
    for individual in initialization:
        if(optimize_value>fitness_function(individual)[0]):
            optimize_value=fitness_function(individual)[0]
            optimize_individual=copy.deepcopy(individual)
    aaa.append([fitness_function(optimize_individual)[1],fitness_function(optimize_individual)[2],fitness_function(optimize_individual)[0]])

    population=initialization


    for i in range(number_loop):
        #print(i)
        #lai ghép
        new_population=[]
        for j in range(int(init_size_population/2)):

            #lai ghép điểm cắt
            if cut_points==1:
                index=np.random.randint(1,len(initialization),size=2)
                first_individual=tournament(population)
                second_individual=tournament(population)
                point=np.random.randint(2,total_task-1)
                new_individual=np.concatenate((first_individual[0:point+1],second_individual[point+1:total_task]))
                new_individual1=np.concatenate((second_individual[0:point+1],first_individual[point+1:total_task]))

            #lai ghép điểm cắt
            else:
                index=np.random.randint(1,len(population),size=2)
                m=tournament(population)
                n=tournament(population)
                point=np.random.randint(3,99)
                point1=np.random.randint(2,point)
                new_individual=np.concatenate((m[0:point1+1],n[point1+1:point+1],m[point+1:100]))
                new_individual1=np.concatenate((n[0:point1+1],m[point1+1:point+1],n[point+1:100]))
            if(check(new_individual)):
                new_population.append(new_individual)
            if(check(new_individual1)):
                new_population.append(new_individual1)

        new_population=np.array(new_population)
        population=np.concatenate((population,new_population),axis=0)

        #đột biến
        for ii in range(int(init_size_population/10)):
            location=np.random.randint(0,total_task,size=1)
            value=np.random.randint(0,total_server,size=1)-1
            individual=np.random.randint(0,len(population),size=1)
            population[individual,location]=value
        object_population=[]
        for ii in population:
            k=fitness_function(ii)[0]
            if(optimize_value>k):
                optimize_value=k
                optimize_individual=copy.deepcopy(ii)
            object_population.append({'individual':ii,'fitness':k})
        object_population.sort(key=lambda x: x['fitness'])
        a=[]
        for ii in range(init_size_population):
            a.append(object_population[ii]["individual"])
            population=a
       
        opt=fitness_function(optimize_individual)
        aaa.append([opt[1],opt[2],opt[0]])
    return aaa
    print(times)
    files.write("times,"+str(times)+"\n")
    files.write("cloud,"+str(opt[3])+"\n")
    files.write("server,"+str(opt[4])+"\n")
    files.write("mvn,"+str(opt[5])+"\n")

    for iii in range(3):
        if iii%3==0:
            files.write("time,")
        if iii%3==1:
            files.write("coss,")
        if iii%3==2:
            files.write("fitness,")
        for kkk in aaa:

            files.write(str(kkk[iii])+",")
        files.write("\n")

for j in range (20):

    print("a")
    GA(100,1000,22,100,1)


    files.write("\n")
files.close()