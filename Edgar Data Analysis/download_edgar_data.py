# Import required libraries
from __future__ import division
from urllib.request import urlopen
from bs4 import BeautifulSoup
import os
from tkinter import *
from tkinter import ttk

'''
This script will download master.idx file for each quarter of the year and then download
the html forms such as 8-K, 10-K, 424B3, 424B4 and 424B5 in the local storage.
'''
# Global Variables Declaration
count_10k_P = 0
count_10k_F = 0
count_8k_P = 0
count_8k_F = 0
count_424B3_P = 0
count_424B3_F = 0
count_424B4_P = 0
count_424B4_F = 0
count_424B5_P = 0
count_424B5_F = 0
count_total_P = 0
count_total_F = 0
log_fp = 0


# This function calculates the overall accuracy of the 8-K forms
def print_statistics():
    global count_10k_P
    global count_10k_F
    global count_8k_P
    global count_8k_F
    global count_424B3_P
    global count_424B3_F
    global count_424B4_P
    global count_424B4_F
    global count_424B5_P
    global count_424B5_F
    try:
        # Calculating Accuracy of downloading 10-K forms
        log_print_statments("********************Evaluation Report********************\n")
        log_print_statments("Total 10-k Passed : " + str(count_10k_P))
        log_print_statments("Total 10-k Failed : " + str(count_10k_F))
        log_print_statments("10-k Accuracy :" + str(count_10k_P / (count_10k_P + count_10k_F) * 100))
        log_print_statments("\n")

        # Calculating Accuracy of downloading 8-K forms
        log_print_statments("Total 8-k Passed : " + str(count_8k_P))
        log_print_statments("Total 8-k Failed : " + str(count_8k_F))
        log_print_statments("8-k Accuracy :" + str(count_8k_P / (count_8k_P + count_8k_F) * 100))
        log_print_statments("\n")

        # Calculating Accuracy of downloading 424B3 forms
        log_print_statments("Total 424B3 Passed : " + str(count_424B3_P))
        log_print_statments("Total 424B3 Failed : " + str(count_424B3_F))
        log_print_statments("424B3 Accuracy :" + str(count_424B3_P / (count_424B3_P + count_424B3_F) * 100))
        log_print_statments("\n")

        # Calculating Accuracy of downloading 424B4 forms
        log_print_statments("Total 424B4 Passed : " + str(count_424B4_P))
        log_print_statments("Total 424B4 Failed : " + str(count_424B4_F))
        log_print_statments("424B4 Accuracy :" + str(count_424B4_P / (count_424B4_P + count_424B4_F) * 100))
        log_print_statments("\n")

        # Calculating Accuracy of downloading 424B5 forms
        log_print_statments("Total 424B5 Passed : " + str(count_424B5_P))
        log_print_statments("Total 424B5 Failed : " + str(count_424B5_F))
        log_print_statments("424B5 Accuracy :" + str(count_424B5_P / (count_424B5_P + count_424B5_F) * 100))

    except Exception as ex:
        log_print_statments("Exception in " + str(ex))


# Write the statements into log file
def log_print_statments(statment):
    global log_fp
    log_fp.write(str(statment) + "\n")


# DOwnloading html file using given URL and name of that file will be same as file_name
def download_html_file(url, file_name):
    response = urlopen(url)
    webContent = response.read()
    soup = BeautifulSoup(webContent, "html.parser")
    f = open(file_name, "w", encoding="UTF-8")
    f.write(soup.prettify())
    f.close()


# Searching SIC code for the corresponding CIK Code
def get_sic_code_by_cik(cik):
    try:
        # Giving CIK parameter in HTTP request to search its correponding SIC Code
        base_info_url = "https://www.sec.gov/cgi-bin/browse-edgar?CIK=" + cik + "&owner=exclude&action=getcompany&Find=Search"
        response = urlopen(base_info_url)
        webContent = response.read()
        soup = BeautifulSoup(webContent, "html.parser")
        for tag in soup("p", attrs={"class": "identInfo"}):
            a_tag = tag.find("a")
            return (a_tag.text)
    except:
        return ""


# Read path from master.idx file for all the form types, and downloading files from that path.
def read_form_data_from_master(year, quater, master_file_name, siccodes):
    global progress
    global var1
    global var2
    global var3
    global var4
    global f1
    folder_path = str(f1.get())
    folder_path = folder_path.replace("\\", "\\\\") + "\\\\"
    # This url will be used to download the forms

    const_URL = "https://www.sec.gov/Archives/"
    master_file_data = []

    with open(master_file_name) as fp:
        file_header = fp.readlines()[:5]

    with open(master_file_name) as fp:
        file_data = fp.readlines()[11:]

    for line in file_data:
        master_file_data.append(line.split("|"))

    folder_name = year + "_" + quater + "_Data"

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    os.chdir(folder_name)

    # Links for required form type
    for line in master_file_data:
        form_type_name = line[2].replace("/", " ").replace(".", " ").replace(",", " ").replace("\\", " ")
        company_number = line[0].replace("/", " ").replace(".", " ").replace(",", " ").replace("\\", " ")
        date_str = line[3].replace("/", " ").replace(".", " ").replace(",", " ").replace("\\", " ")
        company_name = line[1].replace("/", " ").replace(".", " ").replace(",", " ").replace("\\", " ")

        try:
            if var1.get() == 1 and "10-K" in line[2]:
                progress.start()
                # Extracting SIC Code using CIK number and if that belongs given SIC code, then download the form
                # else skip the file
                siccode = get_sic_code_by_cik(company_number)
                if siccode not in siccodes:
                    continue

                # Constructing file name for the 10-K form
                file_name = siccode + "_" + company_number + "_" + company_name + "_" + date_str + "_" + form_type_name + ".html"
                if not os.path.exists("10-K"):
                    os.makedirs("10-K")
                os.chdir("10-K")

                # Downloading the 10-K form from constrcuted URL
                download_html_file(const_URL + line[4], file_name)

                # Calculating total number of files downloaded
                global count_10k_P
                count_10k_P += 1

            elif var2.get() == 1 and "8-K" in line[2]:

                # Extracting SIC Code using CIK number and if that belongs given SIC code, then download the form
                # else skip the file
                siccode = get_sic_code_by_cik(company_number)
                if siccode not in siccodes:
                    continue

                # Constructing file name for the 8-K form
                file_name = siccode + "_" + company_number + "_" + company_name + "_" + date_str + "_" + form_type_name + ".html"

                if not os.path.exists("8-K"):
                    os.makedirs("8-K")
                os.chdir("8-K")

                # Downloading the 8-K form from constrcuted URL
                download_html_file(const_URL + line[4], file_name)

                # Calculating total number of files downloaded
                global count_8k_P
                count_8k_P += 1

            elif var3.get() == 1 and "424B3" in line[2]:

                # Extracting SIC Code using CIK number and if that belongs given SIC code, then download the form
                # else skip the file
                siccode = get_sic_code_by_cik(company_number)
                if siccode not in siccodes:
                    continue

                # Constructing file name for the 424B3 form
                file_name = siccode + "_" + company_number + "_" + company_name + "_" + date_str + "_" + form_type_name + ".html"
                form_type = "424B3"
                if not os.path.exists(form_type):
                    os.makedirs(form_type)

                os.chdir(form_type)

                # Downloading the 424B3 form from constrcuted URL
                download_html_file(const_URL + line[4], file_name)

                # Calculating total number of files downloaded
                global count_424B3_P
                count_424B3_P += 1

            elif var4.get() == 1 and "424B4" in line[2]:

                # Extracting SIC Code using CIK number and if that belongs given SIC code, then download the form
                # else skip the file
                siccode = get_sic_code_by_cik(company_number)
                if siccode not in siccodes:
                    continue

                form_type = "424B4"
                if not os.path.exists(form_type):
                    os.makedirs(form_type)

                # Constructing file name for the 424B4 form
                file_name = siccode + "_" + company_number + "_" + company_name + "_" + date_str + "_" + form_type_name + ".html"

                os.chdir("424B4")

                # Downloading the 424B4 form from constrcuted URL
                download_html_file(const_URL + line[4], file_name)

                # Calculating total number of files downloaded
                global count_424B4_P
                count_424B4_P += 1

            elif var5.get() == 1 and "424B5" in line[2]:

                # Extracting SIC Code using CIK number and if that belongs given SIC code, then download the form
                # else skip the file
                siccode = get_sic_code_by_cik(company_number)
                if siccode not in siccodes:
                    continue

                form_type = "424B5"
                if not os.path.exists(form_type):
                    os.makedirs(form_type)

                # Constructing file name for the 424B5 form
                file_name = siccode + "_" + company_number + "_" + company_name + "_" + date_str + "_" + form_type_name + ".html"

                os.chdir("424B5")

                # Downloading the 424B5 form from constrcuted URL
                download_html_file(const_URL + line[4], file_name)

                # Calculating total number of files downloaded
                global count_424B5_P
                count_424B5_P += 1

            os.chdir(folder_path + folder_name)
            # os.chdir("C:\\Users\\Capstone\\Desktop\\Capstone Submission Data\\Submission data\\" + folder_name )
        except:
            log_print_statments(file_name)

            # Calcuating number of failed records for each form
            print("Error Downloading :", file_name)
            if "10-K" in line[2]:
                global count_10k_F
                count_10k_F += 1
            elif "8-K" in line[2]:
                global count_8k_F
                count_8k_F += 1
            elif "424B3" in line[2]:
                global count_424B3_F
                count_424B3_F += 1
            elif "424B4" in line[2]:
                global count_424B4_F
                count_424B4_F += 1
            elif "424B5" in line[2]:
                global count_424B5_F
                count_424B5_F += 1


# def download_edgar_data_by_year(year):
def download_edgar_data_by_year():
    global e1
    global e2
    global f1

    global var1
    global var2
    global var3
    global var4
    global var5

    if var1.get() == 0 and var2.get() == 0 and var3.get() == 0 and var4.get() == 0 and var5.get() == 0:
        return

    fyear = str(e1.get())
    tyear = str(e2.get())

    if not tyear:
        tyear = int(fyear) + 1

    folder_path = str(f1.get())
    folder_path = folder_path.replace("\\", "\\\\") + "\\\\"

    # bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)

    global count_10k_P
    global count_10k_F
    global count_8k_P
    global count_8k_F
    global count_424B3_P
    global count_424B3_F
    global count_424B4_P
    global count_424B4_F
    global count_424B5_P
    global count_424B5_F

    # re-initialization of global variables to calculate next year's accuracy
    count_10k_P = 0
    count_10k_F = 0
    count_8k_P = 0
    count_8k_F = 0
    count_424B3_P = 0
    count_424B3_F = 0
    count_424B4_P = 0
    count_424B4_F = 0
    count_424B5_P = 0
    count_424B5_F = 0

    # Opening log text file in append mode to wirte statistics, file name and errors
    for year in range(int(fyear), int(tyear)):
        global log_fp
        log_fp = open("log_download_" + str(year) + ".txt", "a")

        # for quater in range(1, 5):
        for quater in range(1, 5):
            file_name = str(year) + "_" + str(quater) + "master.idx"
            # os.chdir("C:\\Users\\Amey\\PycharmProjects\Capstone")
            os.chdir(folder_path)
            if not os.path.exists(file_name):
                master_file_base_url = "https://www.sec.gov/Archives/edgar/full-index/" + str(year) + "/QTR" + str(
                    quater) + "/master.idx"
                response = urlopen(master_file_base_url)
                webContent = response.read()
                soup = BeautifulSoup(webContent, "html.parser")
                f = open(file_name, "w", encoding="UTF-8")
                f.write(soup.prettify())
                f.close()
            siccodes = ["2834", "2836"]
            read_form_data_from_master(str(year), "Q" + str(quater), file_name, siccodes)

        log_fp.close()

# for x in range(2010,2016):
#
#     # Opening log text file in append mode to wirte statistics, file name and errors
#     global log_fp
#     log_fp = open("log_download_" + str(year) + ".txt", "a")
#     download_edgar_data_by_year(str(x))
#     print_statistics()

win = Tk()
win.title("Download Edgar Data")

mainframe = ttk.Frame(win, padding="15 15 15 15")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

Label(mainframe, text="Year").grid(row=0, column=0, columnspan=2)

Label(mainframe, text="From: ").grid(row=1, column=0, sticky=E)
e1 = Entry(mainframe, width=20)
e1.grid(row=1, column=1, pady=5)

Label(mainframe, text="To: ").grid(row=2, column=0, sticky=E)
e2 = Entry(mainframe, width=20)
e2.grid(row=2, column=1, pady=5)

Label(mainframe, text="Form Types:").grid(row=0, column=3, columnspan=2)
var1 = IntVar()
var1.set(1)
c1 = Checkbutton(mainframe, text="10-K", variable=var1, onvalue=1, offvalue=0).grid(row=1, column=3, sticky=W)

var2 = IntVar()
var2.set(1)
Checkbutton(mainframe, text="8-K", variable=var2, onvalue=1, offvalue=0).grid(row=2, column=3, sticky=W)

var3 = IntVar()
var3.set(1)
Checkbutton(mainframe, text="424B3", variable=var3, onvalue=1, offvalue=0).grid(row=1, column=4, sticky=W)

var4 = IntVar()
var4.set(1)
Checkbutton(mainframe, text="424B4", variable=var4, onvalue=1, offvalue=0).grid(row=2, column=4, sticky=W)

var5 = IntVar()
var5.set(1)
Checkbutton(mainframe, text="424B4", variable=var5, onvalue=1, offvalue=0).grid(row=1, column=5, sticky=W)

Label(mainframe, text="Absolute Folder Path: ").grid(row=4, column=0, columnspan=3, sticky=W)
f1 = Entry(mainframe)
f1.grid(row=5, column=0, columnspan=6, sticky=W + E)

Button(mainframe, text='Download', command=download_edgar_data_by_year, width=30).grid(row=6, column=0, columnspan=6,
                                                                                       pady=5)


mainloop()