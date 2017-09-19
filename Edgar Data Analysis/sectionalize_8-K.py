#Import required libraries

from bs4 import BeautifulSoup
from urllib.request import urlopen
import os
import re
import html2text
import traceback
from pymongo import MongoClient

'''
This python script reads the 8-K html file and fetches each item number and their description, text under it and
exhibit numbers and their description. Once all information is stored in a list, it saves these information in MongoDB
database for further analysis. This script also evaluates the result by calculating accuracy using
number of records processed and failed.
'''

#Global Variable Declaration
total_files_processed = 0
total_files_passed = 0
total_files_failed = 0
total_files_no_data = 0

total_exibit_passed = 0
total_exibit_failed = 0
total_exibit_no_data = 0

#Opening log text file in append mode to wirte statistics, file name and errors
log_fp = open("log_8k.txt", "a")

#This function calculates the overall accuracy of the 8-K forms
def print_statistics():
    global total_files_processe
    global total_files_passed
    global total_files_failed
    global total_files_no_data
    global total_exibit_passed
    global total_exibit_failed
    global total_exibit_no_data

    log_print_statments("\n")
    log_print_statments("\n")
    log_print_statments("\n")
    log_print_statments("********************Evaluation Report********************\n")
    try:
		#Calculating Accuracy of sectionalizing 8-K forms
        log_print_statments("Total 8-k Processed : " +  str(total_files_processed))
        log_print_statments("Total 8-k Passed : " + str(total_files_passed))
        log_print_statments("Total 8-k Failed : " + str(total_files_failed))
        log_print_statments("Total 8-k with no Data : " + str(total_files_no_data))
        log_print_statments("8-k Overall Accuracy :" +
                            str(total_files_passed / (total_files_processed - total_files_no_data) * 100))
        log_print_statments("\n")

        log_print_statments("Total Exhibits extracted: " + str(total_exibit_passed))
        log_print_statments("Total Exhibits with no Data: " + str(total_exibit_no_data))
        log_print_statments("Total Exhibits extraction failed: " + str(total_exibit_failed))
        log_print_statments("8-k Exhibits Accuracy :" +
                            str((total_exibit_passed - total_exibit_failed)  /(total_exibit_passed + total_exibit_no_data) * 100))
        log_print_statments("\n")
    except Exception as ex:
        log_print_statments("Exception in " + str(ex))


#Write the statements into log file
def log_print_statments(statment):
    global log_fp
    log_fp.write(str(statment) + "\n")

# Insert Data to Mongodb RawData collection and return the document id fo the inserted record
def insertData(db, fileName,item_no,title,item_text,exhibit_no,exhibit_text):
    sik, cik, CompanyName, date, formType = fileName.split("_")
    doc = {
        "SIC": sik,
        "CIK": cik,
        "Company Name": CompanyName,
        "Date": date,
        "Form Type": formType,
        "Item Number": item_no,
        "Title": title,
        "Item Description": item_text,
        "Exhibit Number": exhibit_no,
        "Exhibit Description": exhibit_text
    }
    doc_id = db.get_collection('RawData_8K').insert_one(doc).inserted_id
    return doc_id

#This function takes input as an url of 8-K forms and fetches the relevant information
def sectionalize_8k(db, url, file_name):
    global total_files_processe
    global total_files_passed
    global total_files_failed
    global total_files_no_data
    global total_exibit_passed
    global total_exibit_failed
    global total_exibit_no_data

    #Opening file and reading the content of the file
    fp = open(url, "r", encoding="utf-8")
    webContent = fp.readlines()

    ind = 0

    #items_8K list stores all information about 8-K items
    item_no_list = []  # list of item number
    title_list = []  # list of title
    item_text_list = []  # list of item text

    exhibit_no_list = []    # exhibit_no list stores all exhibit numbers of the particular form
    exhibit_text_list = []  # description of the corresponding exhibit numbers
    is_exhibit = False
    try:
        while(True):
            #parsing html text from particular index of the html file
            html_line = BeautifulSoup( webContent[ind], "html.parser" ).text.strip().lower()

            #exit condition i.e. if text contains "signature", then exit from the loop as we dont require any information
            #beyond the signature text
            if html_line.startswith("signature"):
                break

            #incrementing index to fetch the line of that index from html file in next iteration
            ind += 1

            #below block of statements retrieve the text which is starting from "item" keyword
            if html_line is not "" and html_line.startswith("item"):

                #item_list list stores each item information and their exhibit_no list
                item_list = []

                temp_ind = ind - 1
                item_no = ""        #stores item number
                title = ""          #stores title of the item number
                item_text = ""      #stores text under the item number

                temp = BeautifulSoup(webContent[temp_ind], "html.parser").text.strip()

                ''' Below code checks for Item Number and its title. First 'If' checks if html line has item no pattern
                    and if it is found, it checks for its descriptin. 'Else checks html line has item no and its
                    description in pattern.
                '''

                #Checks only Item No first, then its title in next html lines
                if re.fullmatch(r'itemÂ*\s\d+\.\d+\.*', temp.lower()):
                    item_no = temp.lower()

                    #Finding the title once item number found
                    for i in range(temp_ind + 1, temp_ind + 10):
                        if (len(webContent) > i):
                            title_html = BeautifulSoup(webContent[i], "html.parser").text.strip()
                            if title_html is not "":
                                title = title_html
                                temp_ind += 1
                else:
                    # Checks for Item No with Title in single html line
                    if re.match(r'itemÂ*\s\d+\.\d+\s*\w+\.*', temp.lower()):
                        temp_split =  temp.split()

                        #Finding the Title once item number found
                        for t in temp_split:
                            if re.fullmatch(r'\d+\.\d+\.*',t):
                                item_no = "item " + t
                                t_ind = temp_split.index(t)
                                for i in temp_split[t_ind+1:]:
                                    title += i + " "

                        temp_ind += 1

                item_no = re.sub('[^a-z0-9.,?!%()$]+', ' ', item_no)
                title = re.sub('[^A-Za-z0-9.,?!%()$]+', ' ', title)
                # print("item no:" + item_no)
                # print("title:" + title)

                # Below code finds the text below the particular item number
                for text in webContent[temp_ind+1:]:
                    temp1 = BeautifulSoup(text, "html.parser").text.strip()

                    #Exit criteria: If next item found or signature text found, it exits from the loop
                    if (temp1.lower().startswith("item") or temp1.lower().startswith("signature")):
                        break

                    if temp1 == title:
                        continue

                    item_text += temp1

                    #print(temp1)
                    #Checks for the exhibit number if item no is '9.01'.
                    if re.fullmatch(r'item 9.01\.*', item_no) and re.fullmatch(r'\d+\.\d+\.*',temp1):
                        exhibit_no_list.append(temp1)
                    else:
                        #If text contains exhibit number and its description in one line, then split the text and find exhibit number
                        if re.fullmatch(r'item 9.01\.*', item_no) and re.match(r'\d+\.\d+\.*\s*\w+\.*',temp1):
                            temp_split = temp1.split()
                            # Finding the exhibit number
                            for t in temp_split:
                                if re.fullmatch(r'\d+\.\d+\.*', t):
                                    exhibit_no_list.append(t)

                #print(exhibit_no_list)
                item_text = re.sub('[^A-Za-z0-9.,?!%()$]+', ' ', item_text)
                #print("item text:"+ item_text)

                is_exhibit = False
                #Extracting exhibit descriptipn of corresponding exhibit number
                if re.fullmatch(r'item 9.01\.*', item_no) and exhibit_no_list:
                    #Looping through all exhibit numbers
                    for i in range (0, len(exhibit_no_list)):
                        '''
                        Storing length of ith exhibit number and first index of the ith exhibit number to retrieve the
                        description of corresponding exhibit number. The description is captured next index of the exhibit
                        number till the next exhibit number is found. If there is a last element in exhibit number list,
                        then retrieve till the end
                        '''
                        item_length = len(str(exhibit_no_list[i]))
                        current_index = item_text.index(str(exhibit_no_list[i]))
                        if i == len(exhibit_no_list) - 1:
                            exhibit_text_list.append(item_text[current_index + item_length : ])
                        else:
                            next_index = item_text.index(str(exhibit_no_list[i + 1]))
                            exhibit_text_list.append(item_text[current_index + item_length :  next_index])

                        is_exhibit = True

                #Storing item_no, title and text in item_list and exhibit number in exhibit_list.
                #Then store all information in items_8K list.
                if item_no and title and item_text:
                    item_no_list.append(item_no)
                    title_list.append(title)
                    item_text_list.append(item_text)

        #Storing 8-k Form details into MongoDB
        if item_no_list and title_list and item_text_list:
            #Calculating if exhibit list is empty, then add 1 to total exhibit failed, else add 1 to total exhibit passed.
            if exhibit_no_list:
                total_exibit_passed += 1
            else:
                total_exibit_no_data += 1

            insertData(db, file_name,item_no_list,title_list,item_text_list,exhibit_no_list,exhibit_text_list)
            total_files_passed += 1
        else:
            total_files_no_data += 1
        log_print_statments("Processed in " + str(url))

    except Exception as ex:
        total_files_failed += 1
        if is_exhibit is False:
            total_exibit_failed += 1
        log_print_statments("Exception in " +  str(url))

# iterate through the files in local_folder for given year and form_type
def get_files(db, local_folder, year, form_type):
    os.chdir(local_folder)
    for quarter in range(1,5):
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
                            sectionalize_8k(db, os.path.join(root, file), file)

                            #Counting total number of files processed and printing statistics once the file is processed
                            global total_files_processed
                            total_files_processed += 1
                            print_statistics()
                os.chdir("..")
            os.chdir("..")

# Initilization of MongoDB client
local_folder = "C:\\Users\\Capstone\\Desktop\\Capstone Submission Data\\Submission data" # Folder with the downloaded data
client = MongoClient('localhost', 27017)  # accesing Mongo DB clinet running on 27017 port of local host
db = client['Capstone']  # Accessing Capstone database

# Function Call
get_files(db, local_folder, "2016", "8-K")

#sectionalize_8k(db, "C:\\Users\\Capstone\\Desktop\\Capstone Submission Data\\Submission data\\2016_Q1_Data\\8-K\\2834_1061983_CYTOKINETICS INC_2016-01-11_8-K.html", "2834_1061983_CYTOKINETICS INC_2016-01-11_8-K.html")

