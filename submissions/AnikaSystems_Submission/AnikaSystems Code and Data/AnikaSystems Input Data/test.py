# -*- coding: utf-8 -*-
import unicodedata

def remove_control_characters(s):
    s = s.replace("\n", "        ")
    s = "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")
    return s.replace("        ", "\n")


def f():
    vtext = open("sample.txt", "r", encoding='utf-8').read()
    # vtext = vtext.replace("\\n", "\n")
    vtext = remove_control_characters(vtext)
    print(vtext)


def removeNonAscii(s): return "".join(filter(lambda x: ord(x)<128, s))


vstr = open("output.txt", "r").read()
# vstr = vstr.replace("�", "")
vstr = removeNonAscii(vstr)
open("output.txt", "w").write(vstr)

#for vline in vtext.split("\\n"):
#    print(vline)