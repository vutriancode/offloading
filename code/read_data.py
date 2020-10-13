import Server,Mvn,Cloud_remote,pickle
'''with open("C:\\Users\\vutri\\OneDrive\\Desktop\\Offloading\\data\\fog_device.p","rb") as a:
    m,n,p=pickle.load(a)
print("MVN:\n")
for i in m:
    print("f="+str(i.get_frequency())+"_____"+"nang luong: "+str(i.get_rm())+"---time:"+str(i.get_delta_time()))
print("MVN:\n")
for i in m:
    print("f="+str(i.get_frequency())+"_____"+"nang luong: "+str(i.get_rm())+"---time:"+str(i.get_delta_time()))'''
with open("C:\\Users\\vutri\\OneDrive\\Desktop\\Offloading\\data\\task2.p","rb") as a:
    tasks =pickle.load(a)
print("Task:\n")
with open("C:\\Users\\vutri\\OneDrive\\Desktop\\Offloading\\data\\task2.csv","w") as a:
    a.write("di,wi,data_response\n")
    for task in tasks:
        a.write(str(task.get_di())+","+str(task.get_wi())+","+str(task.get_res())+"\n")
'''
with open("C:\\Users\\vutri\\OneDrive\\Desktop\\Offloading\\data\\mvns.csv","w") as a:
    a.write("f,nang luong ,time\n")
    for i in m:
        a.write(str(i.get_frequency())+","+str(i.get_rm())+","+str(i.get_delta_time())+"\n")'''