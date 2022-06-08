# Anthony Galustyan
# Louis Zuckerman
# CPSC 479-01
# Project 2

from mpi4py import MPI
import random
import datetime
from datetime import timezone
import requests
import os
import json
import dateutil.parser
import time
import re
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from dotenv import load_dotenv

load_dotenv()

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# what we sort our data by
sort_category = 'uptime_hours'

def mergeSort(arr):
    if len(arr) > 1:
        mid = len(arr)//2
 
        left = arr[:mid]
        right = arr[mid:]
 
        mergeSort(left)
        mergeSort(right)
 
        i = 0
        j = 0
        k = 0
 
        while i < len(left) and j < len(right):
            if left[i][sort_category] > right[j][sort_category]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            k += 1
 
        while i < len(left):
            arr[k] = left[i]
            i += 1
            k += 1
 
        while j < len(right):
            arr[k] = right[j]
            j += 1
            k += 1

def insertionSort(arr):
    for i in range(1, len(arr)):
        val = arr[i]
        pos = i

        while pos > 0 and arr[pos - 1][sort_category] < val[sort_category]:
            arr[pos] = arr[pos - 1]
            pos = pos -1
    
        arr[pos] = val

# streamcount must be 1-100
# multiplier can be any number >= 1, but will increase processing time
streamcount = 100
multiplier = 1

N = streamcount * multiplier
partition = N / size

streamlist = []
raw_list = []


headers = {'client-id': os.environ['CLIENT_ID'], 'Authorization': 'Bearer ' + os.environ['API_AUTH']}

# sequential requests for top N streams
if rank == 0:
    pagination=""

    for i in range(0, multiplier):
        top_streams = requests.get(f'https://api.twitch.tv/helix/streams?first={streamcount}&after={pagination}', headers=headers)
        raw_list.extend(top_streams.json()['data'])
        pagination = top_streams.json()['pagination']['cursor']

# sends results of those requests to every process
raw_list = comm.bcast(raw_list, root=0)

# slices based on rank
for stream in raw_list[int(rank*partition):int(rank*partition+partition)]:
    stream_data = {}

    # calculates how long a stream has been online
    start_time = dateutil.parser.parse(stream['started_at'])
    current_time = datetime.datetime.now(timezone.utc).replace(microsecond=0)
    uptime = current_time - start_time
    stream_data['uptime'] = str(uptime)

    # converts HH:MM:SS uptime format to hours
    split_time = re.split(',| |:', str(uptime))
    if len(split_time) == 3:
        stream_data['uptime_hours'] = int(split_time[0]) + int(split_time[1])/60 + int(split_time[2])/3600
    elif len(split_time) > 3:
        stream_data['uptime_hours'] = int(split_time[0])*24 + int(split_time[3]) + int(split_time[4])/60 + int(split_time[5])/3600
    else:
        stream_data['uptime_hours'] = 0

    # sets stream info
    stream_data['game_name'] = stream['game_name']
    stream_data['user_id'] = stream['user_id']
    stream_data['user_login'] = stream['user_login']
    stream_data['viewer_count'] = stream['viewer_count']
    stream_data['title'] = stream['title']

    # gets follower count of stream
    user_id = stream_data['user_id']
    follow_count = requests.get(f'https://api.twitch.tv/helix/users/follows?to_id={user_id}&first=1', headers=headers)
    stream_data['follow_count'] = follow_count.json()['total']

    # makes sure we don't exceed rate limit
    if int(follow_count.headers['Ratelimit-Remaining']) < 100:
        print(f" Current rate limit: {follow_count.headers['Ratelimit-Remaining']}")
        print(f"Waiting...")
        time.sleep(10)
    
    # local list of channel info
    streamlist.append(stream_data)

# gathers all local lists into a master list at process 0
# this is a list of lists
streamlist = comm.gather(streamlist, root=0)

comm.Barrier()

# lists are scattered back out across processes
split_streamlist = comm.scatter(streamlist, root=0)

# each process merge sorts their list
mergeSort(split_streamlist)

# reduce brings all the values in the sorted lists together into one list
sorted_streamlist = comm.reduce(split_streamlist, root = 0)

# sorted_streamlist is now *nearly* sorted, so insertion sort works well here
if rank == 0:
    insertionSort(sorted_streamlist)


if rank == 0:
    # flattens the streamlist, which is still a list of lists
    # this maintains the original order of the get streams call
    viewcount_sorted = [val for sublist in streamlist for val in sublist]
    print(f"Size of dataset: {len(viewcount_sorted)}")
    
    with open('viewcount_data.json', 'w', encoding='utf-8') as f:
        json.dump(viewcount_sorted, f, ensure_ascii=False, indent=4)

    with open('sorted_data.json', 'w', encoding='utf-8') as f:
        json.dump(sorted_streamlist, f, ensure_ascii=False, indent=4)

if rank == 0:
    json_output = pd.read_json('viewcount_data.json')
    csv_output = json_output.to_csv('raw_data.csv', index = None, header=True)

    path = 'raw_data.csv'
    dataset = pd.read_csv(path, header = 1)

    dataset.columns = ['game_name', 'user_id', 'user_login', 'viewer_count', 'title', 'uptime', 'uptime_hours', 'follow_count']
#print(dataset)

# determine if there is correlation between viewer_count and uptime with target being follow_count // covariance
    numeric_dataset = dataset[['user_id', 'viewer_count', 'uptime_hours', 'follow_count']]
    viewer = dataset['viewer_count']
    uptime = dataset['uptime_hours']
    follow_count = dataset['follow_count']

    correlation = numeric_dataset.corr()
    figure = plt.figure()
    axis = figure.add_subplot(111)
    caxis = axis.matshow(correlation,cmap='coolwarm', vmin=-1, vmax=1)
    figure.colorbar(caxis)
    ticks = np.arange(0,len(numeric_dataset.columns),1)
    axis.set_xticks(ticks)
    plt.xticks(rotation=90)
    axis.set_yticks(ticks)
    axis.set_xticklabels(numeric_dataset.columns)
    axis.set_yticklabels(numeric_dataset.columns)
    plt.show()
    print(correlation)