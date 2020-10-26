import fileinput
import pandas as pd
import sys

tabNames = ['PC_Time2014', 'PC_Time2015', 'PC_Time2016',
            'PC_Time2017', 'PC_Time2018']

allTabNames = ['PC_Time2014', 'PC_Time2015', 'PC_Time2016',
               'PC_Time2017', 'PC_Time2018', 'Circuit_Sector',
               'PC_Circuit']

sectorNames = ['S12', 'S23', 'S34', 'S45', 'S56', 'S67', 'S78', 'S81']

#Filtered data lists
filteredCircuits = [[], []]
filteredPC = [[], []]
filteredData = []

#Skipped lines counter
skippedRows = 0

#Number of rows
correctRows = {'PC_Time2014' : 0, 'PC_Time2015' : 0, 
            'PC_Time2016': 0, 'PC_Time2017' : 0,
            'PC_Time2018' : 0}
allRows = {'PC_Time2014' : 0, 'PC_Time2015' : 0, 
            'PC_Time2016': 0, 'PC_Time2017' : 0,
            'PC_Time2018' : 0}

#############################################################

def removeDuplicatesFromCSV(pathIn, pathOut):
    df = pd.read_csv(pathIn)
    firstColumn = df.columns[0]
    df = df.drop([firstColumn], axis=1)
    df.to_csv(pathOut, index=False)
    df = pd.read_csv(pathOut).drop_duplicates(keep='first')
    df.to_csv(pathOut, index=False)

def circuitFilter(pathIn, circuitsBySector):
    for line in fileinput.FileInput(pathIn, inplace=1):
        sectorData = line.split(',')
        print(line, end = '')
        if sectorData[2] in sectorNames:
            circuitsBySector[0].append(sectorData[1])  
            circuitsBySector[1].append(sectorData[2])

def pcFilter(pathIn, circuitsBySector, pcByCircuit):
    skippedRows = 0
    for line in fileinput.FileInput(pathIn, inplace=1):
        circuitData = line.split(',')
        if circuitData[0] not in circuitsBySector[0]:
            skippedRows += 1
            continue
        else:
            pcByCircuit[1].append(circuitsBySector[1][circuitsBySector[0].index(circuitData[0])])
        namePC = circuitData[2]
        namePC = namePC[:-1]
        pcByCircuit[0].append(namePC) 
        print(line, end = '') 
    print('Circuit validation, number of skipped: ', skippedRows)

#############################################################

#Selecting years and sector (will be replaced by gui)
def diff(first, second):
        second = set(second)
        return [item for item in first if item not in second]
txtIn = ''
while txtIn != 'x':
    print('Selected sectors: ', sectorNames)
    #print('Selected years: ', dataTabs)
    txtIn = input("Type names of sector to remove it from the list or type 'x' to exit.")
    sectorsToRemove = txtIn.split(',')
    sectorNames = diff(sectorNames, sectorsToRemove)
    if len(sectorNames) == 0:
        print('All sectors removed...')
        sys.exit()
txtIn = ''
while txtIn != 'x':
    print('Selected years: ', tabNames)
    #print('Selected years: ', dataTabs)
    txtIn = input("Type years to remove it from the list or type 'x' to exit.")
    yearsToRemove = txtIn.split(',')
    tabNames = diff(tabNames, yearsToRemove)
    allTabNames = diff(allTabNames, yearsToRemove)
    if len(tabNames) == 0:
        print('All years removed...')
        sys.exit()


#Removing duplicates
for tab in allTabNames:
    removeDuplicatesFromCSV('./Dane/' + tab + '.csv', './Dane/Po/' + tab + '.csv')
    print(tab + ' - duplicates removed')

#Saving circuits from selected sectors
circuitFilter('./Dane/Po/Circuit_Sector.csv', filteredCircuits)

#Saving PCs from available circuits
pcFilter('./Dane/Po/PC_Circuit.csv', filteredCircuits, filteredPC)

#Getting data from all PC_Time csv files
for tab in tabNames:
    for line in fileinput.FileInput('./Dane/Po/' + tab + '.csv', inplace=1):
        allRows[tab] += 1
        tabData = line.split(',')
        if tabData[0] not in filteredPC[0]:
            skippedRows += 1
            continue
        else:
            correctRows[tab] += 1
            line = line[:-1]
            line += ',' + tab
            sectorName = filteredPC[1][filteredPC[0].index(tabData[0])]
            line += ',' + sectorName + '\n'
        filteredData.append(line)
        print(line, end = '')
        
    print(tab, 'validation, number of skipped: ', skippedRows)
    skippedRows = 0

print('Data saved.')

for tab in tabNames:
    print('Number of all lines in ', tab, ': ', allRows[tab])
    print('Number of correct lines in ', tab, ': ', correctRows[tab])
    print('Number of removed lines in ', tab, ': ', allRows[tab] - correctRows[tab])
    print('Percentage of valid lines in', tab, ': ', round((correctRows[tab] / allRows[tab]), 4) * 100, '%')
