#!/usr/bin/env python
# coding: utf-8

# In[16]:


import re
import pandas as pd
import numpy as np


file_path = 'Midnight_logs.txt'

# Read the entire content of the file
with open(file_path, 'r') as file:
    file_content = file.read()

# Split the content into blocks based on "Date" strings
blocks = re.split(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} MidnightData:', file_content)
blocks = [block.strip() for block in blocks if block.strip()]


# Create a DataFrame with a single column
df = pd.DataFrame(blocks, columns=['Complete_Row'])
df = df.iloc[1:,:]


df['models_list'] = df['Complete_Row'].str.split(',')
df_listed = pd.DataFrame(df['models_list'].tolist()).fillna('')
df_listed.columns = df_listed.iloc[0,:]
df_listed = df_listed.iloc[1:,:]

df_listed.rename(columns={'Price': 'Midnight Price'}, inplace=True)

df_listed.set_index('Date', inplace=True)

df_listed.index = pd.to_datetime(df_listed.index)
df_listed = df_listed.resample('d').last()
df_listed.dropna(inplace=True)

one_day = pd.DateOffset(days=1)
df_listed = df_listed.shift(freq=one_day)

df_listed = df_listed.iloc[:-1,:-2]


for i in df_listed.columns:
    if 'pearson' in i:
        df_listed[i] = pd.to_numeric(df_listed[i])

    elif 'Midnight Price' == i:
        df_listed[i] = pd.to_numeric(df_listed[i])
        


df_listed.tail()


# In[17]:




file_path = 'Morning_logs.txt'

# Read the entire content of the file
with open(file_path, 'r') as file:
    file_content = file.read()

# Split the content into blocks based on "Date" strings
blocks = re.split(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} MorningData:', file_content)
blocks = [block.strip() for block in blocks if block.strip()]


# Create a DataFrame with a single column
df_morn = pd.DataFrame(blocks, columns=['Complete_Row'])
df_morn = df_morn.iloc[1:,:]

display(df_morn.head())
df_morn['models_list'] = df_morn['Complete_Row'].str.split(',')
df_morn_listed = pd.DataFrame(df_morn['models_list'].tolist()).fillna('')
df_morn_listed.columns = df_morn_listed.iloc[0,:]
df_morn_listed = df_morn_listed.iloc[1:,:]

df_morn_listed.set_index('Date', inplace=True)

df_morn_listed.index = pd.to_datetime(df_morn_listed.index)
df_morn_listed = df_morn_listed.resample('d').last()
df_morn_listed.dropna(inplace=True)


df_morn_listed = df_morn_listed.iloc[:-1,:-2]
display(df_morn_listed.head())

df_morn_listed['1:30pm Price']= pd.to_numeric(df_morn_listed['1:30pm Price'])
df_morn_listed['AM Session High'] = pd.to_numeric(df_morn_listed['AM Session High'])
df_morn_listed['AM Session Low'] = pd.to_numeric(df_morn_listed['AM Session Low'])


df_morn_listed.columns


# In[18]:



file_path = 'DailyProfile_logs.txt'

# Read the entire content of the file
with open(file_path, 'r') as file:
    file_content = file.read()

# Split the content into blocks based on "Date" strings
blocks = re.split(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} DailyProfile:', file_content)
blocks = [block.strip() for block in blocks if block.strip()]


# Create a DataFrame with a single column
df_prof = pd.DataFrame(blocks, columns=['Complete_Row'])
df_prof = df_prof.iloc[1:,:]

display(df_prof.head())
df_prof['models_list'] = df_prof['Complete_Row'].str.split(',')
df_prof_listed = pd.DataFrame(df_prof['models_list'].tolist()).fillna('')
df_prof_listed.columns = df_prof_listed.iloc[0,:]
df_prof_listed = df_prof_listed.iloc[1:,:]

df_prof_listed.set_index('Date', inplace=True)

df_prof_listed.index = pd.to_datetime(df_prof_listed.index)
df_prof_listed = df_prof_listed.resample('d').last()
df_prof_listed.dropna(inplace=True)


df_prof_listed = df_prof_listed.iloc[:-1,:-2]
display(df_prof_listed.head())


# In[19]:


df_prof_listed.tail(10)


# In[23]:


df_whole = df_listed.merge(df_morn_listed, right_index=True, left_index=True, how='inner')


df_whole.rename(columns ={'1:30pm Price':'Morning Price'}, inplace=True)
df_whole = df_whole.iloc[:-1,:]

display(df_whole.dtypes)
df_whole['am_session'] = df_whole['Morning Price'] - df_whole['Midnight Price']
df_whole['pm_session'] = df_whole['Midnight Price'] - df_whole['Morning Price'].shift()

df_whole = df_whole.merge(df_prof_listed, right_index=True, left_index=True, how='inner')

df_whole.dropna(inplace=True)
df_whole.index = df_whole.index.astype(str)


# In[24]:


df_whole.tail(60)


# In[26]:


df_whole.to_excel('Midnight_logs_processed_str.xlsx')


# 
# • AM session points (+ / -)
# 
# • PM session points (+ / -)
# 
# • Make changes to Pearson R depending on if the channel is + / -
# 
# • EMA-50 on H4 and H1
# 
# • Daily Candle Close

# - Midnight SPX500 price
# - AM session points (difference between midnight price and 1:30 pm price, if bearish value should be - and + if bullish)
# - PM session points (difference between 1:30pm and midnight price, if bearish value should be - and + if bullish)
# 
# We need to slightly alter the Pearson R values, if the channel is bullish, the Pearson R should be +. 
# 
# EMA-50 for H4 and H1 - was price above / below the EMA at midnight?

# In[ ]:




