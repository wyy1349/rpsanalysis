import csv
import pandas as pd
import numpy as np
import json
#import sklearn
from collections import Counter
import matplotlib.pyplot as plt
import random

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

#last_n_rows(100)

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
            state = player_outcome[0].upper() + uds[0]
            if 'N' not in state:
                single_array.append(player_outcome[0].upper() + uds[0])
    #Append the single_array to all_winners_array
    all_winners_array.append(single_array)

all_trans_mat = []
for winner in all_winners_array:
    action_dict = Counter(winner)
    new_action_dict = {k:v/len(winner) for k, v in action_dict.items()}
    for key in new_action_dict:
        if 'N' in key:
            print(winner.index(key), all_winners_array.index(winner))
    all_trans_mat.append(new_action_dict)

def avg_mat(all_mat):
    mat = {}
    for key in all_mat[0]:
        mat[key] = 0
    for one_mat in all_mat:
        for key in mat:
            mat[key] += one_mat.get(key,0)
    for key in mat:
        mat[key] = mat[key]/len(all_mat)
    return mat




#print(all_trans_mat)
avgmat = avg_mat(all_trans_mat)
#print(avgmat)

all_trans_mat_np = []
for m in all_trans_mat:
    arr = np.array([[m['WU'],m['WD'],m['WS']],[m['LU'],m['LD'],m['LS']],[m['TU'],m['TD'],m['TS']]])
    all_trans_mat_np.append(arr)

# for idx, a in enumerate(all_trans_mat_np):
#     #cmap = mpl.colors.ListedColormap(['white', 'red'])
#     plt.imshow(a, cmap='hot', vmin=0, vmax=0.4)
#     new_a = np.zeros(np.array(a.shape) * 100)

#     for j in range(a.shape[0]):
#         for k in range(a.shape[1]):
#             new_a[j * 100: (j+1) * 100, k * 100: (k+1) * 100] = a[j, k]
#     plt.imsave('imgs/heatmap_player_'+str(idx)+'.png',new_a, cmap='hot',vmin=0, vmax=0.4)
# plt.colorbar()
# plt.show()

#clustering
all_trans_mat_clus = []
for m_np in all_trans_mat_np:
    all_trans_mat_clus.append(m_np.flatten())
all_trans_mat_clus = np.array(all_trans_mat_clus)
#print(all_trans_mat_clus.shape)

from sklearn.cluster import KMeans
kmeans5 = KMeans(n_clusters=5)
kmeans5.fit(all_trans_mat_clus)
y_kmeans5 = kmeans5.predict(all_trans_mat_clus)
#print(y_kmeans5)
y_kmeans5_dict = {id:cat for id, cat in enumerate(y_kmeans5)}
print("grouping", y_kmeans5_dict)

fixed_dict = {0: 0, 1: 4, 2: 0, 3: 0, 4: 0, 5: 0, 6: 4, 7: 4, 8: 4, 9: 1, 10: 0, 11: 4, 12: 0, 13: 1, 14: 0, 15: 4, 16: 0, 17: 0, 18: 4, 19: 4, 20: 2, 21: 4, 22: 3, 23: 0, 24: 1, 25: 3, 26: 3, 27: 3, 28: 0, 29: 4}

#averaging within each cluster to get a prototypical x-playstyle player
list_all = [[all_trans_mat_np[key] for key, value in fixed_dict.items() if value == i] for i in range(5)]
av_all = [np.mean(l, axis=0) for l in list_all]

av_dict_list = []
for av in av_all:
    av_dict = {}
    av_dict['W'] = av[0]
    av_dict['L'] = av[1]
    av_dict['T'] = av[2]
    av_dict_list.append(av_dict)


'''
kmeans4 = KMeans(n_clusters=4)
kmeans4.fit(all_trans_mat_clus)
y_kmeans4 = kmeans4.predict(all_trans_mat_clus)
print(y_kmeans4)
y_kmeans4_dict = {id:cat for id, cat in enumerate(y_kmeans4)}
print(y_kmeans4_dict)

kmeans3 = KMeans(n_clusters=3)
kmeans3.fit(all_trans_mat_clus)
y_kmeans3 = kmeans3.predict(all_trans_mat_clus)
print(y_kmeans3)
y_kmeans3_dict = {id:cat for id, cat in enumerate(y_kmeans3)}
print(y_kmeans3_dict)



#Save the all_winners_array to a text file
with open('all_winners_array.txt', 'w') as f:
    f.write(str(all_winners_array))
'''
reverseres = {"paper":{"U":"scissors","D":"rock","S":"paper"},
                "rock":{"U":"paper","D":"scissors","S":"rock"},
                "scissors":{"U":"rock","D":"paper","S":"scissors"}}

def playernextaction(player:dict, lastaction, lastresult):
    udsaction = random.choices(("U","D","S"),weights=player[lastresult],k=1)[0]
    actualact = reverseres[lastaction][udsaction]
    return actualact

def compete(player1:dict, player2:dict, num_rounds:int):
    options = ("rock", "paper", "scissors")
    log = [] #each entry is (p1action, p2action, p1outcome "WLT", p2outcome "WLT")
    p1actionlog = []
    p2actionlog = []
    p1outcomelog = []
    p2outcomelog = []
    
    starting1 = random.choice(options)
    starting2 = random.choice(options)
    p1actionlog.append(starting1)
    p2actionlog.append(starting2)
    p1outcomelog.append(res[p1actionlog[-1]][p2actionlog[-1]][0])
    p2outcomelog.append(res[p2actionlog[-1]][p1actionlog[-1]][0])

    for i in range(num_rounds):
        p1action = playernextaction(player1, p1actionlog[-1], p1outcomelog[-1])
        p2action = playernextaction(player2, p2actionlog[-1], p2outcomelog[-1])
        p1actionlog.append(p1action)
        p2actionlog.append(p2action)
        p1outcomelog.append(res[p1actionlog[-1]][p2actionlog[-1]][0])
        p2outcomelog.append(res[p2actionlog[-1]][p1actionlog[-1]][0])
    
    log = list(zip(p1actionlog, p2actionlog, p1outcomelog, p2outcomelog))
    return log    
        
def maketournament(playerlist, num_rounds):
    num_players = len(playerlist)
    scores = np.zeros((num_players,num_players,3))
    for i in range(num_players):
        for j in range(i+1,num_players):
            log = compete(playerlist[i], playerlist[j], num_rounds)
            p1score = (sum([1 if x[2]=="W" else 0 for x in log])/num_rounds, sum([1 if x[2]=="L" else 0 for x in log])/num_rounds, sum([1 if x[2]=="T" else 0 for x in log])/num_rounds)
            p2score = (sum([1 if x[3]=="W" else 0 for x in log])/num_rounds, sum([1 if x[3]=="L" else 0 for x in log])/num_rounds, sum([1 if x[3]=="T" else 0 for x in log])/num_rounds)
            scores[i,j] = p1score
            scores[j,i] = p2score
    return scores


def makentournaments(playerlist, num_rounds, num_tournaments):
    num_players = len(playerlist)
    scoreboards = np.zeros((num_tournaments,num_players,num_players,3))
    for i in range(num_tournaments):
        scoreboards[i] = maketournament(playerlist, num_rounds)
    return scoreboards

scoreboards = makentournaments(av_dict_list, 1000, 25)
tournament_avg = np.mean(scoreboards, axis=0) #shape is nxnx3

#get a board of binary win/losses from the scoreboard
#apply this to individual scoreboards to get the win/losses from individual tournaments
#apply this to tournament average to see who beats who on average
def winboard(scoreboard):
    num_players = scoreboard.shape[0]
    winboard = np.zeros((num_players,num_players))
    for i in range(num_players):
        for j in range(i+1,num_players):
            if scoreboard[i,j,0] > scoreboard[j,i,0]:
                winboard[i,j] = 1
            elif scoreboard[i,j,0] < scoreboard[j,i,0]:
                winboard[j,i] = 1
            elif scoreboard[i,j,0] == scoreboard[j,i,0]:
                winboard[i,j] = 0.5
                winboard[j,i] = 0.5

    return winboard

print("final winboard", winboard(tournament_avg))

def cumwinboard(scoreboards):
    num_tournaments = scoreboards.shape[0]
    num_players = scoreboards.shape[1]
    cumwinboard = np.zeros((num_players,num_players))
    for i in range(num_tournaments):
        cumwinboard += winboard(scoreboards[i])
    return cumwinboard

print("cumulative winboard", cumwinboard(scoreboards))

#Save the all_winners_array to a json file
#with open('all_winners_array.json', 'w') as f:
#    json.dump(all_winners_array, f)
