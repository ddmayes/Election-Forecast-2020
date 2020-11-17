#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import csv 
from sklearn import preprocessing


# In[3]:


#Read in the data as a pd dataframe
data_2016 = pd.read_csv('presidential_polls_2016.csv')
data_2016.head()


# In[4]:


#Reorganize data
data_2016 = data_2016[["startdate", "enddate", "state", "matchup", "pollster", "grade", "adjpoll_clinton", "adjpoll_trump"]]
data_2016 = data_2016.rename(columns = {"adjpoll_clinton" : "clinton", "adjpoll_trump" : "trump"})
data_2016["startdate"] = pd.to_datetime(data_2016["startdate"])
data_2016["enddate"] = pd.to_datetime(data_2016["enddate"])
data_2016.head()


# In[5]:


#Creation of the democratic "edge" column
data_2016["dem_edge"] = data_2016['clinton'] - data_2016['trump']
data_2016.head()


# In[2]:


#Now a similar dataset for 2020
data_2020 = pd.read_csv('2020 US presidential election polls - all_polls.csv')
data_2020.head()


# In[3]:


#Drop unecessary cols and reorganize
data_2020 = data_2020[["start.date", "end.date", "state", "pollster", "biden", "trump"]]
data_2020["start.date"] = pd.to_datetime(data_2020["start.date"])
data_2020["end.date"] = pd.to_datetime(data_2020["end.date"])
data_2020["dem_edge"] = data_2020["biden"] - data_2020["trump"]
data_2020.head()


# In[4]:


data_2020['dem_edge'] = data_2020['dem_edge'] / 100.0


# In[8]:


#Create unique set of states and pollsters
states = set()
for val in data_2016['state']:
    states.add(val)

pollsters = set()
for val in data_2016['pollster']:
    pollsters.add(val)
states.remove('Nebraska CD-1')
states.remove('District of Columbia')
states.remove('Nebraska CD-2')
states.remove('Maine CD-1')
states.remove('Nebraska CD-3')
states.remove('Maine CD-2')
states.remove('U.S.')
states.remove('Alaska')


# In[9]:


#The validation data
results_2016 = pd.read_csv('nytimes_presidential_elections_2016_results_county.csv')
results_2016.head()


# In[10]:


#The actual outcome in each state. If positive, democratic, assuming winner take all
actual_results = {}
for state in states:
    running_total = 0
    total = 0
    with open('nytimes_presidential_elections_2016_results_county.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if row[3] == state:
                    lead = (float(row[0]) - float(row[1]))
                    total = total + (float(row[0]) + float(row[1]))
                    running_total = running_total + lead
    actual_results[state] = running_total / total

print(actual_results)

dem_or_rep_victory_by_state = {}
for val in actual_results:
    if actual_results[val] > 0:
        dem_or_rep_victory_by_state[val] = 'dem'
    else:
        dem_or_rep_victory_by_state[val] = 'rep'
print(dem_or_rep_victory_by_state)


# In[11]:


data_2016['dem_edge'] = data_2016['dem_edge'] / 100.0
print(data_2016['dem_edge'])


# In[16]:


the_total = 0
for val in actual_results:
    the_total = the_total + actual_results[val]
actual_results['U.S.'] = the_total / len(actual_results)
actual_results['Alaska'] = the_total / len(actual_results)
actual_results['Maine CD-1'] = the_total / len(actual_results)
actual_results['Maine CD-2'] = the_total / len(actual_results)
actual_results['Nebraska CD-1'] = the_total / len(actual_results)
actual_results['Nebraska CD-2'] = the_total / len(actual_results)
actual_results['Nebraska CD-3'] = the_total / len(actual_results)
actual_results['District of Columbia'] = the_total / len(actual_results)


# In[21]:


data_2016['actual_outcome']
i = 0
for row in data_2016['state']:
    data_2016['actual_outcome'][i] = actual_results[row]
    i = i + 1
data_2016.head()


# In[24]:


from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

features = ['clinton', 'trump', 'dem_edge']
X = data_2016[features]
y = data_2016.actual_outcome

train_X, valid_X, train_y, valid_y = train_test_split(X, y, random_state=1)

model = RandomForestRegressor(random_state=1)
model.fit(train_X, train_y)
model_predictions = model.predict(valid_X)
error = mean_absolute_error(model_predictions, valid_y)
print("Mean absolute error for this model: ", error)


# In[5]:


#Onto 2020!
electoral = pd.read_csv('electoral-college.csv')
electoral.head()


# In[6]:


electors = {}
for i in range(len(electoral)):
    electors[electoral['State'][i]] = electoral['Electors'][i]
    i = i + 1


# In[41]:


data_2020['electors'] = '0'
k = 0
for row in data_2020['state']:
    if row != '--':
        data_2020['electors'][k] = electors[row]
        k = k + 1
    elif row == '--':
        data_2020['electors'][k] = 0
        k = k + 1
    else:
        k = k + 1
        continue
data_2020.head()


# In[42]:


#Abbreviated states
ab_states = set()
for state in data_2020['state']:
    ab_states.add(state)
print(ab_states)    


# In[43]:


trump_elector = 0
biden_electors = 0
average_edge_by_state = {}
for state in ab_states:
    running_avg = []
    for i in range(len(data_2020)):
        if data_2020['state'][i] == state:
            running_avg.append(data_2020['dem_edge'][i])
    average_edge_by_state[state] = sum(running_avg) / len(running_avg)
    
print(average_edge_by_state)


# In[61]:


for state in ab_states:
    if average_edge_by_state[state] > 0:
        biden_electors = biden_electors + electors[state]
    elif average_edge_by_state[state] < 0:
        trump_electors = trump_electors + electors[state]

print("Trump's predicted elector count: ", trump_electors)
print("Biden's predicted elector count: ", biden_electors)


# In[16]:


better_data_2020 = pd.read_csv('president_polls.csv')
better_data_2020.head()


# In[17]:


better_data_2020 = better_data_2020[["start_date", "end_date", "state", "fte_grade", "pollster", "answer", "pct"]]
better_data_2020.head()


# In[18]:


new2020data = better_data_2020[(better_data_2020["answer"] == "Biden") | (better_data_2020["answer"] == "Trump")]
new2020data = new2020data.pivot_table(values = 'pct', index=['start_date', 'end_date', 'state', 'fte_grade', 'pollster'], columns='answer')
new2020data = new2020data.dropna(axis = 0, how = 'any')
new2020data.head()


# In[19]:


new2020data['dem_edge'] = (new2020data["Biden"] - new2020data["Trump"]) / 100.0
new2020data.head()


# In[20]:


new2020data['electors'] = '0'
k = 0
for row in new2020data['state']:
    if row != '--':
        new2020data['electors'][k] = electors[row]
        k = k + 1
    elif row == '--':
        data_2020['electors'][k] = 0
        k = k + 1
    else:
        k = k + 1
        continue
new2020data.head()


# In[25]:


states_2020_pt2 = set()
for state in new2020data["state"]:
    states_2020_pt2.add(state)


# In[ ]:





# In[ ]:




