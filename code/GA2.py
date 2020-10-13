import Config
import PreData
import numpy as np
import copy
#khoi tao ca the init individual
f=open("kq20_100_2.txt","w")
def kiemtradk(randd):
    a=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    isAccept=True
    h=0
    for i in randd :
        if(i>0):
            h=h+1
            a[i-1].append(h)
    m=-1
    
    for i in a:
        m=m+1
        time=0
        for k in i:
            time+=PreData.tasks[k-1].get_di()/(1000*Config.Rm)*8+PreData.tasks[k-1].get_res()/(1000*Config.Rm1)*8+PreData.tasks[k-1].get_wi()/(PreData.Mvns[m].get_frequency()*1000)
        if(m<20):
            if(time>PreData.Mvns[m].get_delta_time()):
                
                isAccept=False
    return isAccept
def tinhf(randd):
    cost=0
    time=0
    a=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    server=[]
    remote_Cloud=[]
    h=0
    for i in randd :
        h=h+1
        if(i==-1):
            server.append(h)
        elif(i==0):
            remote_Cloud.append(h)
        elif(i>0):
            
            a[i-1].append(h)
    m=-1
    
    for i in a:
        delta_Time=0
        m=m+1
        for k in i:
            cost+=Config.cost_rate*PreData.Mvns[m].get_rm()*PreData.tasks[k-1].get_di()/(1000*Config.Rm)*8
            cost+=Config.cost_MVN*PreData.tasks[k-1].get_wi()/1000
            
            time+=delta_Time+PreData.tasks[k-1].get_di()/(1000*Config.Rm)*8+PreData.tasks[k-1].get_res()/(1000*Config.Rm1)*8+PreData.tasks[k-1].get_wi()/(PreData.Mvns[m].get_frequency()*1000)
            delta_Time+=PreData.tasks[k-1].get_di()/(1000*Config.Rm)*8+PreData.tasks[k-1].get_res()/(1000*Config.Rm1)*8+PreData.tasks[k-1].get_wi()/(PreData.Mvns[m].get_frequency()*1000)
    tong1=0
    for i in server:
        tong1+=np.sqrt(Config.delta_t*PreData.tasks[i-1].get_wi())
    for i in server:
        time+=(1/1000)*PreData.tasks[i-1].get_wi()/(PreData.MECServer.get_frequency()*np.sqrt(Config.delta_t*PreData.tasks[i-1].get_wi())/tong1)
    tong2=0
    for i in remote_Cloud:
        tong2+=np.sqrt(Config.delta_t*PreData.tasks[i-1].get_wi())
        cost+=Config.cost_RC*PreData.tasks[i-1].get_wi()/1000
    for i in remote_Cloud:
        time+=(1/1000)*(PreData.tasks[i-1].get_di()+PreData.tasks[i-1].get_res())/Config.R0+(1/1000)*PreData.tasks[i-1].get_wi()/(PreData.MECServer.get_frequency()*np.sqrt(Config.delta_t*PreData.tasks[i-1].get_wi())/tong2)
    return Config.delta_t*time+Config.delta_c*cost
    
khoitao=[]
for i in range(10000):
    randd=np.random.randint(22,size=100)-1
    while (not kiemtradk(randd)):
        randd=np.random.randint(22,size=100)-1
    khoitao.append(randd)
mins=tinhf(khoitao[0])
toiuu=khoitao[0]
for i in khoitao:
    if(mins>tinhf(i)):
        mins=tinhf(i)
        toiuu=copy.deepcopy(i)
f.write(str(mins))
f.write(str(toiuu))
#lai ghep
for i in range(100):
    print("A")
    moi=[]
    for j in range(5000):
        size=np.random.randint(1,len(khoitao),size=2)
        m=khoitao[size[0]]
        n=khoitao[size[1]]
        diem=np.random.randint(3,99)
        diem1=np.random.randint(2,diem)
        h=np.concatenate((m[0:diem1+1],n[diem1+1:diem+1],m[diem+1:100]))
        h2=np.concatenate((n[0:diem1+1],m[diem1+1:diem+1],n[diem+1:100]))
        if(kiemtradk(h)):
            moi.append(h)
        if(kiemtradk(h2)):
            moi.append(h2)
    khoitao=np.array(khoitao)
    moi=np.array(moi)
    khoitao=np.concatenate((khoitao,moi),axis=0)
    m=len(khoitao)
 
    k=0
    for i in range(m):
        if(i>=len(khoitao)): break
        if(tinhf(khoitao[i])>mins+50):
            khoitao=np.delete(khoitao,i,axis=0)
    m=len(khoitao)
    for i in range(1000):
        vt=np.random.randint(0,100,size=1)
        gt=np.random.randint(0,22,size=1)-1
        cathe=np.random.randint(0,m,size=1)
        khoitao[cathe,vt]=gt
    for i in khoitao:
        if(mins>tinhf(i)):
            mins=tinhf(i)
            toiuu=copy.deepcopy(i)
    f.write(str(mins))
    f.write(str(toiuu))
zeros=np.zeros(100)
am=np.zeros(100)-1
f.write(str(tinhf(zeros)))
f.write(str(tinhf(am)))