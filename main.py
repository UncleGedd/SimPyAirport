import random
import simpy
import numpy as np

ARRIVAL_RATE_LAMBDA = 5  # passengers per minute (lambda)

NUM_SERVERS = 2  # ID/boarding-pass queue servers
SERVICE_TIME = 0.75  # minutes per passenger at ID/boarding pass queue
averageServeTime = []

NUM_CHECKERS = 2  # personal-check queue checkers
MIN_SCAN_TIME = 0.5
MAX_SCAN_TIME = 1.0
averageCheckTime = []

SIM_RUN_TIME = 1440  # minutes to run the simulation
REPEATS = 100

averageTotalWaitTime = []
averageSystemTime = []


class ServerQueue(object):
    def __init__(self, env, numServers):
        self.env = env
        self.machine = simpy.Resource(env, numServers)

    def serve(self):
        yield self.env.timeout(SERVICE_TIME)


class CheckerQueue(object):
    def __init__(self, env, numCheckers):
        self.env = env
        self.machine = simpy.Resource(env, numCheckers)

    def check(self):
        checkerTime = random.uniform(MIN_SCAN_TIME, MAX_SCAN_TIME)
        yield self.env.timeout(checkerTime)


def passengerInBoardingPassIdQueue(env, name, serverQueue):
    # passenger arrives
    enterSystemTime = env.now
    print('%s arrives at the airport at %.2f.' % (name, enterSystemTime))

    # passenger enters ID/boarding-pass queue
    with serverQueue.machine.request() as requestForServer:
        startWaitingForServer = env.now
        yield requestForServer
        waitTimeForServer = env.now - startWaitingForServer
        averageServeTime.append(waitTimeForServer)

        print('%s enters the ID/boarding pass queue at %.2f.' % (name, env.now))
        yield env.process(serverQueue.serve())
        print('%s leaves the ID/boarding pass queue at %.2f.' % (name, env.now))

    return waitTimeForServer


def passengerInPersonalCheckQueue(env, name, checkerQueue):
    # passenger enter personal-check queue
    with checkerQueue.machine.request() as requestForChecker:
        startWaitingForChecker = env.now
        yield requestForChecker
        waitTimeForChecker = env.now - startWaitingForChecker
        averageCheckTime.append(waitTimeForChecker)

        print('%s enters the personal-check queue at %.2f.' % (name, env.now))
        yield env.process(checkerQueue.check())
        print('%s leaves the personal-check queue at %.2f.' % (name, env.now))

    return waitTimeForChecker


def startSimulation(env, numServers, numCheckers):
    # Create the queues
    serverQueue = ServerQueue(env, numServers)
    checkerQueue = CheckerQueue(env, numCheckers)

    # Create 5 initial passengers at time 0
    for i in range(5):
        env.process(passengerInBoardingPassIdQueue(env, 'Passenger %d' % i, serverQueue))
        env.process(passengerInPersonalCheckQueue(env, 'Passenger %d' % i, checkerQueue))

    # Create more passengers while the simulation is running
    arrivalNumber = 0
    while True:
        # time between successive arrivals (exponential distribution)
        yield env.timeout(np.random.exponential(ARRIVAL_RATE_LAMBDA))

        # arriving passengers
        for i in range(ARRIVAL_RATE_LAMBDA):
            arrivalNumber += 1
            env.process(passengerInBoardingPassIdQueue(env, 'Passenger %d' % arrivalNumber, serverQueue))
            env.process(passengerInPersonalCheckQueue(env, 'Passenger %d' % arrivalNumber, checkerQueue))


# Setup and start the simulation
random.seed(7)

env = simpy.Environment()
env.process(startSimulation(env, NUM_SERVERS, NUM_CHECKERS))

# Execute!
env.run(until=SIM_RUN_TIME)

print("\n")
print('avg wait in serve queue', np.mean(averageServeTime))
print('avg wait in check queue', np.mean(averageCheckTime))
# print('avg total wait time', np.mean(averageTotalWaitTime))
# print('avg time in system', np.mean(averageSystemTime))
