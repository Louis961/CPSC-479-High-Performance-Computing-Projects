# CPSC 479 Project 2
## Parallelizing Twitch API

#### Problem Summary

Our implementation of the data science project features two sections of parallelization and one section of data analysis. The main purpose of our project is to pull data from the Twitch API and analyze that data. First, we parallelize our HTTP GET requests to the Twitch API servers. This allows us to increase our request rate by N processes. This was needed because getting follow information required many extra GET requests which were very slow. Then, we implement parallel sorting with merge sort, once it has a nearly sorted list we conduct an insertion sort on process 0. Following that, we conduct some correlation data analysis using pandas and numpy. 

![image2](https://i.imgur.com/l4CTIu8.png)

![image](https://i.imgur.com/bua2J2W.png)

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

`mpiexec -n 8 python3 project2.py`

or

`mpirun -n 8 python3 project2.py`

-n can be set to the desired number of processes. Testing has been conducted with 8 processes. 

### Dependencies:

>A working MPI implentation (tested with MPICH)
>
>Python3 (+python3-dev & pip)
>
>MPI for Python (mpi4py)
>
>pandas
>
>NumPy

mpich:

`apt-get install mpich`

pip:

`apt-get install python3-pip`

python3-dev:

`apt-get install python3-dev`

mpi4py:

`python3 -m pip install mpi4py`

pandas:

`python3 -m pip install pandas`

numpy:

`python3 -m pip install numpy`

