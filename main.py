import time
import re
import random
from nltk.tree import *
from nltk.draw.tree import TreeView
from PhraseBlock import PhraseBlock

stringsToParse = [
    'the man bite the green dog',
    'the man bites the green dog',
    'the man like the green dog',
    'the man likes the green dog',
    'a man bite the green dog',
    'a man bites the green dog',
    'a man like the green dog',
    'a man likes the green dog',
    'the men bite the green dog',
    'the men bites the green dog',
    'the men like the green dog',
    'the men likes the green dog',
    'a men bite the green dog',
    'a men bites the green dog',
    'a men like the green dog',
    'a men likes the green dog',
    'the woman bite the green dog',
    'the woman bites the green dog',
    'the woman like the green dog',
    'the woman likes the green dog',
    'a woman bite the green dog',
    'a woman bites the green dog',
    'a woman like the green dog',
    'a woman likes the green dog',
    'the women bite the green dog',
    'the women bites the green dog',
    'the women like the green dog',
    'the women likes the green dog',
    'a women bite the green dog',
    'a women bites the green dog',
    'a women like the green dog',
    'a women likes the green dog',
]


files = [
    'phrases_breakdowns/adj.txt',
    'phrases_breakdowns/det.txt',
    'phrases_breakdowns/nouns.txt',
    'phrases_breakdowns/verbs.txt'
]

grammical = False

def init_dic():
    names = ['adj', 'det', 'noun', 'verb'] # the possible keys off the lexicon dictionary
    i = 0

    for file in files:
        lines = [line.rstrip('\n') for line in open(file)] # read the lines in our file list
        currentDictEntry = names[i] # the key to the dictionary
        phrases[currentDictEntry] = [] # add empty array for the word entries

        for line in lines: # loop through the words
            if '(s)' in line:       # if its the singular version of the word
                if currentDictEntry + '(s)' not in phrases:
                    phrases[currentDictEntry + '(s)'] = [] # add the dictionary key if not present
                phrases[currentDictEntry + '(s)'].append(re.sub(r'\(s\)', '', line)) # add word to lexicon
            elif '(p)' in line: # for the plural
                if currentDictEntry + '(p)' not in phrases:
                    phrases[currentDictEntry + '(p)'] = []
                phrases[currentDictEntry + '(p)'].append(re.sub(r'\(p\)', '', line))
            else:
                phrases[currentDictEntry].append(line)
        i += 1

def bottomUpApproach(sentence): # starting at the sentence form of the sentence

    grammicalTill = checkMassAgreement(sentence.split(' '))

    if grammicalTill == 3:
        words = str.split(sentence, ' ') # split to an array to process
    else:
        words = sentence.split(' ')[:grammicalTill + 1]

    taggedWords = []

    # this loop is responsible for tagging the words to their type, eg verb
    for word in words:
        for pKey in phrases: # searches for the entry in the dictionary
            tag = pKey
            if word in phrases[pKey]: # if we find the word in the dictonary
                if '(p)' in pKey:
                    tag = re.sub(r'\(p\)', '', pKey) # we want to remove the plural and singular tags as its not important for this processing
                elif '(s)' in pKey:
                    tag = re.sub(r'\(s\)', '', pKey)

                phraseBlock = PhraseBlock(tag) # create a phrase block object
                phraseBlock.phrases.append(word) # add the word to that phrase array. in the first instance of processing. phrase array will just contain the word.
                taggedWords.append(phraseBlock) # add to the tagged words

    parseTaggedWords(taggedWords) # up to the next level of processing


def checkMassAgreement(sentence):
    words_to_check = sentence[0:3] # in our program, the first 3 words are the ones that dicate the agreement
    pValue = 0 # mass value 1 = singular, 2 = plural, 0 = unprocessed, 0 in first iteration or in case of the word 'the'
    grammicalCount = 0 # number of words that are grammical

    for word in words_to_check: # check each word in the sentence
        if word == 'the': # the word 'the' can be used for the singular or plural nouns, we want to skip this iteration
            grammicalCount += 1
            continue

        for pKey in phrases: # this is the dictonaray and pkey is the key
            if word not in phrases[pKey]: # checks value in that index
                continue

            if '(p)' in pKey: # we have a plural
                if pValue == 1: # but if we have set the sentence to be singular, its not an agreement, bail out of the loop. Its failed.
                    return grammicalCount
                grammicalCount += 1
                    #return False
                pValue = 2 # set the value to be plural
            else: # other case, which can be singural only
                if pValue == 2: # we have a plural, bail out and fail
                    return grammicalCount
                grammicalCount += 1
                    #return False
                pValue = 1 # set the value to be singular

    global grammical
    grammical = True

    return grammicalCount

def getRules():
    rules = [line.rstrip('\n') for line in open('phrases_breakdowns/rules.txt')] # find the rules file
    ruleArray = [] # the array that will contain rules

    for rule in rules:
        tagStart = rule.find('[') + 1 # find the brackets of the tag
        tagFinish = rule.find(']')
        key = rule[tagStart: tagFinish] # the rule key
        allowedTypes = rule[tagFinish + 1:] # get the rule
        ruleArray.append(Rule(key, allowedTypes)) # add a rule object to the array

    return ruleArray


def parseTaggedWords(phraseBlocks):
    rules = getRules() # get the rules
    index = 0
    temp_rules = rules[:] # this method works by as the rules dont match the tags, it removes that rule. We need to have a temp rule array and not lose rules for each iteration
    processing_tag = '' # string of tags for rule comparsion
    last_unfound_index = 0 # the index of the word that has not been found yet
    next_level = [] # the next phraseblocks

    while index < len(phraseBlocks): # while we have phrases to process
        current_word = phraseBlocks[index] # get the word that is the start point of the search
        processing_tag += current_word.tag + ' ' # add a tag to the processing tags string

        for rule in temp_rules: # loop through rules
            if processing_tag[: -1] not in rule.word: # the current rule doesnt match the current tag, remove it for next iteration
                temp_rules.remove(rule)

            if processing_tag[:-1] == rule.word: # we found our rule
                processing_tag = '' # reset the processing tag
                phraseBlock = PhraseBlock(rule.tag) # create the block with the rule tag that fits
                for i in range(last_unfound_index, index + 1): # loop through the phraseblocks that are included in the processing tags
                    phraseBlock.phrases.append(phraseBlocks[i]) # add them to the array
                next_level.append(phraseBlock) # add to the next level array for further processing
                last_unfound_index = index + 1 # start the loop at the next word that has to be processed
                temp_rules = rules[:] # reset the rules
                break # break out of the loop for the rules

        if len(temp_rules) == 0: # we have no rules left
            processing_tag = '' # remove the tags
            temp_rules = rules[:] # reset the rules
            next_level.append(phraseBlocks[last_unfound_index]) # add the failed check to the next level for search as the tag is probabily combined with other tags in a rule
            index = last_unfound_index + 1 # start the search at next word
            last_unfound_index = index # change the last unfound
        else:
            index += 1 # we have rules left, add the next phrase with the current and search

    if len(next_level) > 1: # we still are not at the root element of senctence, recursive function call
        parseTaggedWords(next_level)
    else:
        formatString(next_level) # all have been processed, print the string
        time.sleep(1)

        if grammical:
            print('\nPhrase is grammical : Showing tree')
            drawTree(next_level) # draw the phrase tree
        else:
            print('\nPhrase is not grammical.')


def formatString(phrases):
    print(phrases[0].formatString(), end=' ') # print the string with all the tags

def drawTree(phrases):
    t = Tree(phrases[0].tag, phrases[0].getChildNodes()) # create tree, call the children to get their trees
    t.draw() # draw the tree

class Rule:
    def __init__(self, tag, word):
        self.tag = tag
        self.word = word


phrases = {}
init_dic()
iterNum = 0

sentence = stringsToParse[random.randint(0, len(stringsToParse))]
print('Parsing the sentence : ' + sentence)
bottomUpApproach(sentence)
print()








