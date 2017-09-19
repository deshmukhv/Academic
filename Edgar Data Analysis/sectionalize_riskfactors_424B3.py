#Import required libraries
from bs4 import BeautifulSoup
import os
import re
from pymongo import MongoClient
import html2text
'''
This python script reads the 424B3/4/5 html file and fetches Risk Factors. It stores start and end index and retrieves
 html content from it. Once this data is found, this script then extract all bold lines and text under it in the list
object. Then it saves these information in MongoDB database for further analysis. This script also evaluates the result
by calculating accuracy using number of records processed and failed.
'''

#Global Variable Declaration
total_files_processed = 0
total_files_passed = 0
total_files_failed = 0
total_files_no_data = 0

total_risk_section_passed = 0
total_risk_section_failed = 0

#Opening log text file in append mode to wirte statistics, file name and errors
log_fp = open("log_424B.txt", "a")

#This function calculates the overall accuracy of the 424B forms
def print_statistics():
    global total_files_processe
    global total_files_passed
    global total_files_failed
    global total_files_no_data
    global total_risk_section_passed
    global total_risk_section_failed

    log_print_statments("\n")
    log_print_statments("\n")
    log_print_statments("\n")
    log_print_statments("********************Evaluation Report********************\n")
    try:
        #Calculating Accuracy of sectionalizing 10-K forms
        if total_files_processed - total_files_no_data > 0:
            log_print_statments("Total 424B Processed : " +  str(total_files_processed))
            log_print_statments("Total 424B Passed : " + str(total_risk_section_passed))
            log_print_statments("Total 424B Failed : " + str(total_risk_section_failed))
            log_print_statments("Total 424B with no Data : " + str(total_files_processed - total_risk_section_passed - total_risk_section_failed))
            log_print_statments("424B Overall Accuracy :" +
                                str(total_risk_section_passed + (total_files_processed - total_risk_section_passed - total_risk_section_failed) / (total_files_processed) * 100))
            log_print_statments("\n")

        if total_risk_section_passed + total_risk_section_failed > 0:
            log_print_statments("Total Risk Sections extracted: " + str(total_risk_section_passed))
            log_print_statments("Total Risk Sections extraction failed: " + str(total_risk_section_failed))
            log_print_statments("424B Risk Sections Accuracy :" +
                                str(total_risk_section_passed / (total_risk_section_passed + total_risk_section_failed) * 100))
            log_print_statments("\n")
    except Exception as ex:
        log_print_statments("Exception in " + str(ex))


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
    # log_print_statments(formatedLines)
    return formatedLines

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
    doc_id = db.get_collection('RawData424B').insert_one(doc).inserted_id
    return doc_id

# Update Data to Mongodb RawData collection for given doc_id with dataType(Risk Factor / Business) Details
def updateData(db, doc_id, dataType,html, text, btags, all_paras):
    db.get_collection('RawData424B').update({"_id": doc_id}, {"$set": {dataType + "HTML": html}})
    db.get_collection('RawData424B').update({"_id": doc_id}, {"$set": {dataType + "TEXT": text}})
    db.get_collection('RawData424B').update({"_id": doc_id}, {"$set": {dataType + "Bold Tags": btags}})
    db.get_collection('RawData424B').update({"_id": doc_id}, {"$set": {dataType + "Paragraphs": all_paras}})

# Takes the HTML data as input and divide it into diferent paragraphs based on Bold Tags in the HTML and return the list og Bold Tags and list of corresponding Pargraphs
def get_bold_and_para_lists(html_data):
    webText = html2text.html2text(html_data)
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

	# storing start and end index of the bold tags in html file
    startind = []
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

# Reurn True if the item_name is found within the range of ind -1 and ind + 10 in webContent
def checkItemText(ind, webContent, item_name, isLower):
    check_text = ""
    for i in range( ind - 1, ind + 20 ):
        if (len( webContent ) > i):
            temp = BeautifulSoup( webContent[i], "html.parser" )
            if isLower:
                temp_plain_text_line = temp.get_text().strip().lower()
            else:
                temp_plain_text_line = temp.get_text( ).strip( )
            if temp_plain_text_line is "":
                continue
            check_text += temp_plain_text_line
    check_text = ''.join( e for e in check_text if e.isalnum())
    if check_text.startswith(item_name):
        return True
    return False

'''
This function reads the file, checks the risk factor from Table of content. and if found, search for next title in
table of content. Once title found, it extract data between both titles. This data is used to separate bold and text.
'''
def convert_html_to_text(db, url, file_name):
    fp = open(url, "r", encoding="utf-8")
    webContent = fp.readlines()
    ind = 0
    index = 0
    html_start = 0
    html_end = 1
    found = False

    no_Risk_factor = True
    try:
        #Searching for Table of Content at the start of html text
        for line in webContent:
            ind += 1
            html_line = BeautifulSoup(line, "html.parser")
            temp_text_line = html_line.get_text().strip()
            plain_text_line = ''.join(e for e in temp_text_line if e.isalnum())
            if plain_text_line is "":
                continue
            if plain_text_line.startswith("TABLEOFCONTENTS") or checkItemText(ind, webContent, "TABLEOFCONTENTS", False):
                index = ind
                break

        found_subtitle = False
        next_subtitle = ""

        #Searching Risk Factor and its next title
        for line in webContent[index:]:
            if found_subtitle:
                break
            ind += 1
            html_line = BeautifulSoup(line, "html.parser")
            temp_text_line = html_line.get_text().strip().lower()
			
			# removing spaces and special characters and merge it to search a particular section
            plain_text_line = ''.join(e for e in temp_text_line if e.isalnum())
            if plain_text_line is "":
                continue

            if plain_text_line.startswith("riskfactors") or checkItemText(ind, webContent, "riskfactors", True):
                if found_subtitle:
                    break
                for i in range(ind, ind + 50):
                    if found_subtitle:
                        break
                    if(len(webContent) > i):
                        if found_subtitle:
                            break
                        temp = BeautifulSoup(webContent[i], "html.parser")
                        temp_plain_text_line = temp.get_text().strip().lower()
                        temp_plain_text_line = ''.join(e for e in temp_plain_text_line if e.isalnum())
                        if temp_plain_text_line is "":
                            continue

                        if re.search('\d', temp_plain_text_line):
                            if found_subtitle:
                                break
                            for j in range(i + 1, i + 50):
                                temp_1 = BeautifulSoup(webContent[j], "html.parser")
                                temp_plain_text_line_1 = temp_1.get_text().strip().lower()
                                temp_plain_text_line_1 = ''.join(e for e in temp_plain_text_line_1 if e.isalnum())
                                if temp_plain_text_line_1 is "":
                                    continue
                                if re.search('\d', temp_plain_text_line_1):
                                    found_subtitle = True
                                    ind = j
                                    break
                                next_subtitle += temp_plain_text_line_1

        index = ind
        html_start = 0

        #Finding start and end index of the Risk Factor section content
        while(found_subtitle and ind < len(webContent)):
            for line in webContent[index:]:
                ind += 1
                html_line = BeautifulSoup(line, "html.parser")
                temp_text_line = html_line.get_text().strip().lower()
                plain_text_line = ''.join(e for e in temp_text_line if e.isalnum())
                if plain_text_line is "":
                    continue
                if html_start == 0 and (plain_text_line.startswith("riskfactors") or checkItemText(ind, webContent, "riskfactors", True)):
                    no_Risk_factor = False
                    html_start = ind
                if html_start > 0 and (plain_text_line.startswith(next_subtitle) or checkItemText(ind, webContent, next_subtitle, True)):
                    html_end = ind
                    found = True
                    break
			
			# If start and end index is left than 50, means there is another table of content in the file
            if(html_end - html_start) < 50:
                index = html_end
                html_start = 0
                html_end = 1
                found = False
                no_Risk_factor = True
            else:
                break

        if found_subtitle and found:
            global total_risk_section_passed
            total_risk_section_passed += 1

            log_print_statments("Risk Factor " + url)
            htmlString = ""

            #Saving content between start and end index in htmlString variable
            for l in webContent[html_start - 1: html_end]:
                if l.__contains__("img"):
                    continue
                htmlString += l


            # Separating bold lines and text under it
            htmlString = formatHTMLForSpace(htmlString)
            risk_btags, risk_paras = get_bold_and_para_lists(htmlString)
            text = html2text.html2text(htmlString)
            text = re.sub('[^A-Za-z0-9.,?!%()$&]+', ' ', text)

            #Storing data into MongoDB database
            if htmlString:
                if len(risk_btags) == 0:
                    risk_btags.append("Risk Factor")
                    risk_paras.append(text)
                doc_id = insertData(db, file_name)
				
				# Update html content, textual content of risk factors into database
                updateData(db, doc_id, "Risk Factor ", htmlString, text, risk_btags, risk_paras)

				# Calculating number of files sectionalized properly
                global total_files_passed
                total_files_passed += 1
            else:
                total_files_no_data += 1
        else:
			# if found_subtitle is false, means there is no table of content, 
			#and it is used for calculating number of no data records
            if not found_subtitle:
                global total_files_no_data
                total_files_no_data += 1

            if not no_Risk_factor:
                global total_risk_section_failed
                total_risk_section_failed += 1
            log_print_statments("No Risk Factor " + url)

    except Exception as inst:
        global total_files_failed
        total_files_failed += 1
        log_print_statments(inst.args)
        log_print_statments(type(inst))
        log_print_statments("Exception in " + str(url))

# iterate thrugh the files in local_folder for given year and form_type
def get_files(db, local_folder, year, form_type):
    os.chdir(local_folder)
    for quarter in range(1,2):
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
                            convert_html_to_text(db, os.path.join(root, file), file)
                            global total_files_processed
                            total_files_processed += 1

                            print_statistics()
                os.chdir("..")
            os.chdir("..")

local_folder = "C:\\Users\\Capstone\\Desktop\\Capstone Submission Data\\Submission data" # Folder with the downloaded data
client = MongoClient( 'localhost', 27017 ) # accesing Mongo DB clinet running on 27017 port of local host
db = client['Capstone'] # Accessing Capstone database

# Function Calls
get_files(db, local_folder, "2016", "424B3")

# total_files_processed += 1
#convert_html_to_text(db, "C:\\Users\\Capstone\\Desktop\\Capstone Submission Data\\Submission data\\2016_Q1_Data\\424B5\\2834_1360214_Imprimis Pharmaceuticals  Inc _2016-03-14_424B5.html", "2834_1360214_Imprimis Pharmaceuticals  Inc _2016-03-14_424B5.html")
#convert_html_to_text(db, "C:\\Users\\Capstone\\Desktop\\Capstone Submission Data\\Submission data\\2016_Q1_Data\\424B5\\2834_1390478_Galena Biopharma  Inc _2016-01-07_424B5.html", "2834_1390478_Galena Biopharma  Inc _2016-01-07_424B5.html")
#convert_html_to_text(db, "C:\\Users\\Capstone\\Desktop\\Capstone Submission Data\\Submission data\\2016_Q1_Data\\424B3\\2834_1460702_RITTER PHARMACEUTICALS INC_2016-02-25_424B3.html", "2834_1460702_RITTER PHARMACEUTICALS INC_2016-02-25_424B3.html")
# print_statistics()

log_fp.close()