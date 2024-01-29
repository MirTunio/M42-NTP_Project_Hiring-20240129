# M42 NTP_Project_Hiring 20240129
This is a small project to assess skills in various python libraries and system design. The idea here is to design a toy system to simulate two computers syncing their local time to each other. Synchronization of time is a deep problem in engineering and in science. Internet protocols, [GPS](https://en.wikipedia.org/wiki/Global_Positioning_System), Space exploration, Batch processing tasks, even Einstein's [Special Relativity](https://en.wikipedia.org/wiki/Einstein_synchronisation).

We are so accustomed to our phones and computers automatically syncing time, have you ever thought about how this works? In principle, your phone exchanges messages with a 'time server' and asks it what the time is. In practice, these messages may be delayed or changed by noise as they are exchanged. This introduces some complexities. The more accurately we need to synchronize two clocks, the more exponentially difficult the task becomes.

<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/en/5/5b/Untitled_Perfect_Lovers.jpg" />
</p>

You need to design a functioning toy system or simulation which demonstrates how to synchronize the clocks of a "slave" system to that of the "master" system. The slave and the master clock must be "connected" by a faulty transmission line which introduces noise and delays in a random manner. You must also devise a method to measure the effectiveness of the synchronisation algorithm you design.

Recall that noise means that bits sent from one end of the line may be flipped by the time they reach the other end of the line. And delay refers to latencies, or the amount of time the signal takes to reach from the input to the output.

In essence, your time sync algorithm must account for three distinct sources of asynchronicity:
1. The initial difference in time between master and slave
2. The delay of the transmission line
3. The potential errors in transmission

I want you to imagine that millions of dollars depend on how synchronized these two clocks are. Larger errors will lead to immense financial losses. And the more accurate the slave clock is, the more there is to gain.


 
### Skills Assessed:
* Understanding of project goals
* Code cleanliness and Commenting
* Knowledge of libraries / ability to learn new libraries
* Measurement of performance of systems

### Python Libraries Used:
You may use any modules to accomplish the task, however you must design the time syncing algorithm yourself, and you must use **zmq** for all communication between processes.

## Required Tasks:
* Create a 'master clock' server which maintains the current time. This will be used as a reference clock for all 'slave clocks'
* Create a 'transmission line' which will be used by master and slave to communicate. The line introduces random delays and errors into any data sent across it. 
* Create a 'slave clock' which will sync it's time with the master clock using your own time syncing algorithm
* Create a 'monitor' which shows the local time of the master and slave in realtime and to a resolution of 10 milliseconds, and an additional metric which quantifies the effectiveness of the time syncing algorithm.

## Usage:
The master clock is first turned on, it can get it's time from the local time of your system.
The transmission line is initiated
The slave clock is initialized to a random time
The slave clock uses this transmission line to get relevant time information and implements a syncing protocol to match it's local time as closely as possible to that of the master clock.
All three components can run on your local system.
All communication between these three systems must be done using zmq.

## Deliverable:
In the alloted time I expect you to furnish your first version of the above. At this stage I will recommend changes (if needed). Then I will review the final version and make an assessment. You may be as creative as you wish, and you may go above and beyod the required tasks if have the time.

### Resources:
* Clean Code: https://gist.github.com/wojteklu/73c6914cc446146b8b533c0988cf8d29
* Python Syle Guide (PEP 8): https://peps.python.org/pep-0008/
* NASA Guidlines (not entirely applicable but good to read): https://en.wikipedia.org/wiki/The_Power_of_10:_Rules_for_Developing_Safety-Critical_Code (number 2 and 5 are applicable, [see]("https://www.geeksforgeeks.org/python-assert-keyword/"))
* NTP guides: https://en.wikipedia.org/wiki/Network_Time_Protocol, 
* ZMQ guide: https://zguide.zeromq.org/
* An example of such a system is in the 'example' folder


_fin_
