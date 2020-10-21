import Config
import pickle
import numpy as np
import copy
import Task
import Mvn
import Server
import Cloud_remote
import sys
#khoi tao ca the init individual
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
with open("E:\\GA\\vutrian\\data\\fog_device.p","rb") as fog:
    mvns,mecServer,remoteCloud=pickle.load(fog)
with open("E:\\GA\\vutrian\\data\\task.p","rb") as data:
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
        tasks_mvn=queue_of_task(tasks_mvn,index)
        for task in tasks_mvn:
            cost+=Config.cost_rate*abs(mvns[index].get_rm())*tasks[task].get_di()/(1000*Config.Rm)*8
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







def roulette_select(total_fitness, population):
    fitness_slice = np.random.rand() * total_fitness
    fitness_so_far = 0.0
    for i, individual in enumerate(population):
        fitness_so_far += fitness_function(individual)[0]
        if fitness_so_far >= fitness_slice:
            return i
    return 0






def uniform_crossover(parent_1, parent_2):
    offspring1 = copy.deepcopy(parent_1)
    offspring2 = copy.deepcopy(parent_2)
    for i in range(len(parent_1)):
        if np.random.rand() < 0.5:
            offspring1[i] = parent_2[i]
            offspring2[i] = parent_1[i]
    return offspring1, offspring2


# def rank_based_selection(population):
#     ps = len(population)
#     fitness_value = sorted(population,reverse=True)

#     fittest_individual = max(fitness_value)
#     medium_individual = np.median(fitness_value)
#     selective_pressure = fittest_individual - medium_individual
#     j_value = 1
#     a_value = np.random.rand()  

#     for i in range(ps):
#         if ps == 0:
#             return None
#         elif ps == 1:
#             return 0
#         else:
#             range_value = selective_pressure - (2*(selective_pressure - 1)*(j_value - 1))/( ps - 1) 
#             prb = range_value/ps
#             if prb > a_value:
#                 return i
#         j_value +=1
    

def sum_fitness_value(population):
    total = 0.0
    for individual in population:
        fitness_value = fitness_function(individual)[0]
        total += fitness_value
    return total


initialization=[]
"""
Sử dụng thuật toán GA cho bài toán.
@para init_size_population:số lượng cá thể khởi tạo cho quần thể ban đầu
@para number_loop: số vòng lặp để tìm giá trị tối ưu
@para cut_poins: số điểm cắt khi lai ghép
"""


def GA(init_size_population:int,  number_loop:int,  total_server: int,total_task:int,cut_points:int, number):
    files=open("E:\\GA\\vutrian\\result\\KQinit_ttest2___1__"+str(init_size_population)+"-task_"+str(total_task)+"-totalserver_"+str(total_server)+"-numberloop_"+str(number_loop)+"-points_"+str(cut_points)+"_" + number+".csv","w")
    files.write("index,time,cost,value\n")
    #khởi tạo quần thể
    initialization = []
    for i in range(init_size_population):
        individual=np.random.randint(total_server,size=total_task)-1
        while (not check(individual)): #kiểm tra hợp lệ
            individual=np.random.randint(total_server,size=total_task)-1
        initialization.append(individual)
    optimize_value=fitness_function(initialization[0])[0]
    optimize_individual=initialization[0]



    #tìm cá thể tốt nhất trong init_pop
    for individual in initialization:
        if(optimize_value>fitness_function(individual)[0]):
            optimize_value=fitness_function(individual)[0] 
            optimize_individual=copy.deepcopy(individual) #optimize_individual ca the tot nhan trong pop

    population=initialization
    KQ=str(i)+","+str(fitness_function(optimize_individual)[1])+","+str(fitness_function(optimize_individual)[2])+","+str(fitness_function(optimize_individual)[0])+"\n"
    files.write(KQ)
 
    for i in range(number_loop):
        #lai ghép
        new_population=[] #off được đưa vào new_pop

        #for rank selection
        # population_with_fitness = []
        # for individual in population:
        #     population_with_fitness.append(fitness_function(individual)[0])

        #for roulette wheel
        total_fitness_value = sum_fitness_value(population)

        for j in range(int(init_size_population/2)):
            #crossover
            #lai ghép điểm cắt
            if cut_points==1:

                # rank-based selection
                # index_0 = rank_based_selection(population_with_fitness)
                # import pdb; pdb.set_trace()
                # index_1 = rank_based_selection(population_with_fitness)
                # while index_0 == index_1:
                #     index_1 = roulette_select(total_fitness_value, population)
                # first_individual=population[index_0] #parent_1
                # second_individual=population[index_1] #parent_2
                
                # roulette wheel selection
                index_0 = roulette_select(total_fitness_value, population)
                index_1 = roulette_select(total_fitness_value, population)
                while index_0 == index_1:
                    index_1 = roulette_select(total_fitness_value, population)
                first_individual=population[index_0] #parent_1
                second_individual=population[index_1] #parent_2
                new_individual, new_individual1 = uniform_crossover(first_individual, second_individual)


                #random selection
                # index=np.random.randint(1,len(population),size=2) 
                # first_individual=population[index[0]] #parent_1
                # second_individual=population[index[1]] #parent_2

                # point=np.random.randint(2,total_task-1)
                # new_individual=np.concatenate((first_individual[0:point+1],second_individual[point+1:total_task]))
                # new_individual1=np.concatenate((second_individual[0:point+1],first_individual[point+1:total_task]))
            
            
            #lai ghép điểm cắt
            elif cut_points == 2:

                # index=np.random.randint(1,len(population),size=2)
                # m=population[index[0]]
                # n=population[index[1]]

                # roulette wheel selection
                index_0 = roulette_select(total_fitness_value, population)
                index_1 = roulette_select(total_fitness_value, population)
                while index_0 == index_1:
                    index_1 = roulette_select(total_fitness_value, population)
                m = population[index_0] #parent_1
                n = population[index_1] #parent_2
                new_individual, new_individual1 = uniform_crossover(m,n)

                # point=np.random.randint(3,99)
                # point1=np.random.randint(2,point)
                # new_individual=np.concatenate((m[0:point1+1],n[point1+1:point+1],m[point+1:100]))
                # new_individual1=np.concatenate((n[0:point1+1],m[point1+1:point+1],n[point+1:100]))

                
            else:
                index_0 = roulette_select(total_fitness_value, population)
                index_1 = roulette_select(total_fitness_value, population)
                while index_0 == index_1:
                    index_1 = roulette_select(total_fitness_value, population)
                parent_1 = population[index_0] 
                parent_2 = population[index_1] 
                new_individual, new_individual1 = uniform_crossover(parent_1, parent_2)

            if(check(new_individual)):
                new_population.append(new_individual)            
            if(check(new_individual1)):
                new_population.append(new_individual1)

        new_population=np.array(new_population)
        population=np.concatenate((population,new_population),axis=0)

       
       
        #đột biến
        # for ii in range(int(init_size_population/10)):
        #     location=np.random.randint(0,total_task,size=1)
        #     value=np.random.randint(0,total_server,size=1)-1
        #     individual=np.random.randint(0,len(population),size=1)
        #     population[individual,location]=value
        # population=sorted(population,key=lambda x: fitness_function(x)[0])[0:init_size_population]
        # optimize_individual=copy.deepcopy(population[0])


        pmute=0.5
        for ii in range(int(init_size_population/10)):
            location1=np.random.randint(0,total_task,size=2)
            less=location1[0] if location1[0]<location1[1] else location1[1] 
            more =location1[1] if location1[0]<location1[1] else location1[0]
            for location in range(less,more):
                mutate_prob =np.random.random()
                if mutate_prob>pmute :
                    value=np.random.randint(0,total_server,size=1)-1
                    individual=np.random.randint(0,len(population),size=1)
                    population[individual,location]=value

        population=sorted(population,key=lambda x: fitness_function(x)[0])[0:init_size_population]
        optimize_individual=copy.deepcopy(population[0])

        
        
        
       

        #in kết quả mỗi vòng lặp
        if (i+1) % 1 !=0:
            sys.stdout.write("\033[F") #back to previous line
            sys.stdout.write("\033[K") #clear line
            a=str("["+"="*(i%1)+str(">")+"-"*(1-i%1)+"]:"+"time:"+str(fitness_function(optimize_individual)[1])+" cost: "+str(fitness_function(optimize_individual)[2])+" value:"+str(fitness_function(optimize_individual)[0]))
          #  print(a)

        #ghi nhận kết quả sau 10 vòng lặp
        else:
            KQ=str(i)+","+str(fitness_function(optimize_individual)[1])+","+str(fitness_function(optimize_individual)[2])+","+str(fitness_function(optimize_individual)[0])+"\n"
            files.write(KQ)
    files.close()

for number in range(0, 2):
    GA(100, 1000, 22, 100, 2, str(number))
    print(number)



