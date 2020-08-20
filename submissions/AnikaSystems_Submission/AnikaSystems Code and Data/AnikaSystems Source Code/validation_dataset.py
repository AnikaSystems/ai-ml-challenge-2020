# validation_dataset.py - Validate data file.

import openpyxl
import classifier
from pdf_to_string import *


# Result data that will be output 
vres = []

# Load validation dataset
vwb = openpyxl.load_workbook("AI_ML_Challenge_Validation_Data_Set_v1.xlsx")
vsheet = vwb["AI_ML_Challenge_Validation_Data"]

# Gather clauses
vclauses = []

for i in range(2, 1397):
    vcell_clause_text = vsheet["B"+str(i)].value
    vcell_clause_id = vsheet["A"+str(i)].value

    if not vcell_clause_text is None:
        # print(vcell_clause_text)
        vcell_clause_text = remove_control_characters(vcell_clause_text).strip()
        vcell_clause_text = vcell_clause_text.replace(u'\ufffd', ' ')
        vcell_clause_text = removeNonAscii(vcell_clause_text)

        vclauses.append(vcell_clause_text)
        vres.append({
            "ID": vcell_clause_id,
            "text": vcell_clause_text.lower(),
        })


# Classify clauses
print(str(len(vclauses)))
print(str(len(vres)))
vpreds = classifier.classify_clauses(vclauses)
print(str(len(vpreds)))

# print(vclauses)

# Create output CSV file
vcsv = 'Clause ID,Prediction,Probability Acceptable'
for i in range(len(vpreds)):
    vcsv += '\n"%s","%s","%s"' % (
        vres[i]["ID"], vpreds[i]["acceptable"], vpreds[i]["confidence"]) 


open("AnikaSystems Validation Data File.csv", "w+").write(vcsv)