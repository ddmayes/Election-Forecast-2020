import pandas as pd
import csv 
from sklearn import preprocessing




#Read in the data as a pd dataframe
data_2016 = pd.read_csv('presidential_polls_2016.csv')
data_2016.head()




#Reorganize data
data_2016 = data_2016[["startdate", "enddate", "state", "matchup", "pollster", "grade", "adjpoll_clinton", "adjpoll_trump"]]
data_2016 = data_2016.rename(columns = {"adjpoll_clinton" : "clinton", "adjpoll_trump" : "trump"})
data_2016["startdate"] = pd.to_datetime(data_2016["startdate"])
data_2016["enddate"] = pd.to_datetime(data_2016["enddate"])
data_2016.head()




#Creation of the democratic "edge" column
data_2016["dem_edge"] = data_2016['clinton'] - data_2016['trump']
data_2016.head()




#Now a similar dataset for 2020
data_2020 = pd.read_csv('2020 US presidential election polls - all_polls.csv')
data_2020.head()




#Drop unecessary cols and reorganize
data_2020 = data_2020[["start.date", "end.date", "state", "pollster", "biden", "trump"]]
data_2020["start.date"] = pd.to_datetime(data_2020["start.date"])
data_2020["end.date"] = pd.to_datetime(data_2020["end.date"])
data_2020["dem_edge"] = data_2020["biden"] - data_2020["trump"]
data_2020.head()




#Again creating the edge value column
data_2020['dem_edge'] = data_2020['dem_edge'] / 100.0




#Create unique set of states and pollsters
states = set()
for val in data_2016['state']:
    states.add(val)

#For simplicity, I've dropped congressional districts of Nebraska and Maine, data provided also did not
#include Alaska or DC so this will result in a total elector count 15 short of the actual 538
#but it's worth noting that this is a rough approximation model
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




#The validation data/actual outcome in each state for the 2016 election
results_2016 = pd.read_csv('nytimes_presidential_elections_2016_results_county.csv')
results_2016.head()




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




data_2016['dem_edge'] = data_2016['dem_edge'] / 100.0
print(data_2016['dem_edge'])




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




data_2016['actual_outcome']
i = 0
for row in data_2016['state']:
    data_2016['actual_outcome'][i] = actual_results[row]
    i = i + 1
data_2016.head()


#Now for a simple prediction model using solely
#poll leads as the features


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




#Onto 2020!
electoral = pd.read_csv('electoral-college.csv')
electoral.head()



#Organizing elector columns by state
electors = {}
for i in range(len(electoral)):
    electors[electoral['State'][i]] = electoral['Electors'][i]
    i = i + 1




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




#Abbreviated states
ab_states = set()
for state in data_2020['state']:
    ab_states.add(state)
print(ab_states)    




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




for state in ab_states:
    if average_edge_by_state[state] > 0:
        biden_electors = biden_electors + electors[state]
    elif average_edge_by_state[state] < 0:
        trump_electors = trump_electors + electors[state]

print("Trump's predicted elector count: ", trump_electors)
print("Biden's predicted elector count: ", biden_electors)



