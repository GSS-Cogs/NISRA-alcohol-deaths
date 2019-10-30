#!/usr/bin/env python
# coding: utf-8

# In[118]:


from gssutils import *

scraper = Scraper('https://www.nisra.gov.uk/publications/alcohol-related-deaths-2007-2017')
scraper.distribution(
    title='Alcohol-Specific Deaths Tables 2007- 2017'
).downloadURL


# In[119]:


if is_interactive():
    import requests
    from cachecontrol import CacheControl
    from cachecontrol.caches.file_cache import FileCache
    from cachecontrol.heuristics import LastModified
    from pathlib import Path

    session = CacheControl(requests.Session(),
                           cache=FileCache('.cache'),
                           heuristic=LastModified())

    sourceFolder = Path('in')
    sourceFolder.mkdir(exist_ok=True)

    inputURL = 'https://www.nisra.gov.uk/sites/nisra.gov.uk/files/publications/Alcohol_Tables_17.xls'
    inputFile = sourceFolder / 'Alcohol_Tables_17.xls'
    response = session.get(inputURL)
    with open(inputFile, 'wb') as f:
      f.write(response.content)
    tab = loadxlstabs(inputFile, sheetids='Table 2')[0]


# In[120]:


tidy = pd.DataFrame()


# In[121]:


cell = tab.filter('Registration Year')
age = cell.fill(RIGHT).is_not_blank().is_not_blank().is_not_whitespace() |        cell.shift(0,1).fill(RIGHT).is_not_blank().is_not_whitespace()
Year = cell.fill(DOWN).is_not_blank().is_not_whitespace()
observations = Year.fill(RIGHT).is_not_blank().is_not_whitespace()
Dimensions = [
            HDim(Year,'Year',DIRECTLY,LEFT),
            HDim(age, 'Age',DIRECTLY,ABOVE),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit','People'),
            HDimConst('Sex', 'T'),
            HDimConst('Underlying Cause of Death', 'all-alcohol-related-deaths'),
            HDimConst('Health and Social Care Trust', 'all')
            ]
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
if is_interactive():
    savepreviewhtml(c1)
table = c1.topandas()


# In[122]:


import numpy as np
table['OBS'].replace('', np.nan, inplace=True)
table.dropna(subset=['OBS'], inplace=True)
table.rename(columns={'OBS': 'Value'}, inplace=True)
table['Value'] = table['Value'].astype(int)


# In[123]:


table['Period'] = 'year/' + table['Year'].astype(str).str[0:4]


# In[124]:


table['Period'] = table['Period'].map(
    lambda x: {
        'year/Tota' : 'gregorian-interval/2007-01-01T00:00:00/P10Y'       
        }.get(x, x))


# In[125]:


table = table[table['Age'] != 'Median Age']


# In[126]:


table['Age'] = table['Age'].map(
    lambda x: {
        '25-34' : 'nisra5/25-34' , 
        '35-44' : 'nisra5/35-44' , 
        '45-54' : 'nisra5/45-54', 
        '55-64' : 'nisra5/55-64', 
        '65-74' : 'nisra5/65-74', 
        '75 and over' : 'nisra5/75-plus' ,
        'All Ages' : 'all',
        'Under 25' : 'nisra5/under-25'            
        }.get(x, x))


# In[127]:


table = table[['Period','Age','Sex','Underlying Cause of Death','Health and Social Care Trust','Measure Type','Value','Unit']]


# In[128]:


tidy = pd.concat([tidy,table])


# In[129]:


tab1 = loadxlstabs(inputFile, sheetids='Table 1')[0]


# In[130]:


cell1 = tab1.filter('Registration Year')
sex = cell1.fill(RIGHT).is_not_blank().is_not_blank().is_not_whitespace() |        cell1.shift(0,1).fill(RIGHT).is_not_blank().is_not_whitespace()
Year = cell1.fill(DOWN).is_not_blank().is_not_whitespace()
allPersons = tab1.filter('All Persons').fill(DOWN).is_not_blank()
observations1 = Year.fill(RIGHT).is_not_blank().is_not_whitespace() - allPersons
Dimensions1 = [
            HDim(Year,'Year',DIRECTLY,LEFT),
            HDim(sex, 'Sex',DIRECTLY,ABOVE),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit','People'),
            HDimConst('Age', 'all'),
            HDimConst('Underlying Cause of Death', 'all-alcohol-related-deaths'),
            HDimConst('Health and Social Care Trust', 'all'),
            #HDim(allPersons, 'All Persons', DIRECTLY, LEFT)
            ]
c2 = ConversionSegment(observations1, Dimensions1, processTIMEUNIT=True)
if is_interactive():
    savepreviewhtml(c2)
table1 = c2.topandas()


# In[131]:


table1['OBS'].replace('', np.nan, inplace=True)
table1.dropna(subset=['OBS'], inplace=True)
table1.rename(columns={'OBS': 'Value'}, inplace=True)
table1['Value'] = table1['Value'].astype(int)


# In[132]:


table1['Period'] = 'year/' + table1['Year'].astype(str).str[0:4]


# In[133]:


table1['Period'] = table1['Period'].map(
    lambda x: {
        'year/Tota' : 'gregorian-interval/2007-01-01T00:00:00/P15Y'       
        }.get(x, x))


# In[134]:


table1['Sex'] = table1['Sex'].map(
    lambda x: {
        'All Persons' : 'T' , 
        'Female' : 'F' , 
        'Male' : 'M', 
        }.get(x, x))


# In[135]:


table1 = table1[['Period','Age','Sex','Underlying Cause of Death','Health and Social Care Trust','Measure Type','Value','Unit']]


# In[136]:


tidy = pd.concat([tidy,table1])


# In[137]:


tab2 = loadxlstabs(inputFile, sheetids='Table 3')[0]


# In[138]:


cell2 = tab2.filter('Underlying Cause (ICD-10 codes)')
Year1 = cell2.fill(RIGHT).is_not_blank().is_not_blank().is_not_whitespace() |        cell2.shift(0,1).fill(RIGHT).is_not_blank().is_not_whitespace()
cd = cell2.fill(DOWN).is_not_blank().is_not_whitespace()
observations3 = Year1.fill(DOWN).is_not_blank().is_not_whitespace()
Dimensions3 = [
            HDim(Year1,'Year',DIRECTLY,ABOVE),
            HDim(cd, 'Underlying Cause of Death',DIRECTLY,LEFT),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit','People'),
            HDimConst('Age', 'all'),
            HDimConst('Sex', 'T'),
            HDimConst('Health and Social Care Trust', 'all')
            ]
c3 = ConversionSegment(observations3, Dimensions3, processTIMEUNIT=True)
if is_interactive():
    savepreviewhtml(c3)
table2 = c3.topandas()


# In[139]:


table2['OBS'].replace('', np.nan, inplace=True)
table2.dropna(subset=['OBS'], inplace=True)
table2.rename(columns={'OBS': 'Value'}, inplace=True)
table2['Value'] = table2['Value'].astype(int)
table2['Period'] = 'year/' + table2['Year'].astype(str).str[0:4]


# In[140]:


table2 = table2[table2['Underlying Cause of Death'] != 'Total deaths from all causes']
table2 = table2[table2['Underlying Cause of Death'] != 'All alcohol related deaths']


# In[141]:


table2['Period'] = table2['Period'].map(
    lambda x: {
        'year/Tota' : 'gregorian-interval/2007-01-01T00:00:00/P10Y'       
        }.get(x, x))
table2['Underlying Cause of Death'] = table2['Underlying Cause of Death'].map(
    lambda x: {
        'Mental and behavioural disorders due to use of alcohol (F10)' : 'f10',
       'Accidental poisoning by and exposure to alcohol (X45)' : 'x45',
       'Intentional self-poisoning by and exposure to alcohol or poisoning by and exposure to alcohol, undetermined intent (X65, Y15)':'x65-y15',
       'All other alcohol related deaths (E24.4, G31.2, G62.1, G72.1, I42.6, K29.2, K70, K85.2, Q86.0, R78.0, K86.0)' : 'all-other-alcohol-related-deaths',
       'All alcohol related deaths': 'all-alcohol-related-deaths'        
        }.get(x, x))


# In[142]:


table2 = table2[['Period','Age','Sex','Underlying Cause of Death','Health and Social Care Trust','Measure Type','Value','Unit']]


# In[143]:


tidy = pd.concat([tidy,table2])


# In[144]:


tab3 = loadxlstabs(inputFile, sheetids='Table 4')[0]


# In[145]:


cell3 = tab3.filter('Registration Year')
hs = cell3.fill(RIGHT).is_not_blank().is_not_blank().is_not_whitespace() |        cell3.shift(0,1).fill(RIGHT).is_not_blank().is_not_whitespace()
Year = cell3.fill(DOWN).is_not_blank().is_not_whitespace()
observations4 = Year.fill(RIGHT).is_not_blank().is_not_whitespace()
Dimensions4 = [
            HDim(Year,'Year',DIRECTLY,LEFT),
            HDim(hs, 'Health and Social Care Trust',DIRECTLY,ABOVE),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit','People'),
            HDimConst('Age', 'all'),
            HDimConst('Underlying Cause of Death', 'all-alcohol-related-deaths'),
            HDimConst('Sex', 'T')
            ]
c4 = ConversionSegment(observations4, Dimensions4, processTIMEUNIT=True)
if is_interactive():
    savepreviewhtml(c4)
table3 = c4.topandas()


# In[146]:


table3['OBS'].replace('', np.nan, inplace=True)
table3.dropna(subset=['OBS'], inplace=True)
table3.rename(columns={'OBS': 'Value'}, inplace=True)
table3['Value'] = table3['Value'].astype(int)
table3['Period'] = 'year/' + table3['Year'].astype(str).str[0:4]


# In[147]:


table3['Period'] = table3['Period'].map(
    lambda x: {
        'year/Tota' : 'gregorian-interval/2007-01-01T00:00:00/P10Y'       
        }.get(x, x))


# In[148]:


table3 = table3[table3['Health and Social Care Trust'] != 'Total']


# In[149]:


table3['Health and Social Care Trust'] = table3['Health and Social Care Trust'].map(
    lambda x: {
        'Belfast': 'belfast', 'Northern': 'northern',
        'South Eastern' : 'south-eastern', 
        ' Southern' : 'southern', 'Western' : 'western'
        }.get(x, x))


# In[150]:


table3 = table3[['Period','Age','Sex','Underlying Cause of Death','Health and Social Care Trust','Measure Type','Value','Unit']]


# In[151]:


if is_interactive():
    destinationFolder = Path('out')
    destinationFolder.mkdir(exist_ok=True, parents=True)
    tidy.to_csv(destinationFolder / ('observations.csv'), index = False)


# In[152]:


from pathlib import Path

out = Path('out')
out.mkdir(exist_ok=True, parents=True)
scraper.dataset.family = 'health'

with open(out / 'dataset.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())
    
csvw = CSVWMetadata('https://gss-cogs.github.io/ref_alcohol/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')


# In[153]:


import pandas as pd
df = pd.read_csv(out / "observations.csv")
df["all_dimensions_concatenated"] = ""
for col in df.columns.values:
    if col != "Value":
        df["all_dimensions_concatenated"] = df["all_dimensions_concatenated"]+df[col].astype(str)
found = []
bad_combos = []
for item in df["all_dimensions_concatenated"]:
    if item not in found:
        found.append(item)
    else:
        bad_combos.append(item)
df = df[df["all_dimensions_concatenated"].map(lambda x: x in bad_combos)]
drop_these_cols = []
for col in df.columns.values:
    if col != "all_dimensions_concatenated" and col != "Value":
        drop_these_cols.append(col)
for dtc in drop_these_cols:
    df = df.drop(dtc, axis=1)
df = df[["all_dimensions_concatenated", "Value"]]
df = df.sort_values(by=['all_dimensions_concatenated'])
df.to_csv("duplicates_with_values.csv", index=False)


# In[ ]:




