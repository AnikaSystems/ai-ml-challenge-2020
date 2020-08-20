# -*- coding: utf-8 -*-
# pdf_to_string.py - Convert PDF file into a string

import pdf_to_png
import sys
import os
from PIL import Image
from pytesseract import image_to_string
import io
import re
import unicodedata


def remove_control_characters(s):
    s = s.replace("\n", "        ")
    s = "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")
    return s.replace("        ", "\n")


def removeNonAscii(s): 
    return "".join(filter(lambda x: ord(x)<128, s))


def pdf_to_string(vpdf):
    # Return array of clauses in PDF.
    print("[* pdf_to_string] Parse %s into clauses..." % vpdf)
    vres = []

    # Convert to image(s)
    print("[* pdf_to_string] Converting to image(s)...")
    vimages = pdf_to_png.pdf2png(vpdf) 

    # OCR extract text from EULA image.
    vtext_all = ""
    print("[* pdf_to_string] OCR extract text...")
    for vpath in vimages:
        vtext = image_to_string(Image.open(vpath), lang='eng', config='-c preserve_interword_spaces=1')
        vtext_all += vtext + "\n\n"
        os.remove(vpath)

    # Remove control characters.
    vtext_all = remove_control_characters(vtext_all).strip()
    vtext_all = vtext_all.replace(u'\ufffd', ' ') 
    vtext_all = removeNonAscii(vtext_all)

    # Write output
    with io.open("output.txt", "w+") as f:
        f.write(vtext_all)

    # Parse clauses
    # Delimeters covered:
    #   10.10
    #   10.10.
    #   10..
    #   A.
    #   XIV.
    #   A)
    #   (10)
    #   (A)
    #   e (bullet point)

    print("[* pdf_to_string] Regex parser...")

    #vclauses = re.split(
    #    r'\n\s{0,}((\d{1,}\.\d{0,}\.{0,1})|([A-z]{1}\.)|([i,v,I,V,x,X]{1,}\.)|([A-z]{1}\))|(\(\d{1,}\))|(e)|(\([A-z]\)))\s{1,}',
    #    vtext_all)

    vclauses = vtext_all.split("\n\n")

    # Remove clauses file if exists already
    try: os.remove("clauses.txt")
    except: pass

    # Format and write clauses to output file (for debugging).
    with open("clauses.txt", "a+") as f:
        for vclause in vclauses:
            if vclause is None: continue
            if len(vclause.strip()) < 3: continue
            if len(vclause.split(" ")) < 3: continue
            vclause = vclause.replace("�", ' ')
            vclause = vclause.strip().replace("\n", " ")
            f.write(vclause)
            f.write("\n\n" + ("*"*64) + "\n\n")
            
            # Append clause to final results.
            vres.append(vclause)

    f.close()

    print("[* pdf_to_string] Parsing completed.")

    # Return array of clauses.
    return {
        "clauses": vres,
        "text": vtext_all
    }


if __name__ == "__main__":
    # DEBUG
    
    if len(sys.argv) < 2:
        print("[*] Usage: pdf_to_string <PDF path>")
        sys.exit()

    import mongo
    import datetime

    vpdf = sys.argv[1]
    vparsed = pdf_to_string(vpdf)

    # Add to mongo queue for testing
    vbytes = open(vpdf, "rb").read()

    # Queue structure:
    """vqueue_item = {
        "fname": vpdf.split("\\")[-1],
        "eula_text": vparsed["text"],
        "clauses": vparsed["clauses"],
        "upload_time": str(datetime.datetime.now()),
        "completed": 0,
        "bytes": vbytes,
    }"""

    # Add to mongo queue db for processing.
    # vres = mongo.queue_add(vqueue_item)