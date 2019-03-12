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

for numCheckers in range(1, 5):
    random.seed(7)
    ARRIVAL_RATE_LAMBDA = 50  # passengers per minute (lambda)

    NUM_SERVERS = 1  # ID/boarding-pass queue servers
    SERVICE_TIME = 0.75  # minutes per passenger at ID/boarding pass queue
    averageServeTime = []

    NUM_CHECKERS = numCheckers  # personal-check queue checkers
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
    env = simpy.Environment()
    env.process(startSimulation(env))

    env.run(until=SIM_RUN_TIME)

    print("\n")
    print('Number of Servers in id/boarding-pass queue:', NUM_SERVERS)
    print('Number of Checkers in personal-check queue:', NUM_CHECKERS)
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
plt.xlabel("Number of Checkers")
plt.ylabel("Total Wait Time")
plt.title("Effects of Increasing Checkers on Wait Times")
plt.legend(['Server Wait',
            'Checker Wait',
            'Total Wait',
            'Time in System'],
           loc='upper right')
plt.show()

