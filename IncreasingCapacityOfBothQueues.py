import random
import simpy
import matplotlib.pyplot as plt
import numpy as np

random.seed(7)

# Grand totals hold the results at each
# iteration of the for loop
GRAND_TOTAL_SERVER_TIME = []
GRAND_TOTAL_CHECKER_TIME = []
GRAND_TOTAL_WAIT_TIME = []
GRAND_TOTAL_SYSTEM_TIME = []

for capacity in range(1, 5):
    arrivalRateLambda = 50  # passengers per minute (lambda)

    numServers = capacity  # ID/boarding-pass queue servers
    serviceTime = 0.75  # minutes per passenger at ID/boarding pass queue

    numCheckers = capacity  # personal-check queue checkers
    minScanTime = 0.5
    maxScanTime = 1.0

    simRunTime = 3000  # minutes to run the simulation

    averageCheckTime = []
    averageServeTime = []
    averageTotalWaitTime = []
    averageSystemTime = []

    class Airport(object):
        def __init__(self, env):
            self.env = env
            self.serverQueue = simpy.Resource(env, capacity=numServers)
            self.checkQueue = simpy.Resource(env, capacity=numCheckers)

        def serve(self):  # boarding-pass/id check
            yield self.env.timeout(serviceTime)

        def check(self):  # personal check
            checkerTime = random.uniform(minScanTime, maxScanTime)
            yield self.env.timeout(checkerTime)


    def passenger(env, name, airport):
        # passenger arrives
        enterSystemTime = env.now

        # passenger enters ID/boarding-pass queue
        with airport.serverQueue.request() as requestForServer:
            startWaitingForServer = env.now
            yield requestForServer
            waitTimeForServer = env.now - startWaitingForServer
            averageServeTime.append(waitTimeForServer)

            yield env.process(airport.serve())

        # passenger enters personal-check queue
        with airport.checkQueue.request() as requestForChecker:
            startWaitingForChecker = env.now
            yield requestForChecker
            waitTimeForChecker = env.now - startWaitingForChecker
            averageCheckTime.append(waitTimeForChecker)

            yield env.process(airport.check())

        averageTotalWaitTime.append(waitTimeForServer + waitTimeForChecker)
        averageSystemTime.append(env.now - enterSystemTime)


    def startSimulation(env):
        airport = Airport(env)

        # Create initial passengers at time 0.0
        for i in range(arrivalRateLambda):
            env.process(passenger(env, 'Passenger %d' % i, airport))

        # Create more passengers while the simulation is running
        arrivalNumber = arrivalRateLambda - 1
        while True:
            # time between successive arrivals (exponential distribution)
            yield env.timeout(np.random.exponential(arrivalRateLambda))

            # arriving passengers
            for i in range(arrivalRateLambda):
                arrivalNumber += 1
                env.process(passenger(env, 'Passenger %d' % arrivalNumber, airport))


    # Setup and start the simulation
    env = simpy.Environment()
    env.process(startSimulation(env))

    env.run(until=simRunTime)

    print("\n")
    print('Number of Servers in id/boarding-pass queue:', numServers)
    print('Number of Checkers in personal-check queue:', numCheckers)
    print('Avg wait in serve queue:', np.mean(averageServeTime))
    print('Avg wait in check queue:', np.mean(averageCheckTime))
    print('Avg total wait time:', np.mean(averageTotalWaitTime))
    print('Avg time in system:', np.mean(averageSystemTime))

    GRAND_TOTAL_WAIT_TIME.append(np.mean(averageTotalWaitTime))
    GRAND_TOTAL_CHECKER_TIME.append(np.mean(averageCheckTime))
    GRAND_TOTAL_SERVER_TIME.append(np.mean(averageServeTime))
    GRAND_TOTAL_SYSTEM_TIME.append(np.mean(averageSystemTime))


# Plot the results
plt.plot(range(1, 5), GRAND_TOTAL_SERVER_TIME)
plt.plot(range(1, 5), GRAND_TOTAL_CHECKER_TIME)
plt.plot(range(1, 5), GRAND_TOTAL_WAIT_TIME)
plt.plot(range(1, 5), GRAND_TOTAL_SYSTEM_TIME)
plt.xticks([1, 2, 3, 4])
plt.xlabel("Capacity of Queues")
plt.ylabel("Total Wait Time")
plt.title("Effects of Increasing Capacity at Both Queues")
plt.legend(['Server Wait',
            'Checker Wait',
            'Total Wait',
            'Time in System'],
           loc='upper right')
plt.show()

