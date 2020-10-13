import pickle
from Mvn import Mvn
from Server import Server
from Cloud_remote import Cloud_remote
import Config
from Task import Task
import pandas as pd
import random

''' khởi tạo các xe MVN (mobile volunteer node): random frequency của mỗi xe [0.5,0.8,1.0] #GHZ.
    khởi tạo các Task bao gồm: kích thước truyền đi, kích thước nhận về và kích thước tính toán.
    Di=[200,1000] #kb kích thước của dữ liệu request.
    [100,500] #KB. kích thước dữ liệu trả về.
    Wi = [200,1000] #M cycle kích thước khối lượng tính toán của mỗi task.
    @file task.txt và task.p là lưu trữ dữ liệu về 100 task:
    @file MVN.txt và MVN.p là lưu trữ dự liệu về các xe bus:
'''

csv=pd.read_csv("./data/data2.csv")
data=csv[csv.distance<=2000]
data_sort=data.sort_values(by=["bus_id","time"])

Mvns=[]
tasks=[]
pre_bus_id=912 
coordinates=[]
delta_time=""
start_time=""
end_time=0
dem=0

for index, row in data_sort.iterrows():
    if(dem==0):
        pre_bus_id=now_bus_id=row["bus_id"]
        start_time=end_time=row["time"]
        dem=dem+1

    pre_bus_id=now_bus_id
    now_bus_id=row["bus_id"]
    if(pre_bus_id==now_bus_id):
        toado=[]
        toado.append(row["x_coordinate"])
        toado.append(row["y_coordinate "])
        coordinates.append(toado)
        end_time=row["time"]
    else:
        st=start_time.split(":")
        et=end_time.split(":")
        delta_time=(int(et[2])-int(st[2]))*60+int(et[3])-int(st[3])
        frequency=random.choice(Config.F_MVN) #random tần số cho mỗi xe
        Mvns.append(Mvn(pre_bus_id,frequency,coordinates,delta_time)) 
        start_time=row["time"]
        coordinates=[]

#loại bỏ đi các xe đáp ứng không tốt

Mvns.remove(Mvns[7])
Mvns.remove(Mvns[12])
Mvns.remove(Mvns[14])
Mvns.remove(Mvns[16])
Mvns.remove(Mvns[12])
Mvns.remove(Mvns[24])
Mvns.remove(Mvns[0])
Mvns.remove(Mvns[0])
Mvns.remove(Mvns[0])
Mvns.remove(Mvns[9])
Mvns.remove(Mvns[10])
Mvns.remove(Mvns[12])
Mvns.remove(Mvns[6])

hh=0

#thiết lập các thông số cho mỗi MVN

for i in Mvns:
    i.set_rm()
    i.get_rm()
    hh=hh+1
    i.set_id(hh)

#tạo MecServer 
MECServer=Server(Config.F_MEC)

#khoi tao remote Cloud
remoteCloud=Cloud_remote(Config.F_RM,Config.R0)

for i in range(500):
    tasks.append(Task(random.randint(Config.Di[0],Config.Di[1]),random.randint(Config.Wi[0],Config.Wi[1]),0))

with open("./data/task2.p","wb") as task:
    pickle.dump(tasks,task)
with open("./data/fog_device1.p","wb") as mvn:
    pickle.dump((Mvns[:10],MECServer,remoteCloud),mvn)


