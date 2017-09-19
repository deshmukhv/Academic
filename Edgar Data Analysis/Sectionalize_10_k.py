#Import required libraries
from bs4 import BeautifulSoup
import os
import re
import html2text
from pymongo import MongoClient
'''
This python script reads the 10-K html file and fetches Risk Factors and Business Sections.
It stores start and end index of both sections and retrieve html content from it. Once this data is found, this script
then extract all bold lines and text under it in the list object. Then it saves these information in MongoDB
database for further analysis. This script also evaluates the result by calculating accuracy using
number of records processed and failed.
'''

#Global Variable Declaration
total_files_processed = 0
total_files_passed = 0
total_files_failed = 0
total_files_no_data = 0
total_bussiness_section_passed = 0
total_bussiness_section_failed = 0
total_risk_section_passed = 0
total_risk_section_failed = 0

#This function calculates the overall accuracy of the 10-K forms
def print_statistics():
    global total_files_processe
    global total_files_passed
    global total_files_failed
    global total_files_no_data
    global total_bussiness_section_passed
    global total_bussiness_section_failed
    global total_risk_section_passed
    global total_risk_section_failed

    log_print_statments("\n")
    log_print_statments("\n")
    log_print_statments("\n")
    log_print_statments("********************Evaluation Report********************\n")
    try:
        #Calculating Accuracy of sectionalizing 10-K forms
        log_print_statments("Total 10-k Processed : " +  str(total_files_processed))
        log_print_statments("Total 10-k Passed : " + str(total_files_passed))
        log_print_statments("Total 10-k Failed : " + str(total_files_failed))
        log_print_statments("Total 10-k with no Data : " + str(total_files_no_data))
        log_print_statments("10-k Overall Accuracy :" +
                            str(total_files_passed / (total_files_processed - total_files_no_data) * 100))
        log_print_statments("\n")

        log_print_statments("Total Bussiness Sections extracted: " + str(total_bussiness_section_passed))
        log_print_statments("Total Bussiness Sections extraction failed: " + str(total_bussiness_section_failed))
        log_print_statments("10-k Bussiness Sections Accuracy :" + str(total_bussiness_section_passed / (
        total_bussiness_section_passed + total_bussiness_section_failed) * 100))
        log_print_statments("\n")

        log_print_statments("Total Risk Sections extracted: " + str(total_risk_section_passed))
        log_print_statments("Total Risk Sections extraction failed: " + str(total_risk_section_failed))
        log_print_statments("10-k Risk Sections Accuracy :" +
                            str(total_risk_section_passed / (total_risk_section_passed + total_risk_section_failed) * 100))
        log_print_statments("\n")
    except Exception as ex:
        log_print_statments("Exception in " + str(ex))


#Opening log text file in append mode to wirte statistics, file name and errors
log_fp = open("log.txt", "a")

#Write the statements into log file
def log_print_statments(statment):
    global log_fp
    log_fp.write(str(statment) + "\n")

# Splitting html content by space, then formating text and merging it back
def formatHTMLForSpace(html):
    lines = html.split(" ")
    formatedLines = ""
    for l in lines:
        if l.strip() is not "":
            formatedLines += l.strip() + " "
    return formatedLines


# log_print_statments list items on new lines with ------------------- seprator
def log_print_statmentsList(items):
    for i in items:
        log_print_statments(str(i) + "\n ------------------- ")
		
'''
Takes the HTML data as input and divide it into diferent paragraphs based on Bold Tags in the HTML and 
return the list of Bold Tags and list of corresponding Pargraphs
'''
def get_bold_and_para_lists(html_data):

	
    webText = html2text.html2text(html_data)
	
	#Removing special characters
    webText = re.sub( '[^A-Za-z0-9.,?!%()$&]+', ' ', webText )
    webText.replace(" amp ", " & ")
    soup = BeautifulSoup(html_data, "html.parser")

    bTags = []

	# Separating bold tags by checking different ways of using bold tags in html file
    for i in soup.findAll('b'):
        if  re.sub('[^A-Za-z0-9.,?!%()$&]+', ' ', i.text.strip( ))  is not "":
            bTags.append(i)

    if len(bTags) == 0:
         for i in soup.findAll('p', style=re.compile(r'font-weight:bold.*?')):
             if re.sub( '[^A-Za-z0-9.,?!%()$&]+', ' ', i.text.strip( ) ) is not "":
                 bTags.append(i)

    if len( bTags ) == 0:
        for i in soup.findAll( 'font', style=re.compile( r'font-weight:bold.*?' ) ):
            if re.sub( '[^A-Za-z0-9.,?!%()$&]+', ' ', i.text.strip( ) ) is not "":
                bTags.append(i)

    if len( bTags ) == 0:
        for i in soup.findAll( 'div', style=re.compile( r'FONT-WEIGHT: bold.*?' ) ):
            if re.sub( '[^A-Za-z0-9.,?!%()$&]+', ' ', i.text.strip( ) ) is not "":
                bTags.append(i)
    if len( bTags ) == 0:
        for i in soup.findAll( 'div', style=re.compile( r'font-weight:bold.*?' )):
            if re.sub( '[^A-Za-z0-9.,?!%()$&]+', ' ', i.text.strip( ) ) is not "":
                bTags.append(i)
    if len( bTags ) == 0:
        for i in soup.findAll( 'font', style=re.compile( r'FONT-WEIGHT: bold.*?' )):
            if re.sub( '[^A-Za-z0-9.,?!%()$&]+', ' ', i.text.strip( ) ) is not "":
                bTags.append(i)
    if len( bTags ) == 0:
        for i in soup.findAll( 'font', style=re.compile( r'font-weight:bold.*?' )):
            if re.sub( '[^A-Za-z0-9.,?!%()$&]+', ' ', i.text.strip( ) ) is not "":
                bTags.append(i)
    if len( bTags ) == 0:
        for i in soup.findAll( 'font', style=re.compile( r'font-weight: bold.*?' )):
            if re.sub( '[^A-Za-z0-9.,?!%()$&]+', ' ', i.text.strip( ) ) is not "":
                bTags.append(i)

    startind = []
	
	# storing start and end index of the bold tags in html file
    for i in range(0, len(bTags)):
        try:
            startind.append([html_data.index(str(bTags[i])), html_data.index(str(bTags[i])) + len(str(bTags[i]))])
        except Exception as inst:
            log_print_statments(inst)
            log_print_statments("Excption in btags: " + str(bTags[i]))

    finalST = []
    i = 0

    merged_btags = []

	# If end index of the current bold tag is same as start index of next tag, then merge it into current index.
    while(i < len(startind ) - 1):
        finalST.append(startind[i][0])
        if startind[i][1] == startind[i + 1][0]:
            merged_btags.append(webText[startind[i][0]: startind[i + 1][1]])
            i += 2
        else:
            merged_btags.append(webText[startind[i][0]: startind[i][1]])
            i += 1

    allparas = []

    last = 0
	
	# Extracting all content under the bold lines
    for i in range(0, len(finalST) - 1):
        allparas.append(html_data[finalST[i]:finalST[i + 1]])
        last = i + 1

	
	# Storing bold text and text under it into different lists
    final_bTags = []
    final_allparas = []

    min_index = min(len(allparas), len(bTags))
    for i in range(0, min_index):
        if bTags[i] and str(bTags[i]).strip() != "" and len(str(bTags[i]).strip()) > 5 and str(allparas[i]).startswith(str(bTags[i])):
            #Move conditions below
            final_bTags.append(re.sub( '[^A-Za-z0-9.,?!%()$&]+', ' ', html2text.html2text(str(bTags[i])) ))
            final_allparas.append(re.sub( '[^A-Za-z0-9.,?!%()$&]+', ' ', html2text.html2text(str(allparas[i])) ) )

    bTags = final_bTags
    allparas = final_allparas

    return bTags, allparas

# Insert Data to Mongodb RawData collection and return the document id fo the inserted record
def insertData(db, fileName):
    sik, cik, CompanyName, date, formType = fileName.split("_")
    doc = {
            "SIK" : sik,
            "CIK" : cik,
            "Company Name" : CompanyName,
            "Date" : date,
            "Form Type" : formType,
          }
    doc_id = db.get_collection('RawData').insert_one(doc).inserted_id
    return doc_id

# Update Data to Mongodb RawData collection for given doc_id with dataType(Risk Factor / Business) Details
def updateData(db, doc_id, dataType,html, text, btags, all_paras):
    db.get_collection('RawData').update({"_id": doc_id}, {"$set": {dataType + "HTML": html}})
    db.get_collection('RawData').update({"_id": doc_id}, {"$set": {dataType + "TEXT": text}})
    db.get_collection('RawData').update({"_id": doc_id}, {"$set": {dataType + "Bold Tags": btags}})
    db.get_collection('RawData').update({"_id": doc_id}, {"$set": {dataType + "Paragraphs": all_paras}})

# Reurn True if the item_name is found within the range of ind -1 and ind + 10 in webContent
def checkItemText(ind, webContent, item_name):
    check_text = ""
    for i in range( ind - 1, ind + 10 ):
        if (len(webContent) > i):
            temp = BeautifulSoup(webContent[i], "html.parser" )
            temp_plain_text_line = temp.get_text().strip().lower()
            if temp_plain_text_line is "":
                continue
            check_text += temp_plain_text_line
    check_text = ''.join( e for e in check_text if e.isalnum())
    if check_text.startswith(item_name):
       return True
    return False

# extracts the risk_factor and business sections from 10K
def extract_risk_factor_and_business_section_from_10K(db, url, file_name):
    try:
        fp = open(url, "r", encoding="utf-8")

        check_no_data_risk = False
        check_no_data_business = False

        webText = ""
        webContent = fp.readlines()

        for line in webContent :
            webText += html2text.html2text(line)

        doc_id = 0

        # ************************          Isolate "Risk Factor" Section for 10 K form   ************************
        ind = 0
        html_start = 0
        html_end = 1
        found = False

        '''
        For isolating risk section, below code first checks for the html line starting from 'item1a risk factor'.
        If it is found, then store its index and then search for 'item1b' or 'item2' and 'unresolved staff comments' section and
        store its index. Now the content between both sections is the entire risk section.
        '''
        for line in webContent:
            ind += 1
            html_line = BeautifulSoup(line, "html.parser")
            temp_text_line = html_line.get_text().strip().lower().replace("Â", "a")
			
			# removing spaces and special characters and merge it to search a particular section
            plain_text_line = ''.join(e for e in temp_text_line if e.isalnum())
            if plain_text_line is "":
                continue

			# Searching start index of the risk factor section
            if plain_text_line.startswith("item1a") or checkItemText(ind, webContent, "item1a"):

                check_text = ""
                for i in range(ind - 1, ind + 20):
                    if(len(webContent) > i):
                        temp = BeautifulSoup(webContent[i], "html.parser")
                        temp_plain_text_line = temp.get_text().strip().lower()
                        if temp_plain_text_line is "":
                            continue
                        check_text += temp_plain_text_line
                check_text = ''.join( e for e in check_text if e.isalnum())

                if "riskfactors" in check_text[:25]:
                    if "unresolvedstaffcomments" not in check_text[:40]:
                        html_start = ind

			# Searching end index of the risk factor section
            if plain_text_line.startswith("item1b") or checkItemText(ind, webContent, "item1b") or \
                    plain_text_line.startswith("item2") or checkItemText(ind, webContent, "item2"):
                check_text = ""
                for i in range(ind - 1, ind + 20):
                    if (len(webContent) > i):
                        temp = BeautifulSoup(webContent[i], "html.parser")
                        temp_plain_text_line = temp.get_text().strip().lower()
                        if temp_plain_text_line is "":
                            continue
                        check_text += temp_plain_text_line
                check_text = ''.join( e for e in check_text if e.isalnum())
                if "unresolvedstaffcomments" in check_text or "properties" in check_text:
                    html_end = ind
                    found = True
        if not found:
            if "item 1. business" in webText.lower():
                global total_risk_section_failed
                total_risk_section_failed += 1
            else:
                check_no_data_risk = True
            log_print_statments("No Risk Factor " + url)
        else:
			#insert basic information of file into database
            doc_id = insertData(db, file_name)
            global total_risk_section_passed
            total_risk_section_passed += 1

            log_print_statments("Risk Factor " + url)
            htmlString = ""
            for l in webContent[html_start - 1: html_end]:
                if l.__contains__("img"):
                    continue
                htmlString += l

			# Extracting bold text and text under the bold line for risk factors section
            htmlString = formatHTMLForSpace(htmlString)
            risk_btags, risk_paras = get_bold_and_para_lists(htmlString)
            text = html2text.html2text(htmlString)
            text = re.sub('[^A-Za-z0-9.,?!%()$&]+', ' ', text)

			# Update html content, textual content of risk factors into database
            updateData(db, doc_id, "Risk Factor ", htmlString, text, risk_btags, risk_paras)

        # ************************          Isolate "Business Section" Section for 10 K form   ************************
        ind = 0
        html_start = 0
        html_end = 1
        found = False

        '''
        For isolating business section, below code first checks for the html line starting from 'item1' and 'business'.
        If it is found, then store its index and then search for 'item1a'and 'risk factor' section and
        store its index. Now the content between both sections is the entire business section.
        '''
        for line in webContent:
            ind += 1
            html_line = BeautifulSoup(line, "html.parser")
            temp_text_line = html_line.get_text().strip().lower().replace("Â", "a")
			
			# removing spaces and special characters and merge it to search a particular section
            plain_text_line = ''.join(e for e in temp_text_line if e.isalnum())
            if plain_text_line is "":
                continue
				
			# Searching start index of the business section
            if plain_text_line.startswith("item1") or checkItemText(ind, webContent, "item1"):
                check_text = ""
                for i in range(ind - 1, ind + 20):
                    if (len(webContent) > i):
                        temp = BeautifulSoup(webContent[i], "html.parser")
                        temp_plain_text_line = temp.get_text().strip().lower()
                        if temp_plain_text_line is "":
                            continue
                        check_text += temp_plain_text_line
                check_text = ''.join(e for e in check_text if e.isalnum())
                if "business" in check_text[:15]:
                    if "riskfactors" not in check_text[:25]:
                        html_start = ind
			
			# Searching end index of the business section
            if plain_text_line.startswith("item1a") or checkItemText(ind, webContent, "item1a"):
                check_text = ""
                for i in range(ind - 1, ind + 20):
                    if (len(webContent) > i):
                        temp = BeautifulSoup(webContent[i], "html.parser")
                        temp_plain_text_line = temp.get_text().strip().lower()
                        if temp_plain_text_line is "":
                            continue
                        check_text += temp_plain_text_line
                check_text = ''.join(e for e in check_text if e.isalnum())
                if "riskfactors" in check_text:
                    html_end = ind
                    found = True

        if not found:
            log_print_statments("No Business " + str(url))

            if "item 1. business" in webText.lower():
                global total_bussiness_section_failed
                total_bussiness_section_failed += 1
            else:
                check_no_data_business = True
        else:
            global total_bussiness_section_passed
            total_bussiness_section_passed += 1
            log_print_statments("Business " + str(url))
            htmlString = ""
            for l in webContent[html_start - 1: html_end]:
                if l.__contains__("img"):
                     continue
                htmlString += l
				
			# Extracting bold text and text under the bold line for business section
            htmlString = formatHTMLForSpace(htmlString)

            business_btags, business_paras = get_bold_and_para_lists(htmlString)

            text = html2text.html2text(htmlString)
            text = re.sub('[^A-Za-z0-9.,?!%()$&]+', ' ', text)
            
            # Update html content, textual content of business section into database
            updateData(db, doc_id, "Business ", htmlString, text, business_btags, business_paras)

        if check_no_data_business and check_no_data_risk:
            global total_files_no_data
            total_files_no_data += 1
        else:
            global total_files_passed
            total_files_passed += 1

    except MemoryError as m:
        log_print_statments(str(m.__cause__) + " : " + str(url))
    except Exception as inst:
        if not check_no_data_business and not check_no_data_risk:
            global total_files_failed
            total_files_failed += 1
        else:
            total_files_no_data += 1
        log_print_statments(inst.args)
        log_print_statments(type(inst))
        log_print_statments("Exception in " + str(url))
    finally:
        webContent.clear()
        del webContent
        print(url)
        fp.close()

# iterate thrugh the files in local_folder for given year and form_type
def get_files(db, local_folder, year, form_type):
    os.chdir(local_folder)
    for quarter in range(2,5):
        quarter_folder = str(year) + "_Q" + str(quarter) + "_" + "Data"
        if os.path.exists(quarter_folder):
            os.chdir(quarter_folder)
            if os.path.exists(str(form_type)):
                os.chdir(str(form_type))
                for root, dirs, files in os.walk(os.getcwd()):
                    for file in files:

                        files_size = os.path.getsize(os.path.join(root, file))

                        if files_size / 1000000 > 10:
                            log_print_statments(str(file) +  " : " + str(files_size / 1000000))
                            continue

                        if file.endswith("_" + form_type + ".html") and not file.startswith("RF"):
                            global total_files_processed
                            total_files_processed += 1
                            extract_risk_factor_and_business_section_from_10K(db, os.path.join(root, file), file)
                            print_statistics()
                os.chdir("..")
            os.chdir("..")

local_folder = "C:\\Users\\Capstone\\Desktop\\Capstone Submission Data\\Submission data" # Folder with the downloaded data
client = MongoClient( 'localhost', 27017 ) # accesing Mongo DB clinet running on 27017 port of local host
db = client['Capstone'] # Accessing Capstone database

# Function Calls
get_files(db, local_folder, "2016", "10-K")


# # total_files_processed += 1
# extract_risk_factor_and_business_section_from_10K(db, 'C:\\Users\\Capstone\\Desktop\\Amey_Code_25_02_2017\\Capstone\\2016_Q1_Data\\10-K\\2834_1226616_MEDICINOVA INC_2016-02-25_10-K.html', '2834_1226616_MEDICINOVA INC_2016-02-25_10-K.html')
# # print_statistics()

log_fp.close()