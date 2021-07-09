import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
import glob
import os
import zipfile
from Skills import complex_skills
from Bus_day_calc import next_business_day, Next_N_BD, map_piv, daily_piv, newPath

import csv
csv.field_size_limit(1000)

today = date.today()
tomorrow = (today + timedelta(days = 1))#.strftime("%m/%d/%Y")
yesterday = (today + timedelta(days = -1))#.strftime("%m/%d/%Y")
F_today = today.strftime("%m%d")
nxt_day = next_business_day(today)
F_today = str('Call_Campaign_v4_' + F_today +'*.txt')
Dpath = newPath('dump','Call_Campaign') + F_today

for file in glob.glob(Dpath):
    filename = file

def Load():
    df = pd.read_csv(filename, sep='|', error_bad_lines=False, engine="python")
    df['PhoneNumber'] = pd.to_numeric(df['PhoneNumber'], errors='coerce')
    df['Site Clean Id'] = pd.to_numeric(df['Site Clean Id'], errors='coerce')
    return df

def Format(File):
    Format_Now = File.copy()
    Format_Now['Last Call'] = pd.to_datetime(Format_Now['Last Call'], errors='coerce').dt.date.copy()
    Format_Now['Last Call'] = pd.to_datetime(Format_Now['Last Call'], errors='coerce').dt.date
    Format_Now['Recommended Schedule Date'] = pd.to_datetime(Format_Now['Recommended Schedule Date'], errors='coerce').dt.date
    Format_Now['Project Due Date'] = pd.to_datetime(Format_Now['Project Due Date'])
    return Format_Now

def Clean_Numbers(df):
    df1 = df.dropna(subset=['PhoneNumber'])
    df1 = df1[df1['PhoneNumber'] > 1111111111]
    return df1

def Last_Call(df):
    df['Last Call'] = pd.to_datetime(df['Last Call'], errors='coerce').dt.date.copy()
    df1 = df
    df1 = df1[df1['Last Call'].notnull()].copy()
    df1['New'] = tomorrow

    df1['DateDiff'] = df1['New'] - df1['Last Call']
    df1 = df1.copy()
    df1['Age'] = (df1['DateDiff']/np.timedelta64(1,'D')).astype(int)

    df['Age'] = 0
    df['Age'] = df1['Age']
    df['Group Number'] = 0
    filter = df['Last Call'].isna()
    df['Group Number'] = np.where(filter, 0, df['Group Number'])

    filter = (df['Age'] >= 0) & (df['Age'] <= 5)
    df['Group Number'] = np.where(filter, 5, df['Group Number'])

    filter = (df['Age'] >= 6) & (df['Age'] <= 10)
    df['Group Number'] = np.where(filter, 10, df['Group Number'])

    filter = (df['Age'] >= 11) & (df['Age'] <= 15)
    df['Group Number'] = np.where(filter, 15, df['Group Number'])

    filter = (df['Age'] >= 16) & (df['Age'] <= 20)
    df['Group Number'] = np.where(filter, 20, df['Group Number'])

    filter = (df['Age'] >= 21)
    df['Group Number'] = np.where(filter, 21, df['Group Number'])

    df['Age'] = df['Age'].fillna(0)
    return df

def Final_Load(Precheck):
    df = Last_Call(Clean_Numbers(Format(Load())))
    df = df.loc[df['OutreachID'].notnull()].copy()
    df['Cluster'] = 0
    df['Load Date'] = nxt_day.strftime("%Y-%m-%d")
    
    df['Daily_Groups'] = 0
    # Precheck = Precheck
    def Test_Load(df, Precheck):
        df0 = df
        if Precheck == 1:
            today = yesterday
        test = df0[df0['Last Call'] == today]['Last Call']
        if today == test.max():
            test_results = print('||| Pass ||| Last Call Count:\t' + str(test.count()))
        else:
            test_results = 'Fail'
        return test_results
    test = Test_Load(df, Precheck)
    return df, test
 # print(filename)
# df, test = Final_Load(1)
# print(df)


if __name__ == "__main__":
    print("File will load")