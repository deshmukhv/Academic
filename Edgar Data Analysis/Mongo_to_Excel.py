from pymongo import MongoClient
from bs4 import BeautifulSoup
import html2text

def mongo_excel():
    result = {}

    client = MongoClient( 'localhost', 27017 )
    db = client['Capstone']
    table = db['RawData']
    # fp = open("outputMongo.csv", "w", encoding="utf-8")
    for d in table.find():
        fp = open(d['Company Name'] + "_" +d['Date']+"_output.csv", "w", encoding="utf-8")

        fp.write('CIK' +  "," + 'Company Name' +  "," + 'Date' +  "," +  'Form Type' + "," + 'Risk Factor Bold Tags' +  "," + 'Risk Factor Paragraphs' +  "," + 'Category for Risk Factor' +  "," + 'Business Bold Tags' + "," +  'Business Paragraphs'+ "," + 'Category for Business' +"\n")
        fp.write(str(d['CIK']) +  "," +  d['Company Name'] +  "," +  d['Date'] +  "," +  d['Form Type'] + "," +  "," +  "," +  "," + "\n")
        # print(d['CIK'], ",", d['Company Name'], ",", d['Date'], ",", d['Form Type'], ",", soup.text.strip())


        rbolds = d['Risk Factor Bold Tags']
        rparas = d['Risk Factor Paragraphs']
        bbolds = d['Business Bold Tags']
        # print(bbolds)
        bparas = d['Business Paragraphs']

        maxIndex = max(len(rbolds), len(bbolds))

        for i in range(0, maxIndex):
            wStr = "," +  "," +  "," +  ","

            if len(rbolds) > i:
                wStr += "\"" + rbolds[i].strip().replace("\t", " ").replace(",", ";").replace("\n", " ").replace('\r', '') + "\"" + "," + "\"" + rparas[i].strip().replace("\t", " ").replace(",", ";").replace("\n", " ").replace('\r', '') + "\"" + ", " + ", "
            else:
                wStr += "," + ","

            if len(bbolds) > i:
                wStr += "\"" + bbolds[i].strip().replace("\t", " ").replace(",", ";").replace("\n", " ").replace('\r', '') + "\"" + "," + "\"" + bparas[i].strip().replace("\t", " ").replace(",", ";").replace("\n", " ").replace('\r', '') + "\"" + ", "
            else:
                wStr += "," + ","

            # print(wStr)
            fp.write(wStr + "\n")
        fp.close()
mongo_excel()