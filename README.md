# Memory-Allocation-By-Segmentation
# Inputs :
1- User inputs total memory size 
2- User inputs holes starting address and size. 
3- User inputs Processes one by one. 
4- User inputs for each process 
a. Number of segments 
b. Name and size of each segment 
(Example: P1 : 3 segments ... Code: 50 , Data: 200, Stack:100) 
5- User inputs the method of allocation (first fit or best fit). 
# Scenario to be done:
1- Allocate segments using allocation methodology. 
2- If one segment or more of a process can not fit in any hole you should generate a message to 
state that this process does not fit. 
3- De-Allocate a process ( The user chooses a process to de-allocate, you should deallocate all 
segments of this process and consider their spaces holes to be used later and add to them to 
any neighboring holes) 
4- Initial between holes spaces are considered old processes and user can choose to deallocate one 
of these old processes
