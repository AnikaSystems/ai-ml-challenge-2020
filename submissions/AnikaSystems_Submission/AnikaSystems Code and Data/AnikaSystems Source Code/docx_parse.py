# docx_parse.py - Convert docx into PDF.

import uuid
import pythoncom
import win32com.client
import os
from pathlib import Path
import docx
import time


def docx_to_pdf(vdoc_name):
    "Return document content and return PDF binary data."

    vdoc_name = os.path.abspath(vdoc_name)

    # Create tmp PDF path.
    vtmp_pdf = os.path.abspath("tmp_%s.pdf" % str(uuid.uuid4())) 

    # Convert docx to tmp PDF
    print("[* docs_search] Convert to PDF...Create comtypes client...")
    pythoncom.CoInitialize()
    vword = win32com.client.Dispatch('Word.Application')
    print("[* docs_search] Convert to PDF...Open word doc...")
    vdoc = vword.Documents.Open(vdoc_name)
    print("[* docs_search] Convert to PDF...Save as PDF...")
    vdoc.SaveAs(vtmp_pdf, FileFormat=17)
    print("[* docs_search] Convert to PDF...Close file pointers...")
    vdoc.Close()
    vword.Quit()

    # Return path name to caller.
    return vtmp_pdf


if __name__ == "__main__":
    docx_to_pdf("sample_eula_1.docx")