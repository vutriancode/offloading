import pickle
import numpy as np
from particle import Particle
from space import Space
from config import Config


# N_DIMENSIONALS = 50
#
#
# def fitness_fn(particle):
#     return sum(particle.position ** 2)
#
#
# class Particle(object):
#     def __init__(self):
#         self.position = np.random.uniform(-200.0, 200.0, N_DIMENSIONALS)
#         self.pbest_position = self.position
#         self.pbest_value = float('inf')
#         self.velocity = np.random.uniform(-20, 20, N_DIMENSIONALS)
#
#     def __str__(self):
#         print(f'current position {self.position}, pbest position {self.pbest_position}')
#
#     def move(self):
#         self.position = self.position + self.velocity
#

def queue_of_task(index_task, index):
    for i in range(len(index_task) - 1):
        for j in range(1, len(index_task)):
            if tasks[index_task[i]].get_di() / (1000 * Config.Rm) * 8 + tasks[index_task[i]].get_res() / (
                    1000 * Config.Rm1) * 8 + tasks[index_task[i]].get_wi() / (mvns[index].get_frequency() * 1000) \
                    > tasks[index_task[j]].get_di() / (1000 * Config.Rm) * 8 + tasks[index_task[j]].get_res() / (
                    1000 * Config.Rm1) * 8 + tasks[index_task[j]].get_wi() / (mvns[index].get_frequency() * 1000):
                middlemen_task = index_task[i]
                index_task[i] = index_task[i + 1]
                index_task[i + 1] = middlemen_task
    return index_task


# mở dữ liệu khởi tạo các thiết bị tính toán(20 mvns,1 mecserver,1 remotecloud) và tập các công việc (100 task)
with open("./data/fog_device.p", "rb") as fog:
    mvns, mecServer, remoteCloud = pickle.load(fog)
with open("./data/task.p", "rb") as data:
    tasks = pickle.load(data)


def check(individual):
    individual = individual.argmax(axis=0) - 1
    mvn_s = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    isAccept = True

    for index, node in enumerate(individual):
        if node > 0:
            mvn_s[node - 1].append(index)

    for index, mvn in enumerate(mvn_s):
        time = 0
        for id_of_task in mvn:
            time += tasks[id_of_task].get_di() / (1000 * Config.Rm) * 8 + tasks[id_of_task].get_res() / (
                    1000 * Config.Rm1) * 8 + tasks[id_of_task].get_wi() / (mvns[index].get_frequency() * 1000)
        if time > mvns[index].get_delta_time():
            isAccept = False
    return isAccept


def fitness_function(particle):
    individual = particle.position
    individual = individual.argmax(axis=0) - 1
    cost = 0
    time = 0
    mvn_s = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    server = []
    remote_Cloud = []
    for index, node in enumerate(individual):
        if node == -1:
            server.append(index)
        elif node == 0:
            remote_Cloud.append(index)
        elif node > 0:
            # print('duc nguyen test -----{}'.format(node))
            mvn_s[node - 1].append(index)
    for index, tasks_mvn in enumerate(mvn_s):
        delta_Time = 0
        '''
            như đã chứng minh thì hàng đợi tối ưu về thời gian tính toán 
            khi các công việc nào có kích thước wi bé sẽ được xử lí trước.
            sắp xếp các công việc theo thứ tự tăng của khối lượng công việc cần tính toán.
        '''
        tasks_mvn = queue_of_task(tasks_mvn, index)
        for task in tasks_mvn:
            cost += Config.cost_rate * abs(mvns[index].get_rm()) * tasks[task].get_di() / (1000 * Config.Rm) * 8
            cost += Config.cost_MVN * tasks[task].get_wi() / 1000
            time += delta_Time + tasks[task].get_di() / (1000 * Config.Rm) * 8 + tasks[task].get_res() / (
                    1000 * Config.Rm1) * 8 + tasks[task].get_wi() / (mvns[index].get_frequency() * 1000)
            delta_Time += tasks[task].get_di() / (1000 * Config.Rm) * 8 + tasks[task].get_res() / (
                    1000 * Config.Rm1) * 8 + tasks[task].get_wi() / (mvns[index].get_frequency() * 1000)
    """sử dụng giải thuậ kkt dễ dàng chứng minh được:
        chia tài nguyên hợp lí mecServer.get_frequency()*np.sqrt(Config.delta_t*tasks[i-1].get_wi())/sum;
        sum bằng tổng của các căn bậc 2 của wi i là id của các mvns
    """
    sum1 = 0
    for i in server:
        sum1 += np.sqrt(Config.delta_t * tasks[i - 1].get_wi())
    for i in server:
        time += (1 / 1000) * tasks[i - 1].get_wi() / (
                mecServer.get_frequency() * np.sqrt(Config.delta_t * tasks[i - 1].get_wi()) / sum1)
    sum2 = 0
    for i in remote_Cloud:
        sum2 += np.sqrt(Config.delta_t * tasks[i - 1].get_wi())
        cost += Config.cost_RC * tasks[i - 1].get_wi() / 1000
    for i in remote_Cloud:
        time += (1 / 1000) * (tasks[i - 1].get_di() + tasks[i - 1].get_res()) / Config.R0 + (1 / 1000) * tasks[
            i - 1].get_wi() / (remoteCloud.get_frequency() * np.sqrt(Config.delta_t * tasks[i - 1].get_wi()) / sum2)
    return Config.delta_t * time + Config.delta_c * cost, time, cost


def my_fitness_fn(particle):
    return fitness_function(particle)[0]


# def my_check(individual):
#     return True


if __name__ == '__main__':
    search_space = Space(Config.N_PARTICLES, fitness_function, Config.W, Config.C1, Config.C2)
    particles = [Particle(check, Config.N_NODES, Config.N_TASKS, Config.V_MAX) for _ in range(search_space.n_particles)]
    search_space.particles = particles
    result = search_space.search(Config.N_ITERATIONS)
    result.to_csv('./result/PSO_improve_1.csv', index=False)


