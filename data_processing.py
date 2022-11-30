import csv
import pandas as pd
import numpy as np

with open('rps_v1_data.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in spamreader:
        #print(', '.join(row))
    
#use pandas to extract the correct columns from csv file

#translate both into rps and win/lose/tie

#optional trimming function (inference with length 300 too large)

#write it into json
