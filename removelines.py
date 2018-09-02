import os
import io
import sys
import argparse
import csv
import xml.etree.ElementTree as ET
import logging
               

FILEPATH = "./input"
FIXED_IDS = {'trans-unit', 'id='}

parser = argparse.ArgumentParser(description="Removal of specific elements from XLIFF.")
parser.add_argument("filename", help="Specify a file name, e.g. 'translations.xliff'")
args = parser.parse_args()


def main(args):
    keywordlist = getkeywords()
    itemstatus = elementRemoval(args.filename, keywordlist)
    cleanXmlSyntax(itemstatus)


def getkeywords():
    keywordlist = []
    with open('keywords.csv', newline='') as kw:
        reader = csv.reader(kw, delimiter=' ', quotechar='|')
        for kws in reader:
            keywordlist.append(kws)
       
        for addids in keywordlist:
            addids.extend(FIXED_IDS)   

    return keywordlist


#Remove XLIFF trans-unit elements which contains ids specified in keywords.txt
def elementRemoval(filename, keywordlist):
    founditem = False
    exceptionList = []
    parseexception = False

    try:
        with open(FILEPATH + '/' + filename, 'r', encoding='utf-8') as xliffFile:     
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
                print('Following keyword: "{}" is not unique, please enter the full id in "keywords.csv".'.format(unique))
                
        if(founditem):
            print('Elements has been removed.')
        else:
            print("No items found.")

        tree.write('output.xml', encoding='utf-8')
        return founditem
    

#Cleaning of XML neccessary because ElementTree parser can not handle "URN" namespace included in Krones XLIFF format.
def cleanXmlSyntax(itemstatus):
    if(itemstatus):
        print('Input file processed and saved.')
        with open('output.xml', 'r', encoding='utf-8') as cleanXml:
            xml = cleanXml.read()
        firstclean = xml.replace('<ns0:', '<')
        secondclean = firstclean.replace('</ns0:', '</')      
        newfilename = os.path.join('./output', 'processed_'+args.filename) 

        with open(newfilename, 'w', encoding='utf-8') as cleanedXml:
            cleanedXml.write('<?xml version="1.0" encoding="utf-8"?>\n')
            cleanedXml.write('<xliff xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">\n')
            cleanedXml.write(secondclean[72:])
    else:
        print('No changes detected. Input file was not processed.')



if __name__== "__main__":
    main(args)
    os.remove('output.xml') 

    







    


    


    


    

    




                

                    
