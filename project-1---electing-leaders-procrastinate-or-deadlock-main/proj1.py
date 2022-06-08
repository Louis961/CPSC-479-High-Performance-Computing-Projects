# Anthony Galustyan
# Louis Zuckerman
# CPSC 479-01
# Project 1

# Two Leader Election Problem implemented concurrently

from mpi4py import MPI
import random
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# random seed
random.seed(time.time() + rank * 999999)
# instead of taking a few steps to find the abs value and adding 10 (for numbers < 10) 
# or taking % 100 (for numbers greater than 100) we used Python's built in random.rantint() method
# all processes generate a random number [10, 100]
# concatenates '1' to the start and the process rank to the end
num = random.randint(10, 100)
num = int(str(1) + str(num) + str(rank))
odd = 0
even = 0

# determine the starting rank 0 if it is even or odd then sends num to rank 1
# process 0 should never generate an odd number because '0' is concatenated to the end
if rank == 0:
    if num % 2 == 0:
        odd = 1
        even = num
    else:
        odd = num
        even = 1

    # process 0 sends even/odd numbers to process 1
    comm.send(even, dest=1, tag=2)
    comm.send(odd, dest=1, tag=3)

# tag used to categorize if recieved data is even or odd, then determines if the received num is greater than
# the previous num stored in even or odd
if rank > 0:
    odd = comm.recv(source=rank-1, tag=3)
    even = comm.recv(source=rank-1, tag=2)

    if (num % 2 == 0):
        # compare to even
        if num > even:
            even = num
    else:
        # compare to odd
        if num > odd:
            odd = num

# sends new odd and even nums to the next rank
# (rank + 1) % size ensures that it's sent back to process 0 after finishing
if rank > 0:
    comm.send(even, dest=((rank+1)%size), tag=2)
    comm.send(odd, dest=((rank+1)%size), tag=3)

# when the ranks come around again the highest even and odd will be receievd and printed to terminal
if rank == 0:
    even = comm.recv(source=size-1, tag=2)
    odd = comm.recv(source=size-1, tag=3)
    print(f"The odd leader (president) is {odd} and the even leader (vice president) is {even}")
