# pdf2png.py - Convert a PDF into images.
from pdf2image import convert_from_path
import os

def pdf2png(vstr_pdf_path):
    # Convert pdf to images.
    vimages = convert_from_path(vstr_pdf_path, 500) # Array of pages.
    vpaths = []

    i = 0
    for vpage in vimages:
        vstr_image_path = ".".join(vstr_pdf_path.split(".")[0:-1])+"_page_%s.png" % i
        vstr_image_path = os.path.abspath(vstr_image_path)
        # print("[* pdf2png] Converted image path: [%s]" % vstr_image_path)
        vpage.save(vstr_image_path, "PNG")
        vpaths.append(vstr_image_path)
        #  voutdir + os.path.sep + 
        i+=1
    
    return vpaths


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("[* pdf2png] Usage: python pdf2png <PDF PATH>")
        sys.exit()
    else:
        pdf2png(sys.argv[1])