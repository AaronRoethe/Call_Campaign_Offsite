import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
import time
import string

from FileLoad import Final_Load
# from Cluster import Clusters
from Skills import complex_skills
from Sprint_Schedule import Daily_Maping

startTime_1 = time.time()

today = date.today()
tomorrow = (today + timedelta(days = 1)).strftime("%Y-%m-%d")

### Get data and mutate
df0 = Final_Load()
df0['Daily_Groups'] = pd.Series(dtype=object)
df0 = Daily_Maping(df0)

## Sprint Schedulual Day
def Map_categories(df):
    Day = 1
    Sprint = 10

    ### Map and Sort
    Sprint_schedual = list(range(0,Sprint))
    Category = list(string.ascii_uppercase)[:Sprint]
    Sprint_schedual = Sprint_schedual[-Day:] + Sprint_schedual
    Daily_sort = dict(zip(Category,Sprint_schedual))
    df['Daily_Priority'] = df['Daily_Groups'].map(Daily_sort)
    return df
df0 = Map_categories(df0)#.sort_values('Daily_Priority'))

def Date_Bins(df):
    df0 = df
    q4 = max(df0['Project Due Date'])
    q0 = min(df0['Project Due Date'])
    q2 = q0 + (q4 - q0)/2
    q1 = q0 + (q2 - q0)/2
    q3 = q2 + (q4 - q2)/2
    bin = [q0,q1,q2,q3,q4]
    label = []
    for i in bin[1:]:
        label.append(i.strftime('%y%m%d'))
    df0['Date Bin'] = pd.cut(df0['Project Due Date'],bins = bin, labels=label, include_lowest=True, right = True).astype("int")
    df_dummy_Due = pd.get_dummies(df0['Date Bin'])
    df0 = df0.join(df_dummy_Due)

    name_sort = {'Escalated':0, 'Unscheduled':1,'PNP Released':2,'Past Due':3,'Scheduled':4}
    rm_sort = {'EMR Remote': 0, 'HIH - Other': 2, 'Onsite':1,'Offsite':3}
    age_sort = {21: 0, 0: 1, 20:2, 15:3, 10:4, 5:5}
    df0['status_sort'] = df0['Outreach Status'].map(name_sort)
    df0['rm_sort'] = df0['Retrieval Group'].map(rm_sort)
    df0['age_sort'] = df0['Group Number'].map(age_sort)

    df_dummy_status = pd.get_dummies(df0['Outreach Status'])
    # df_dummy_age = pd.get_dummies(df0['Group Number'])
    df1 = df0.join(df_dummy_status)#.join(df_dummy_age) #,21:'sum', 0:'sum', 20:'sum', 15:'sum', 10:'sum', 5:'sum'
    df1['Unique Phone'] = 0 

    col_stat = df0['Outreach Status'].unique()
    d1 = dict.fromkeys(col_stat, 'sum')
    label = [int(x) for x in label]
    d2 = dict.fromkeys(label, 'sum')
    col = {'PhoneNumber':'count','Cluster':'mean',**d1, **d2,}
    ### Unique Numbers count and status
    df2 = df1.groupby(['PhoneNumber']).agg(col).rename(columns={'PhoneNumber':'OutreachID Count','Cluster':'Cluster_Avg'})
    df2 = df2.reset_index()
    return df2
print(Date_Bins(df0))
# ### Add info to main line and reskill
# df3 = pd.merge(df0,df2, on='PhoneNumber')
# df3 = complex_skills(df3)

# ### Sort Order and drop Dups
# # df4 = df3.sort_values(by = ['Daily_Priority', 'rm_sort', 'status_sort','age_sort', 'Unscheduled', 'Cluster_Avg'], ascending= [True, True, True, True, False, True]).reset_index(drop = True)
# df4 = df3.sort_values(by = ['Date Bin','rm_sort', 'status_sort','age_sort', 'Unscheduled', 'Cluster_Avg'], ascending= [True, True, True, True, False, True]).reset_index(drop = True)

# df4 = df4.drop_duplicates(['PhoneNumber']).reset_index(drop = True)
# df4 = df4.sort_values(by = ['age_sort','DueDate Avg']).reset_index(drop = True)

# df4['Unique Phone'] = 1

# ### Rank and append duplicate list
# def Rank_Individual_skill(df):
#     df4 = df
#     Skills = df4['Skill'].unique()
#     df_skill = pd.DataFrame()

#     def Score(df, skill):
#         df1 = df[df['Skill'] == skill].reset_index(drop= True)
#         End = len(df1)
#         Range = list(range(0, End, 1))
#         Retrieval = pd.DataFrame(Range,columns= ['Score'])
#         df1['Score'] = Retrieval['Score']
#         return df1

#     for i in Skills:
#         df_skill = df_skill.append(Score(df4, i))
#     return df_skill.sort_values('Score').reset_index(drop= True)

# df_skill = Rank_Individual_skill(df4)

# ### Create file with assigned categories to ORG
# def Assign_Map(df):
#     skills = df['Skill'].unique()
#     df_key = pd.DataFrame()
#     def assign_skill(df, sk):
#         dk_skill = df[df['Skill'] == sk].reset_index(drop = True)
#         #### INPUT BY DAY ####
#         Sprint = 10
#         ######################
#         df_len = len(dk_skill.index)
#         group_size = df_len // Sprint 
#         letters = list(string.ascii_uppercase)[:Sprint] * group_size
#         letters.sort()
#         ## Create Same len list of letters as len of df
#         Daily_Priority = pd.DataFrame(letters, columns=['Daily_Groups'])
#         add_back = df_len - len(Daily_Priority)
#         Daily_Priority = Daily_Priority.append(Daily_Priority.iloc[[-1]*add_back]).reset_index(drop=True)
#         df_join = dk_skill.join(Daily_Priority)[['PhoneNumber', 'Skill','Daily_Groups']]
#         return df_join
#     ## Add together all skills with uniquely broken out sprints
#     for i in skills:
#         df_key = df_key.append(assign_skill(df, i))
#     path2 = 'C:\\Users\\ARoethe\\OneDrive - CIOX Health\\Aaron\\Projects\\Call Campaign Automation\\Table_Drops\\'
#     df_key.to_csv(path2 + 'Assignment_Map' + str(tomorrow) +  '.csv', index=False)
# # Re calculate ever 2 weeks
# Assign_Map(df_skill)

# # Add Unique ORGs to Rank list 
# df5 = df_skill.append(df3)
# df6 = df5.drop_duplicates(['OutreachID']).reset_index(drop= True)

# ### Piped ORGs attached to phone numbers
# df6['OutreachID'] = df6['OutreachID'].astype(str)
# df6['Matches'] = df6.groupby(['PhoneNumber'])['OutreachID'].transform(lambda x : '|'.join(x)).apply(lambda x: x[:3000])

# df = df6
# # df = df[df['ORG Stat'] == 1]
# # print(df)
# # print(df4.groupby('Skill').agg({'OutreachID Count':'count', 'TotalCharts':'sum'}).sort_values('OutreachID Count', ascending= False))
# # print(df.groupby('Skill').agg({'OutreachID Count':'count', 'TotalCharts':'sum'}).sort_values('OutreachID Count', ascending= False))

# def Save(Where):
#     if Where == 'Work':
#         path = 'C:\\Users\\ARoethe\\OneDrive - CIOX Health\\Aaron\\Projects\\Call Campaign Automation\\dump\\Group_Rank\\'
#         path2 = 'C:\\Users\\ARoethe\\OneDrive - CIOX Health\\Aaron\\Projects\\Call Campaign Automation\\Table_Drops\\'
#     else:
#         path = 'C:\\Users\\roeth\\OneDrive - CIOX Health\\Aaron\\Projects\\Call Campaign Automation\\dump\\Group_Rank\\'
#         path2 = 'C:\\Users\\roeth\\OneDrive - CIOX Health\\Aaron\\Projects\\Call Campaign Automation\\Table_Drops\\'

#     df.to_csv(path + str(tomorrow) +  '.csv', index=False)

#     df.to_csv(path2 + 'Group_Rank.csv', index=False)

# Save('Work')



executionTime_1 = (time.time() - startTime_1)
print("-----------------------------------------------")
print('Time: ' + str(executionTime_1))
print("-----------------------------------------------")