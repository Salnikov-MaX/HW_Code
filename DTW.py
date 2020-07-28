import lasio
import pandas as pd
import os
import seaborn as sns
% matplotlib
inline
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
from dtw import dtw
import itertools
import operator
from operator import itemgetter



class my_dictionary(dict):
    def __init__(self):
        self = dict()

    def add(self, key, value):
        self[key] = value


# Создание списка с названиями скважин

targ_form = pd.read_csv('C:/Users/SMA_9/Desktop/HW/FieldWTPS1.csv', sep=';')
targ_form = targ_form.groupby(['Well', 'Surface']).aggregate({'MD': 'mean'})
files = []
length = targ_form['MD'].size
for i in range(length):
    files.append(targ_form['MD'].index[i][0])
files = set(files)

# Подготовка данных каротажа

for i_file in files:
    try:
        cor = lasio.read('C://Users/SMA_9/Desktop/HW/path/' + i_file + '.las')
        SP = pd.DataFrame({'DEPT': cor['DEPT'], 'SP': cor['SP']})
        SP = SP.fillna(0)
        SP = SP.query("SP != 0 & SP != 9999 & SP != (-9999)")
        if targ_form.loc[i_file.split('.')[0]].nunique()[0] == 2:
            top = targ_form.loc[(i_file.split('.')[0], 'Top_Georg')][0]
            bottom = targ_form.loc[(i_file.split('.')[0], 'U1-3_bot')][0]
        else:
            top = targ_form.loc[(i_file.split('.')[0], 'Top_Georg')][0]
            bottom = top + 100
        SP = SP.query("DEPT >= @top  & DEPT <= @bottom ")
        if SP.size > 0:
            typic = SP.rename(columns={'DEPT': 'Y', 'SP': 'X'})
            typic.Y = (typic.Y - typic.Y.min()) * 100 / (typic.Y.max() - typic.Y.min())
            typic.X = (typic.X - typic.X.min()) * 1 / (typic.X.max() - typic.X.min())
            f = interpolate.interp1d(typic.Y.values, typic.X.values)
            ynew = np.arange(0, 100, 1)
            xnew = f(ynew)
            corotazh_total = pd.DataFrame({'Y': ynew[::-1], 'X': xnew})
            corotazh_total.to_csv('C://Users/SMA_9/Desktop/HW/OutData2/' + i_file.split('.')[0] + '.csv')
    except Exception:
        pass

# Подготовка данных типовых кривых

files = os.listdir(path="C://Users/SMA_9/Desktop/HW/typical/CSV")
for i in files:
    typic = pd.read_csv('C://Users/SMA_9/Desktop/HW/typical/CSV/' + i, sep=';')
    typic.Y = (typic.Y - typic.Y.min()) * 55 / (typic.Y.max() - typic.Y.min())
    typic.X = (typic.X - typic.X.min()) * 1 / (typic.X.max() - typic.X.min())
    f = interpolate.interp1d(typic.Y.values, typic.X.values)
    xnew = f(np.arange(0, 55, 1))
    corotazh_total = pd.DataFrame({'Y': np.arange(0, 55, 1), 'X': xnew})
    corotazh_total.to_csv('C://Users/SMA_9/Desktop/HW/typical/reb/' + i)



# Применение алгоритма DTW для классификации и сохранение данных в формат CSV
    
files = os.listdir(path="C://Users/SMA_9/Desktop/HW/OutData2")
data_1 = pd.DataFrame({'well': [], "typic": [], "value": []})
g = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
for u in files:
    my_dict = my_dictionary()
    SP = pd.read_csv('C://Users/SMA_9/Desktop/HW/OutData2/' + u)
    x = SP.X
    for i in g:
        SP1 = pd.read_csv('C://Users/SMA_9/Desktop/HW/typical/reb/' + i + '.csv', index_col=0)
        y = SP1.X
        manhattan_distance = lambda x, y: np.abs(x - y)
        d, cost_matrix, acc_cost_matrix, path = dtw(x, y, dist=manhattan_distance)
        my_dict.add(i, d)
    for key, value in itertools.islice(sorted(my_dict.items(), key=operator.itemgetter(1)), 1):
        data_1 = pd.concat([data_1, pd.DataFrame({'well': [u], "typic": [key], "value": [value]})])

data_1.to_csv('C:/Users/SMA_9/Desktop/HW/mark.csv')