import csv
import pandas as pd
import numpy as np

#Open the csv file using pandas
df = pd.read_csv('rps_v1_data.csv')
#Concatenate game_id and player_id columns to create a unique identifier 
df['game_id'] = df['game_id'].astype(str)
df['player_id'] = df['player_id'].astype(str)
df['game_player_id'] = df['game_id'] + df['player_id']
#Drop the game_id and player_id columns
df = df.drop(['game_id', 'player_id', 'round_begin_ts', 'player_rt', 'player_outcome_viewtime'], axis=1)
#Drop the rows where player_outcome is empty
df = df.dropna(subset=['player_outcome'])

#Create a dictionary of dataframes, one for each game_player_id
df_dict = {k: v for k, v in df.groupby('game_player_id')}

winner_dict = {}

#For each df in df_dict
for key in df_dict:
    #Count the number of rows
    n = df_dict[key].shape[0]
    #Count the number of rows where player_outcome = win
    w = df_dict[key][df_dict[key]['player_outcome'] == 'win'].shape[0]
    l = df_dict[key][df_dict[key]['player_outcome'] == 'loss'].shape[0]
    ratio = w/(w+l)
    #If pct is less than 55%, drop the df from df_dict
    if ratio >= 0.55:
        winner_dict[key] = df_dict[key]

#helper function: convert a sequence of two plays to "UP", "DOWN", "STAY"
#key1: the first play, key 2: the second play. value1: whether the first play is higher, lower, or the same as the second play; value2: is first -> second going up, down or staying
res = {"paper":{"scissors":("L","UP"),"rock":("W","DOWN"),"paper":("T","STAY")},
    "scissors":{"paper":("W","DOWN"),"rock":("L","UP"),"scissors":("T","STAY")},
    "rock":{"paper":("L","UP"),"scissors":("W","DOWN"),"rock":("T","STAY")}}

def compare(key1,key2):
    try:
        return res[key1][key2][1]
    except:
        return "NO INFO"


#helper function: convert a sequence of plays, length n, to a sequence of "UP", "DOWN", "STAY", length n-1
def compare_seq(seq):
    return [compare(seq[i],seq[i+1]) for i in range(len(seq)-1)]

#optional trimming function (inference with length 300 too large)
def last_n_rows(n):
    for key in winner_dict:
        if winner_dict[key].shape[0] > n:
            winner_dict[key] = winner_dict[key].tail(n)

last_n_rows(100)

for key in winner_dict:
    uds_seq = compare_seq(winner_dict[key]['player_move'].tolist())
    uds_seq.insert(0,"NULL")
    #print(uds_seq)
    #set uds_seq as a new column in the dataframe
    winner_dict[key].insert(0,"uds",uds_seq)

#write it into csv

filenum = 0
for key in winner_dict:
    filename = "csvs/processed_data_" + str(filenum) + ".csv"
    filenum += 1
    with open(filename, 'w') as f:
        winner_dict[key].to_csv(f, header=False)
