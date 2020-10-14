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
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor

class GA:
    def __init__(self,init_size_population,number_loop,total_server,total_task,cut_points,running_loop):
        self.init_size_population = init_size_population
        self.number_loop = number_loop
        self.total_server = total_server
        self.total_task = total_task
        self.cut_points = cut_points
        self.running_loop=running_loop
        with open("./data/fog_device.p","rb") as fog:
            self.mvns,self.mecServer,self.remoteCloud=pickle.load(fog)
        with open("./data/task.p","rb") as data:
            self.tasks=pickle.load(data)
        self.population=[]
        self.files=open("./result/tlm_1_100_1000_13_10.csv","w")
        self.optimize_value=None
        self.optimize_individual=None
        self.new_population=None
    def tournament(self,population):
        a=np.random.randint(len(population),size=5)
        a=np.array(population)[a]
        minp=min(a,key=lambda x:self.fitness_function(x)[0])    
        return minp


    def queue_of_task(self,index_task,index):
        for i in range(len(index_task)-1):
            for j in range(1,len(index_task)):
                if self.tasks[index_task[i]].get_di()/(1000*Config.Rm)*8+self.tasks[index_task[i]].get_res()/(1000*Config.Rm1)*8+self.tasks[index_task[i]].get_wi()/(self.mvns[index].get_frequency()*1000)\
                    >self.tasks[index_task[j]].get_di()/(1000*Config.Rm)*8+self.tasks[index_task[j]].get_res()/(1000*Config.Rm1)*8+self.tasks[index_task[j]].get_wi()/(self.mvns[index].get_frequency()*1000):
                    middlemen_task=index_task[i]
                    index_task[i]=index_task[i+1]
                    index_task[i+1]=middlemen_task
        return index_task
    def initialization(self):        
        initialization=[]
        for i in range(self.init_size_population):
            individual=np.random.randint(self.total_server,size=self.total_task)-1
            while (not self.check(individual)):
                individual=np.random.randint(self.total_server,size=self.total_task)-1
            initialization.append(individual)
        self.optimize_value=self.fitness_function(initialization[0])[0]
        self.optimize_individual=initialization[0]
        for individual in initialization:
            if(self.optimize_value>self.fitness_function(individual)[0]):
                self.optimize_value=self.fitness_function(individual)[0]
                self.optimize_individual=copy.deepcopy(individual)

        self.population=initialization
    def Crossover(self,J):
        #lai ghép điểm cắt
        if self.cut_points==1:
            #index=np.random.randint(1,len(initialization),size=2)
            first_individual=self.tournament(self.population)
            second_individual=self.tournament(self.population)
            point=np.random.randint(2,self.total_task-1)
            new_individual=np.concatenate((first_individual[0:point+1],second_individual[point+1:self.total_task]))
            new_individual1=np.concatenate((second_individual[0:point+1],first_individual[point+1:self.total_task]))

        #lai ghép điểm cắt
        else:
            #index=np.random.randint(1,len(population),size=2)
            m=self.tournament(self.population)
            n=self.tournament(self.population)
            point=np.random.randint(3,99)
            point1=np.random.randint(2,point)
            new_individual=np.concatenate((m[0:point1+1],n[point1+1:point+1],m[point+1:100]))
            new_individual1=np.concatenate((n[0:point1+1],m[point1+1:point+1],n[point+1:100]))
        if(self.check(new_individual)):
            self.new_population.append(new_individual)
        if(self.check(new_individual1)):
            self.new_population.append(new_individual1)
        #return new_population
    def Mutation(self,J):
        location=np.random.randint(0,self.total_task,size=1)
        value=np.random.randint(0,self.total_server,size=1)-1
        self.population=np.array(self.population)
        individual=np.random.randint(0,len(self.population),size=1)
        self.population[individual,location]=value
    def check(self,individual):
        mvn_s=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        isAccept=True

        for index,node in enumerate(individual):
            if(node>0):
                mvn_s[node-1].append(index)
    
        for index,mvn in enumerate(mvn_s):
            time=0
            for id_of_task in mvn:
                time+=self.tasks[id_of_task].get_di()/(1000*Config.Rm)*8+self.tasks[id_of_task].get_res()/(1000*Config.Rm1)*8+self.tasks[id_of_task].get_wi()/(self.mvns[index].get_frequency()*1000)
            if(time>self.mvns[index].get_delta_time()):    
                isAccept=False
        return isAccept

    '''
    tính giá trị hàm fitness của bài toán
    @parameter:individual là một một cá thể trong quần thể
    '''

    def fitness_function(self,individual):
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
            tasks_mvn=self.queue_of_task(tasks_mvn,index)
            for task in tasks_mvn:
                cost+=Config.cost_MVN*self.tasks[task].get_wi()/1000
                time+=delta_Time+self.tasks[task].get_di()/(1000*Config.Rm)*8+self.tasks[task].get_res()/(1000*Config.Rm1)*8+self.tasks[task].get_wi()/(self.mvns[index].get_frequency()*1000)
                delta_Time+=self.tasks[task].get_di()/(1000*Config.Rm)*8+self.tasks[task].get_res()/(1000*Config.Rm1)*8+self.tasks[task].get_wi()/(self.mvns[index].get_frequency()*1000)
        """sử dụng giải thuậ kkt dễ dàng chứng minh được:
            chia tài nguyên hợp lí mecServer.get_frequency()*np.sqrt(Config.delta_t*tasks[i-1].get_wi())/sum;
            sum bằng tổng của các căn bậc 2 của wi i là id của các mvns
        """
        sum1=0
        for i in server:
            sum1+=np.sqrt(Config.delta_t*self.tasks[i-1].get_wi())
        for i in server:
            time+=(1/1000)*self.tasks[i-1].get_wi()/(self.mecServer.get_frequency()*np.sqrt(Config.delta_t*self.tasks[i-1].get_wi())/sum1)
        sum2=0
        for i in remote_Cloud:
            sum2+=np.sqrt(Config.delta_t*self.tasks[i-1].get_wi())
            cost+=Config.cost_RC*self.tasks[i-1].get_wi()/1000
        for i in remote_Cloud:
            time+=(1/1000)*(self.tasks[i-1].get_di()+self.tasks[i-1].get_res())/Config.R0+(1/1000)*self.tasks[i-1].get_wi()/(self.remoteCloud.get_frequency()*np.sqrt(Config.delta_t*self.tasks[i-1].get_wi())/sum2)
        return Config.delta_t*time+Config.delta_c*cost,time,cost,number_task_on_cloud,number_task_on_server,number_task_on_mvn
    """
    Sử dụng thuật toán GA cho bài toán.
    @para init_size_population:số lượng cá thể khởi tạo cho quần thể ban đầu
    @para number_loop: số vòng lặp để tìm giá trị tối ưu
    @para cut_poins: số điểm cắt khi lai ghép
    """


    def active_GA(self,I):
        aaa=list()
        self.initialization()
        opt=None
        for i in range(self.number_loop):
            self.new_population=[]
            for kk in range(int(self.init_size_population/2)):
                self.Crossover(1)
            for j in range(int(self.init_size_population/10)):
                self.Mutation(1)
            self.new_population=np.array(self.new_population)
            self.population=np.concatenate((self.population,self.new_population),axis=0)
            self.population=sorted(self.population,key=lambda x: self.fitness_function(x)[0])[0:self.init_size_population]
            self.optimize_individual=copy.deepcopy(self.population[0])
            self.optimize_value=self.fitness_function(self.optimize_individual)[0]
            opt=self.fitness_function(self.optimize_individual)
            aaa.append([opt[1],opt[2],opt[0]])
            print(opt[0])
        self.files.write("cloud,"+str(opt[3])+"\n")
        self.files.write("server,"+str(opt[4])+"\n")
        self.files.write("mvn,"+str(opt[5])+"\n")


        for iii in range(3):
            if iii%3==0:
                self.files.write("time,")
            if iii%3==1:
                self.files.write("coss,")
            if iii%3==2:
                self.files.write("fitness,")
            for kkk in aaa:
                self.files.write(str(kkk[iii])+",")
            self.files.write("\n")
    def run_GA(self):
        #with ProcessPoolExecutor() as executor:
        for i in range(self.running_loop):
            self.active_GA(1)
        self.files.close()
FUZZY=GA(100,1000,22,100,1,20)
FUZZY.run_GA()