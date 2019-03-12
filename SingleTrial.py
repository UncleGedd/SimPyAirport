import random
import simpy
import numpy as np

ARRIVAL_RATE_LAMBDA = 50  # passengers per minute (lambda)

NUM_SERVERS = 3  # ID/boarding-pass queue servers
SERVICE_TIME = 0.75  # minutes per passenger at ID/boarding pass queue
averageServeTime = []

NUM_CHECKERS = 2  # personal-check queue checkers
MIN_SCAN_TIME = 0.5
MAX_SCAN_TIME = 1.0
averageCheckTime = []

SIM_RUN_TIME = 3000  # minutes to run the simulation

averageTotalWaitTime = []
averageSystemTime = []


class Airport(object):
    def __init__(self, env):
        self.env = env
        self.serverQueue = simpy.Resource(env, capacity=NUM_SERVERS)
        self.checkQueue = simpy.Resource(env, capacity=NUM_CHECKERS)

    def serve(self):  # boarding-pass/id check
        yield self.env.timeout(SERVICE_TIME)

    def check(self):  # personal check
        checkerTime = random.uniform(MIN_SCAN_TIME, MAX_SCAN_TIME)
        yield self.env.timeout(checkerTime)


def passenger(env, name, airport):
    # passenger arrives
    enterSystemTime = env.now
    print('%s arrives at the airport at %.2f.' % (name, enterSystemTime))

    # passenger enters ID/boarding-pass queue
    with airport.serverQueue.request() as requestForServer:
        startWaitingForServer = env.now
        yield requestForServer
        waitTimeForServer = env.now - startWaitingForServer
        averageServeTime.append(waitTimeForServer)

        print('%s enters the ID/boarding pass queue at %.2f.' % (name, env.now))
        yield env.process(airport.serve())
        print('%s leaves the ID/boarding pass queue at %.2f.' % (name, env.now))

    # passenger enters personal-check queue
    with airport.checkQueue.request() as requestForChecker:
        startWaitingForChecker = env.now
        yield requestForChecker
        waitTimeForChecker = env.now - startWaitingForChecker
        averageCheckTime.append(waitTimeForChecker)

        print('%s enters the personal-check queue at %.2f.' % (name, env.now))
        yield env.process(airport.check())
        print('%s leaves the personal-check queue at %.2f.' % (name, env.now))

    averageTotalWaitTime.append(waitTimeForServer + waitTimeForChecker)
    averageSystemTime.append(env.now - enterSystemTime)


def startSimulation(env):
    airport = Airport(env)

    # Create initial passengers at time 0.0
    for i in range(ARRIVAL_RATE_LAMBDA):
        env.process(passenger(env, 'Passenger %d' % i, airport))

    # Create more passengers while the simulation is running
    arrivalNumber = ARRIVAL_RATE_LAMBDA - 1
    while True:
        # time between successive arrivals (exponential distribution)
        yield env.timeout(np.random.exponential(ARRIVAL_RATE_LAMBDA))

        # arriving passengers
        for i in range(ARRIVAL_RATE_LAMBDA):
            arrivalNumber += 1
            env.process(passenger(env, 'Passenger %d' % arrivalNumber, airport))


# Setup and start the simulation
random.seed(7)
env = simpy.Environment()
env.process(startSimulation(env))

env.run(until=SIM_RUN_TIME)

print("\n")
print('avg wait in serve queue', np.mean(averageServeTime))
print('avg wait in check queue', np.mean(averageCheckTime))
print('avg total wait time', np.mean(averageTotalWaitTime))
print('avg time in system', np.mean(averageSystemTime))
