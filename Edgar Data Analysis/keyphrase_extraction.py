#Import required libraries
import rake_nltk
import operator
from pymongo import MongoClient
import pprint

'''
This script will read the bold list and para list from MondoDB of documents from 
MondoDB collection. Then it finds key-phrases and storing back into same collection
'''

# Extracting key-phrases using rake library
def extractKeyPhrase(phrase):
    rake_object = rake_nltk.Rake( )

    rake_object.extract_keywords_from_text( phrase )

    # print(rake_object.get_ranked_phrases())
    exctractedKeyphrase = rake_object.get_ranked_phrases_with_scores( )
    return exctractedKeyphrase


# Setting up MongoDB Client
client = MongoClient( 'localhost', 27017 )	# accesing Mongo DB clinet running on 27017 port of local host
db = client['Capstone']		# Accessing Capstone database
table = db['RawData']		# Accessing RawData Collection where 10-K sectionalized data is stored


cursor = table.find()	

# Looping through each documents of the collection
for doc in cursor:
    keyphrase_para_list = []  #stores key-phrases of each paragraph
	
	# Extracting key-phrases of all paras and updating it into same collection
    for para in doc["Para List"]:
        para_keyphrases = ""
        if para:
            keyphrases = extractKeyPhrase(para)
            for p,j in keyphrases[0:5]:
                para_keyphrases += j + " | "
        keyphrase_para_list.append(para_keyphrases)
    print(keyphrase_para_list)

    db.get_collection('RawData').update({"_id": doc["_id"]},{"$set": {"Para Keyphrases": keyphrase_para_list}})

	# Extracting key-phrases of all bold text and updating it into same collection
    keyphrase_bold_list = []	#stores key-phrases of each bold text
    for boldText in doc["Bolds"]:
        bold_keyphrases = ""
        if boldText:
            keyphrases = extractKeyPhrase( boldText )
            for p, j in keyphrases[0:5]:
                bold_keyphrases += j + " | "
        keyphrase_bold_list.append( bold_keyphrases )
    print( keyphrase_bold_list )

    db.get_collection( 'RawData' ).update( {"_id": doc["_id"]}, {"$set": {"Bold Keyphrases": keyphrase_bold_list}} )

