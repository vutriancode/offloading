import numpy as np


class Particle(object):
    def __init__(self, is_valid, n_nodes, n_tasks, v_max):
        rand_solution = np.random.randint(0, n_nodes, n_tasks)
        self.position = np.zeros((n_nodes, n_tasks))
        for idx_task, idx_node in enumerate(rand_solution):
            self.position[idx_node, idx_task] = 1
        self.is_valid = is_valid

        self.pbest_position = self.position
        self.pbest_value = float('inf')
        self.velocity = np.random.uniform(-v_max, v_max, (n_nodes, n_tasks))

    def move(self):
        temp_position = self.position + self.velocity
        new_position = np.zeros_like(self.position)
        for idx_task, idx_node in enumerate(temp_position.argmax(axis=0)):
            new_position[idx_node, idx_task] = 1
        if self.is_valid(new_position):
            # print('duc nguyen test new position')
            self.position = new_position
        # else:
            # print('duc nguyen not valid ----------------- ')

