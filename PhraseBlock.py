from nltk.tree import *

class PhraseBlock:

    def __init__(self, tag):
        self.tag = tag
        self.phrases = []

    def formatString(self):

        if len(self.phrases) == 0: # if we have a phrase with a length of 0, bail
            return

        formatted_string = self.tag # get the phrase tag

        for p in self.phrases: # get the phrases in the block
            if isinstance(p, str): # if its a string, its the last in the line
                formatted_string += '[' + p + ']' # return the phrase we have
                return formatted_string
            else:
                formatted_string += '[' + p.formatString() + ']' # else get the child phrases

        return  formatted_string

    def getChildNodes(self):

        childNodes = []

        for phrase in self.phrases:
            if len(phrase.phrases) > 1: # if we have a children, recursive get nodes
                childNodes.append(Tree(phrase.tag, phrase.getChildNodes()))
            else :
                childNodes.append(Tree(phrase.tag, [phrase.phrases])) #  else return the last child in the line

        t = Tree(self.tag, []) # create subtree

        for child in childNodes: # append children to the tree
            t.append(child)

        return t
