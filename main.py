import pygame
from sys import exit
from drone.swarm import Swarm
from greedy import Greedy
from grid.drawer import GridDrawer
from grid.generator import GridGenerator
from grid.grid import Grid
from drone.drone import Drone
from areas.areas import Areas
from logger import Logger
from cluster.cluster import Cluster
import matplotlib.pyplot as plt
from SeededRandom import SeededRandom
import datetime
import os
import json

IS_RENDER = False

ALGORITHM_NAME = os.getenv('ALGORITHM_NAME', 'Greedy') # 'Greedy' or 'EqualInterest' or 'EqualAreas' or 'Cluster'


DISTRIBUTION_TYPE = 'equal_interest' if ALGORITHM_NAME == 'EqualInterest' else 'equal_areas' # 'equal_interest' or 'equal_areas' 
IS_AREAS = ALGORITHM_NAME == 'EqualAreas' or ALGORITHM_NAME == 'EqualInterest' 
IS_CLUSTER = ALGORITHM_NAME == 'Cluster' 
IS_GREEDY = ALGORITHM_NAME == 'Greedy' 

IS_DRAW_AREAS = False

SCREEN_WIDTH = 1500 # 1500
SCREEN_HEIGHT = 900
CELL_SIZE = 5 # 5

SPEED = 5
GROWTH_RATE = 1

INTERVAL_MULTIPLIER = 5000
GRID_GENERATION_INTERVAL = 4 * INTERVAL_MULTIPLIER
DRONE_AMOUNT_CHANGE_INTERVAL = 1 * INTERVAL_MULTIPLIER
DRONE_PUSH_INTERVAL = 1 * INTERVAL_MULTIPLIER
DRONE_POP_TWICE_INTERVAL =  2 * INTERVAL_MULTIPLIER
DRONE_POP_INTERVAL = 3 * INTERVAL_MULTIPLIER

INIT_DRONES_AMOUNT = int(os.getenv('INIT_DRONES_AMOUNT', 4))

AMOUNT_OF_GRIDS = 5

iterations_amount = AMOUNT_OF_GRIDS * GRID_GENERATION_INTERVAL

meta_data = {
    'IS_RENDER': IS_RENDER,
    'ALGORITHM_NAME': ALGORITHM_NAME,
    'DISTRIBUTION_TYPE': DISTRIBUTION_TYPE,
    'IS_DRAW_AREAS': IS_DRAW_AREAS,
    'SCREEN_WIDTH': SCREEN_WIDTH,
    'SCREEN_HEIGHT': SCREEN_HEIGHT,
    'CELL_SIZE': CELL_SIZE,
    'SPEED': SPEED,
    'GROWTH_RATE': GROWTH_RATE,
    'INTERVAL_MULTIPLIER': INTERVAL_MULTIPLIER,
    'GRID_GENERATION_INTERVAL': GRID_GENERATION_INTERVAL,
    'DRONE_AMOUNT_CHANGE_INTERVAL': DRONE_AMOUNT_CHANGE_INTERVAL,
    'DRONE_PUSH_INTERVAL': DRONE_PUSH_INTERVAL,
    'INIT_DRONES_AMOUNT': INIT_DRONES_AMOUNT,
    'AMOUNT_OF_GRIDS': AMOUNT_OF_GRIDS
}

seed_str = str('14') + str(SCREEN_WIDTH) + str(SCREEN_HEIGHT) + str(CELL_SIZE) + str(SPEED) + str(int(GROWTH_RATE)) 
seed_str += str(GRID_GENERATION_INTERVAL) + str(DRONE_AMOUNT_CHANGE_INTERVAL) + str(DRONE_PUSH_INTERVAL)
seed = int(seed_str)

SeededRandom.set_initial_seed(seed)

print('Initializing the environment...')

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Runner')
clock = pygame.time.Clock()


print('Generating the grid...')
grid_generator = GridGenerator(SCREEN_WIDTH, SCREEN_HEIGHT)
grid = grid_generator.generate_grid(CELL_SIZE)
grid_drawer = GridDrawer(pygame, screen, draw_grid_lines=IS_RENDER and False)

print('Initializing the swarm...')
swarm = Swarm(pygame, screen, grid, SPEED, init_drones_amount=INIT_DRONES_AMOUNT, is_draw=IS_RENDER)

print('Initializing the logger...')
logger = Logger(pygame, screen, grid, is_log_on_screen=IS_RENDER)

print('Initializing the algorithms...')
greedy = Greedy(grid, swarm.drones)
cluster_algorithm = Cluster(grid, swarm.drones)
areas_algorithm = Areas(grid, swarm.drones, distribution_type=DISTRIBUTION_TYPE)

if (IS_AREAS):
    swarm.set_algorithm(areas_algorithm)

if (IS_CLUSTER):
    swarm.set_algorithm(cluster_algorithm)

if (IS_GREEDY):
    swarm.set_algorithm(greedy)


iterations = 0

print('Starting the simulation...')

amount_of_grids = 1


prev_drones_amount = len(swarm.drones)
while True:
    iterations += 1

    if (iterations % 1000 == 0):
        print('Progress: {:.2f}%'.format(iterations / iterations_amount * 100))

    if (iterations % GRID_GENERATION_INTERVAL == 0 and iterations != 0):
        if (amount_of_grids == AMOUNT_OF_GRIDS):
            break

        amount_of_grids += 1
        grid = grid_generator.generate_grid(CELL_SIZE)
        swarm.set_grid(grid)
        logger.set_grid(grid)

    # elif (iterations % DRONE_AMOUNT_CHANGE_INTERVAL == 0 and iterations != 0):
    #     if (iterations % DRONE_POP_TWICE_INTERVAL == 0):
    #         swarm.pop_drone()
    #         swarm.pop_drone()
    #     else:
    #         swarm.push_drone()

    #     print('Drones amount:', len(swarm.drones), 'Iteration:', iterations + 1)

    # if (len(swarm.drones) != prev_drones_amount):
    #     prev_drones_amount = len(swarm.drones)
    #     print('Drones amount:', len(swarm.drones), 'Iteration:', iterations + 1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # Screen background color
    screen.fill((0, 0, 0))

    if (IS_AREAS and IS_DRAW_AREAS and IS_RENDER):
        grid_drawer.draw_clusters(grid, areas_algorithm.areas_grid, len(swarm.drones))

    if (IS_CLUSTER and IS_DRAW_AREAS and IS_RENDER):
        grid_drawer.draw_clusters(grid, cluster_algorithm.clusters_grid, len(swarm.drones))

    # Grid logic 
    if (IS_RENDER):
        grid_drawer.draw(grid)
        
    grid.increase(GROWTH_RATE)

    # Update all swarm drones
    swarm.update()
    

    # Logger logic
    logger.log_grid_sum()
    logger.log_iteration(iterations)
    logger.log_is_even(len(grid.grid[0]))

    pygame.display.update()
    clock.tick(1000)


cells_sum_list = logger.cells_sum_list
grids_data = logger.grids_data

AlgorithmName = ALGORITHM_NAME

# Save the data to a file

print('Saving the data to a file...')
# Get date and time for file name

now = datetime.datetime.now()
date_time = now.strftime("%Y-%m-%d %H:%M:%S")

results_dir = './results/' + AlgorithmName + '/test4_' + f'dronesAmount={INIT_DRONES_AMOUNT};cellSize={CELL_SIZE};{date_time}' '/'
os.makedirs(results_dir, exist_ok=True)

# Define the file names
file_name1 = os.path.join(results_dir, f'interest.json')
file_name2 = os.path.join(results_dir, f'grids_data.json')
file_name3 = os.path.join(results_dir, f'meta_data.json')

with open(file_name1, 'w') as file:
    json.dump(cells_sum_list, file)

with open(file_name2, 'w') as file:
    json.dump(grids_data, file)

with open(file_name3, 'w') as file:
    json.dump(meta_data, file)

# Draw the graph

# flattened_cells_sum_list = [item for sublist in cells_sum_list for item in sublist]

# print('Plotting the graph...')
# plt.plot(flattened_cells_sum_list)
# plt.xlabel('Time Step')
# plt.ylabel('Cells Sum')
# plt.title('Cells Sum Over Time')
# plt.grid(True)
# plt.show()