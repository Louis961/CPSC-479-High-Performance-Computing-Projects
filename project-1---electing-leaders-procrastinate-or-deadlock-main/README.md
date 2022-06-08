# CPSC 479 Project 1
## Electing Leaders in a Ring Topology

#### Problem Summary

Our algorithm selects two leaders, which we can call them as the president and the vice-president. The president will be the largest odd value and the vice president will be the largest even value. The two elections can run concurrently (by sending/receiving two values in the same MPI send) or separately (sending one message for president-odd value and another message for vice-president-even value).

The two leader election algorithm has been implemented **concurrently**

## Group members:
>Anthony Galustyan
>
>*agalustyan@csu.fullerton.edu*
>
>
>Louis Zuckerman
>
>*louiszman@csu.fullerton.edu*

## How to use

### Run

`mpiexec -n 8 python3 proj1.py`

or

`mpirun -n 8 python3 proj1.py`

-n can be set to the desired number of processes. 

### Dependencies:

**A Dockerfile with all required dependencies has been provided in the `.devcontainer` folder**

>A working MPI implentation (tested with MPICH)
>
>Python3 (+python3-dev & pip)
>
>MPI for Python (mpi4py)

mpich:

`apt-get install mpich`

pip:

`apt-get install python3-pip`

python3-dev:

`apt-get install python3-dev`

mpi4py:

`python3 -m pip install mpi4py`

