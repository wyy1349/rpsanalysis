import numpy as np

#print(np.cumsum([0.1,0.1,0.15,0.12,0.12,0.08,0.11,0.11,0.11]))
strg = "['LS', 'LD', 'TU', 'TS', 'TU', 'LD', 'WS', 'TD', 'WU', 'LS', 'WD', 'LS', 'TU', 'LS', 'TU', 'LS', 'WD', 'WS', 'LD', 'WU', 'WU', 'WD', 'WU', 'TD', 'WU', 'WU', 'TU', 'TD', 'TD', 'WD', 'LD', 'WS', 'TD', 'WD', 'TS', 'WU', 'WU', 'WS', 'WU', 'LU', 'TU', 'TU', 'LD', 'TS', 'WU', 'TU', 'WS', 'WD', 'TS', 'WD', 'LS', 'WD', 'LS', 'WU', 'TS', 'LU', 'TU', 'TS', 'WU', 'WS', 'TU', 'TS', 'WU', 'TS', 'WU', 'TS', 'LD', 'WD', 'TS', 'TU', 'WU', 'TD', 'TD', 'TD', 'TU', 'TU', 'TS', 'LU', 'LD', 'WD', 'WS', 'WU', 'LD', 'LD', 'LD', 'LD', 'LU', 'WU', 'TU', 'TS', 'LU', 'WS', 'TD', 'WS', 'TU', 'LU', 'WU', 'TS', 'TU']"
f=lambda x: x.replace("'",'"')
print(f(strg))