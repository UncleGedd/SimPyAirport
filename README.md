# SimPyAirport
Simulate a boarding pass queue followed by a security queue using SimPy. Uses Poisson and Exponential distributions to model arriving passengers

Passengers arrive at the airport and enter boarding pass queue with a mean service time of 0.75 / minute. After the boarding pass queue, the passengers enter the personal check queue which has a variable service time that follows a uniform distribution between 0.5 and 1.0.

The files in this repo correspond to several experiments that vary the lambda parameter of the Poisson/Exponential distributions, as well as, the capacity of each resource.
