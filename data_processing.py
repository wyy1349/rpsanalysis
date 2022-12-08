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
'''
filenum = 0
for key in winner_dict:
    filename = "csvs/processed_data_" + str(filenum) + ".csv"
    filenum += 1
    with open(filename, 'w') as f:
        winner_dict[key].to_csv(f, header=False)
'''
# We generate an array with round results and actions taken based on it.
# This means that we take the win/lose of a round and the action taken in the NEXT round
all_winners_array = []
for key in winner_dict:
    single_array = []
    #Make the dataframe index start at 0
    winner_dict[key].reset_index(drop=True, inplace=True)
    #Loop through the rows of the dataframe
    for index, row in winner_dict[key].iterrows():
        
        #Get the player_outcome of the current row and the uds of the next row
        if index < winner_dict[key].shape[0] - 1:
            player_outcome = winner_dict[key].iloc[index]['player_outcome']
            uds = winner_dict[key].iloc[index+1]['uds']
            #Append the first letter of player_outcome and uds to the single_array, capitalize the first letter of player_outcome
            single_array.append(player_outcome[0].upper() + uds[0])
    #Append the single_array to all_winners_array
    all_winners_array.append(single_array)
print(all_winners_array)
