import time

import numpy as np
from config import Config
from pandas import DataFrame


class Space(object):
    def __init__(self, n_particles, fitness_fn, w, c1, c2):
        self.n_particles = n_particles
        self.fitness_fn = fitness_fn
        self.w = w
        self.c1 = c1
        self.c2 = c2

        self.particles = []
        self.gbest_value = float('inf')
        self.gbest_evaluate = None
        self.gbest_position = None

    def evaluate_fitness(self):
        fitnesses = []
        for particle in self.particles:
            fitnesses.append(self.fitness_fn(particle))
        return np.array(fitnesses)

    def update_pbest_gbest(self):
        my_fitnesses = self.evaluate_fitness()  # (fitness, time, cost)
        fitnesses = my_fitnesses[:, 0]  # fitness

        # update pbest
        for idx, particle in enumerate(self.particles):
            fitness_candidate = fitnesses[idx]
            if fitness_candidate < particle.pbest_value:
                particle.pbest_value = fitness_candidate
                particle.pbest_position = particle.position

        # update gbest
        best_fitness_candidate_index = np.argmin(fitnesses)
        if fitnesses[best_fitness_candidate_index] < self.gbest_value:
            self.gbest_value = fitnesses[best_fitness_candidate_index]
            self.gbest_evaluate = my_fitnesses[best_fitness_candidate_index]
            self.gbest_position = self.particles[best_fitness_candidate_index].position

    def move_particles(self):
        for particle in self.particles:
            new_velocity = \
                self.w * particle.velocity \
                + self.c1 * np.random.uniform() * (particle.pbest_position - particle.position) \
                + self.c2 * np.random.uniform() * (self.gbest_position - particle.position)
            # TODO: if new position is invalid? -> velocity?

            new_velocity = (new_velocity - new_velocity.min()) / (new_velocity.max() - new_velocity.min()) \
                           * Config.V_MAX * 2 - Config.V_MAX
            particle.velocity = new_velocity
            particle.move()

    def jump(self):
        for particle in self.particles:
            particle.velocity = 20 * np.random.uniform(-1, 1) * particle.velocity
            particle.move()

    def search(self, n_iterations, n_jump=10, print_time=100):
        result = []
        iteration = 1
        history = []
        start_time = time.time()
        while iteration <= n_iterations:

            if time.time() - start_time >= print_time:
                print('iteration {}/{}: gbest_value = {}, time = {}, cost = {}'. \
                      format(iteration, n_iterations, self.gbest_value, self.gbest_evaluate[1], self.gbest_evaluate[2]))
                start_time = time.time()

            self.update_pbest_gbest()
            # print('iteration {}/{}: gbest_value = {}, time = {}, cost = {}'. \
            #       format(iteration, n_iterations, self.gbest_value, self.gbest_evaluate[1], self.gbest_evaluate[2]))
            self.move_particles()

            history.append(self.gbest_value)
            if iteration > n_jump:
                if history[-1] == history[-n_jump]:
                    self.jump()
            if iteration == 1 or iteration % 10 == 0:
                tmp_list = [iteration]
                tmp_list.extend(list(self.gbest_evaluate))
                result.append(tmp_list)
                # print(result)
            iteration += 1
        print('the best solution is: {}'.format(self.gbest_position))
        print('best_value: {}'.format(self.gbest_value))
        result = DataFrame(data=result, columns=['iteration', 'fitness', 'time', 'cost'])
        return result

