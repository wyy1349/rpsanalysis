import csv
import pandas as pd
import numpy as np

<<<<<<< Updated upstream
=======
with open('rps_v1_data.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in spamreader:
        print(', '.join(row))
>>>>>>> Stashed changes
#Open the csv file using pandas
df = pd.read_csv('rps_v1_data.csv')
#Concatenate game_id and player_id columns to create a unique identifier 
df['game_id'] = df['game_id'].astype(str)
df['player_id'] = df['player_id'].astype(str)
df['game_player_id'] = df['game_id'] + df['player_id']
#Drop the game_id and player_id columns
df = df.drop(['game_id', 'player_id', 'round_begin_ts', 'player_rt', 'player_outcome_viewtime'], axis=1)

#Create a dictionary of dataframes, one for each game_player_id
df_dict = {k: v for k, v in df.groupby('game_player_id')}
<<<<<<< Updated upstream

=======
#For each df in df_dict
for key in df_dict:
    #Count the number of rows
    n = df_dict[key].shape[0]
    #Count the number of rows where player_outcome = win
    w = df_dict[key][df_dict[key]['player_outcome'] == 'win'].shape[0]
    pct = w/(n*100)
    #If pct is less than 55%, drop the df from df_dict
    if pct < 0.55:
        del df_dict[key]
    
>>>>>>> Stashed changes
#use pandas to extract the correct columns from csv file

#helper function: convert a sequence of two plays to "UP", "DOWN", "STAY"
#key1: the first play, key 2: the second play. value1: whether the first play is higher, lower, or the same as the second play; value2: is first -> second going up, down or staying
res = {"paper":{"scissors":("L","UP"),"rock":("W","DOWN"),"paper":("T","STAY")},
    "scissors":{"paper":("W","DOWN"),"rock":("L","UP"),"scissors":("T","STAY")},
    "rock":{"paper":("L","UP"),"scissors":("W","DOWN"),"rock":("T","STAY")}}

def compare(key1,key2):
    return res[key1][key2][1]

#helper function: convert a sequence of plays, length n, to a sequence of "UP", "DOWN", "STAY", length n-1
def compare_seq(seq):
    return [compare(seq[i],seq[i+1]) for i in range(len(seq)-1)]

#translate both into rps and win/lose/tie

#optional trimming function (inference with length 300 too large)

#write it into json
