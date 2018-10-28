import os
import io
import sys
import argparse
import csv
import xml.etree.ElementTree as ET
import logging
               

#FILEPATH = "./input"
#FILEPATH_DUPLICATE_CSV = 
FIXED_IDS = {'trans-unit', 'id='}
FIRST_TEMP_OUTPUT = 'output.xml', 'duplicateoutput.xml'
DUPLICATES_CSV = 'duplicate_keywords.csv'
OUTPUT_PREFIX = 'processed_', 'removedDuplicates_'

parser = argparse.ArgumentParser(description="Removal of specific elements from XLIFF.")
parser.add_argument("filename", help="Specify a file name, e.g. 'translations.xliff'")
args = parser.parse_args()


def main(args):
    #First part of the program. Removal of keyword elements from XLIFF.
    keywordlist = getkeywords('keywords.csv') 
    itemstatus, tree = elementRemoval('./input',args.filename, keywordlist, FIRST_TEMP_OUTPUT[0])
    outputName = cleanXmlSyntax(itemstatus, FIRST_TEMP_OUTPUT[0], OUTPUT_PREFIX[0])
    ##########################################################
    #Second part of the program. Removal of duplicates for sending to translations.
    sourceValues, elementids = getSourceValues(itemstatus, tree)
    listOfDuplicates = findDuplicates(sourceValues, elementids)
    duplicateIdFile(listOfDuplicates, DUPLICATES_CSV)
    secondKeyWordList = getkeywords(DUPLICATES_CSV)
    elementRemoval('./output', outputName, secondKeyWordList, FIRST_TEMP_OUTPUT[1])
    #FIXME: Escape spaces in
    #print(outputName)
    



def getkeywords(csvfile):
    keywordlist = []
    with open(csvfile, newline='') as kw:
        reader = csv.reader(kw, delimiter=' ', quotechar='|')
        for kws in reader:
            keywordlist.append(kws)
       
        for addids in keywordlist:
            addids.extend(FIXED_IDS)   

    return keywordlist


def duplicateIdFile(duplicateIds, duplicatesCsvName):
    #1. Create csv file
    with open(duplicatesCsvName, 'w', encoding='utf-8') as dup:
        for line in duplicateIds:
            dup.write('{}\n'.format(line))



#Remove XLIFF trans-unit elements which contains ids specified in keywords.txt
def elementRemoval(filepath, filename, keywordlist, tempOutput):
    founditem = False
    exceptionList = []
    parseexception = False

    try:
        with open(filepath + '/' + filename, 'r', encoding='utf-8') as xliffFile:     
            tree = ET.parse(xliffFile)  


    except ET.ParseError as err:
        parseexception = True
        print('XML syntax error. See error_syntax.log for more information.')
        with open('error_syntax.log', 'w') as error_log_file:
            error_log_file.write(str(err))
         
    if not parseexception:
        root = tree.getroot()
        #find all trans-unit elements, outgoing from document root    
        for file in root.findall('.//{urn:oasis:names:tc:xliff:document:1.2}file/'):
            for transunit in file.findall('./{urn:oasis:names:tc:xliff:document:1.2}trans-unit'):
                elementids = transunit.get('id')                          
                #check keywords from keywords.txt 
                for keywords in keywordlist:       
                    print(len(keywords))
                    #TODO: Check for ids with spaces in keywordlist       
                    for word in keywords:                        
                        if(word in elementids):                           
                            founditem = True
                            #print('Word: "{}"; ElementIDs: "{}"; Found Item: "{}"'.format(word, elementids, founditem))
                            #check if found words in keywords.txt are sufficiently described in order to identify trans-unit distinctly. 
                            try: 
                                #remove corresponding element from document roo
                                file.remove(transunit)
                            except:
                                print('Word: "{}"; ElementIDs: "{}"; Found Item: "{}"'.format(word, elementids, founditem))
                                logging.exception("Fatal error")
                                if(word not in exceptionList):
                                    exceptionList.append(word)
                                
        #if keywords.txt does contain not sufficiently described keywords, state them 
        if(exceptionList):
            founditem = False
            for unique in exceptionList:
                print('Following keyword: "{0}" is not unique, please enter the full id in "keywords.csv".'.format(unique))
                
        if(founditem):
            print('Elements has been successfully removed.')
        else:
            print("No items found.")

        tree.write(tempOutput, encoding='utf-8')
        #print("Founditem {}".format(founditem))
        return founditem, tree


def getSourceValues(itemstatus, tree):
    if(itemstatus):
        sourceTexts = []
        elementids = []
        #get all xliff <source> values
        root = tree.getroot()
        for file in root.findall('.//{urn:oasis:names:tc:xliff:document:1.2}file/'):
            for transunit in file.findall('./{urn:oasis:names:tc:xliff:document:1.2}trans-unit'):
                elementids.append(transunit.get('id'))
                for source in transunit.findall('{urn:oasis:names:tc:xliff:document:1.2}source'):
                    sourceTexts.append(source.text)
    #print(sourceTexts)
    #print(elementids)
    return sourceTexts, elementids


def findDuplicates(sourceValues, elementids):
    seen = {}
    duplicates = []
    idIndex = []
    duplicateIds = []    
    duplicateCount = 0

    print("Find duplicate elements in already processed file.")
    for value in sourceValues:
        if value not in seen:
            seen[value] = 1
        else:
            if seen[value] == 1:
                duplicates.append(value)     
                idIndex.append(sourceValues.index(value))
                duplicateCount +=1
            seen[value] +=1

    counter = 0
    for i in idIndex:
        duplicateIds.append(elementids[i])
        counter += 1
        #print("{0} id: {1}".format(counter,elementids[i]))
    print("Found '{}' duplicates.".format(duplicateCount))
    return duplicateIds


def findIdSpaces(keywordlist):
    listLength = len(keywordlist)



    return spacefreeKeywordIds  


#Cleaning of XML neccessary because ElementTree parser can not handle "URN" namespace included in Krones XLIFF format.
def cleanXmlSyntax(itemstatus, tempoutput, outputPrefix):
    if(itemstatus):
        print('Input file processed and saved.')
        with open(tempoutput, 'r', encoding='utf-8') as cleanXml:
            xml = cleanXml.read()
        firstclean = xml.replace('<ns0:', '<')
        secondclean = firstclean.replace('</ns0:', '</')      
        newfilename = os.path.join('./output', outputPrefix + args.filename) 
        nameWithoutPath = (outputPrefix + args.filename)

        with open(newfilename, 'w', encoding='utf-8') as cleanedXml:
            cleanedXml.write('<?xml version="1.0" encoding="utf-8"?>\n')
            cleanedXml.write('<xliff xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">\n')
            cleanedXml.write(secondclean[72:])
    else:
        print('No changes detected. Input file was not processed.')

    return nameWithoutPath        



if __name__== "__main__":
    main(args)
    os.remove(FIRST_TEMP_OUTPUT[0]) 

    







    


    


    


    

    




                

                    
