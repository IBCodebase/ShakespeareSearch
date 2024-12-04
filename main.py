import json
import requests
import re
import pandas as pd
import matplotlib.pyplot as plt

#questions to answer:
#which play has the most novel words used (words used only once)
#how do plays compare in most frequently used words?

#----------------------------------scraping/processing into json----------------


def removeLegalNotice(text):
    #there is a chunky legal notice peppered throughout the source text
    return text.replace("<<THIS ELECTRONIC VERSION OF THE COMPLETE WORKS OF WILLIAM\nSHAKESPEARE IS COPYRIGHT 1990-1993 BY WORLD LIBRARY, INC., AND IS\nPROVIDED BY PROJECT GUTENBERG ETEXT OF ILLINOIS BENEDICTINE COLLEGE\nWITH PERMISSION.  ELECTRONIC AND MACHINE READABLE COPIES MAY BE\nDISTRIBUTED SO LONG AS SUCH COPIES (1) ARE FOR YOUR OR OTHERS\nPERSONAL USE ONLY, AND (2) ARE NOT DISTRIBUTED OR USED\nCOMMERCIALLY.  PROHIBITED COMMERCIAL DISTRIBUTION INCLUDES BY ANY\nSERVICE THAT CHARGES FOR DOWNLOAD TIME OR FOR MEMBERSHIP.>>", "")

def cleanUp(text):
    #this will turn the big chunk of text into something usable
    #remove legal notice is already called in getCompleteWorksOfShakespeare()!
    list =text.replace("!", " ").replace("]", "").replace("[", "").replace(".", " ").replace("(","").replace(")","").replace(",", " ").replace("\n", " ").replace(";"," ").replace("?", " ").replace("\""," ").split(" ")
    filtered_list = [item for item in list if item != ""]
    lower_list = [word.lower() for word in filtered_list]
    return lower_list

def getCompleteWorksOneString():
    #this one comes pre-cleaned up
    url = "https://ocw.mit.edu/ans7870/6/6.006/s08/lecturenotes/files/t8.shakespeare.txt"
    response = requests.get(url)

    return cleanUp(removeLegalNotice(response.text).split("DOWNLOAD TIME OR FOR MEMBERSHIP.>> ")[1])

def getCompleteWorksOfShakespeare():
    #that's an awfully funny function name
    #this now returns a list that has the text split roughly, DO NOT USE FOR MAIN CALCS, YOU WILL GET LOST IN THE SAUCE
    #the list is broken up by areas that are convenient for scraping, but this method does not produce clean data
    url = "https://ocw.mit.edu/ans7870/6/6.006/s08/lecturenotes/files/t8.shakespeare.txt"
    response = requests.get(url)
    return removeLegalNotice(response.text).split("DOWNLOAD TIME OR FOR MEMBERSHIP.>> ")[1].split("THE END")[:-1]

def getPlayName(text):
    return re.sub(r"\d", "", text.split("by William Shakespeare")[0]).replace("\n","")

def getPlayText(text):
    return text.split("by William Shakespeare")[1]

def createItemizedJson():
    #the json is called data.json
    #it contains a dictionary with each play as the key, and a list containing the cleaned words as the value
    #i decided to keep newlines in to preserve some sentence structure (considering all punctuation has been removed
    #I'm assuming anyone looking at this is skilled enough to remove them if you so wish

    playDict = getPlayDict()
    for play in playDict:
        playDict[play] = cleanUp(playDict[play])
    with open("data.json", "w") as file:
        json.dump(playDict, file, indent=4)

def getPlayDict():
    #this returns a dictionary with the play name as the key, and the tokenized list of words as the value
    playDict = {}
    for play in getCompleteWorksOfShakespeare():
        playDict[getPlayName(play)] = getPlayText(play)
    return playDict

#-------------------------------------------------------------------------------
#----------------------------------------analysis tools-------------------------


def getFrequency(textArray):
    # this takes an array of text, then returns a dictionary with each word as the key, and the num of times used as
    # the value

    wordMap = {}
    for word in textArray:
        if wordMap.__contains__(word):
            wordMap[word] = wordMap[word] + 1
        else:
            wordMap.update({word: 1})
    return(wordMap)

def swapKeyAndValue(textDict):
    #take a guess
    #jk, it swaps the key and value
    newDict ={}
    for key in textDict:
        newDict[textDict.get(key)] = key
    return newDict


def findNumUniqueWords():
    #finds the number of unique words in each play
    playDict = jsonToDict()

    for play in playDict:
        frequencyDict = getFrequency(playDict[play])
        counter = 0
        for word in frequencyDict:
            if frequencyDict[word] == 1:
                counter = counter + 1
        playDict[play] = counter
        counter = 0
    return playDict

def findNumWords():
    playDict = jsonToDict()
    counter = 0
    for play in playDict:
        for word in playDict[play]:
            counter = counter + 1
        playDict[play] = counter
        counter = 0
    return playDict

def findPercentUniqueWords():
    playDictUnique = findNumUniqueWords()
    playDictTotal = findNumWords()
    for play in playDictUnique:
        playDictUnique[play] = round(float(playDictUnique[play])/float(playDictTotal[play]) * 100, 3)
    return playDictUnique

def findMostFrequentWords():
    wordDict = getFrequency(getCompleteWorksOneString())
    return dict(sorted(wordDict.items(), key=lambda item: item[1], reverse=True))

def findTop100Words():
    #I know this is a jank method, give me a break it works fine
    wordDict = findMostFrequentWords()
    newDict = {}
    counter = 0
    for word in wordDict:
        if counter == 100:
            break
        newDict[word] = wordDict[word]
        counter = counter + 1
    return newDict
#-------------------------------------------------------------------------------------
#---------------------------graphing--------------------------------------------------
def numUniqueWordsGraph():
    word_counts = findNumUniqueWords()

    df = pd.DataFrame(list(word_counts.items()), columns=['Work', 'Word Count'])

    df = df.sort_values(by='Word Count', ascending=False)

    plt.figure(figsize=(15, 8))  # Adjust size for readability
    df.plot(kind='bar', x='Work', y='Word Count', legend=False, ax=plt.gca())

    plt.title('One Use Word Count in Shakespeare\'s Works')
    plt.xlabel('Work')
    plt.ylabel('Word Count')
    plt.xticks(rotation=90)
    plt.tight_layout()

    plt.show()

def percentUniqueWordsGraph():
    word_counts = findPercentUniqueWords()

    df = pd.DataFrame(list(word_counts.items()), columns=['Work', 'Word Count'])

    df = df.sort_values(by='Word Count', ascending=False)

    plt.figure(figsize=(15, 8))  # Adjust size for readability
    df.plot(kind='bar', x='Work', y='Word Count', legend=False, ax=plt.gca())

    plt.title('Percentage of one-use words in Shakespeare\'s Works')
    plt.xlabel('Work')
    plt.ylabel('Percent')
    plt.xticks(rotation=90)
    plt.tight_layout()

    plt.show()

def top100WordsGraph():
    word_counts = findTop100Words()

    df = pd.DataFrame(list(word_counts.items()), columns=['Word', 'Times Used'])

    df = df.sort_values(by='Times Used', ascending=False)

    plt.figure(figsize=(15, 8))  # Adjust size for readability
    df.plot(kind='bar', x='Word', y='Times Used', legend=False, ax=plt.gca())

    plt.title('Top 100 words in Shakespeare\'s Works')
    plt.xlabel('Word')
    plt.ylabel('Times Used')
    plt.xticks(rotation=90)
    plt.tight_layout()

    plt.show()
#-------------------------------------------------------------------------------
#---------------------------------------reading json----------------------------
def jsonToDict():
    with open('ShakespeareSearch/data.json', 'r') as file:
        data = json.load(file)
        return data
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    #percentUniqueWordsGraph()
    #createItemizedJson()
    top100WordsGraph()
    #numUniqueWordsGraph()

