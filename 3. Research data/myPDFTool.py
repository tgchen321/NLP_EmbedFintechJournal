# import PyPDF2 as pdf
import fitz, pickle, re
########### keep edit: line 81

def pdf2text(IFileName, journal):
    pdf_document = fitz.open(IFileName)

    plainText = ""
    references = [{}]
    referenceStart = False
    for pageNum in range(pdf_document.page_count):
        page = pdf_document.load_page(pageNum)

        # plainText += "\n\n-------- page: " + str(pageNum) + ", " + str(len(page.get_text("blocks"))) + " blocks --------\n\n"
        # print("-- PAGE " + str(pageNum) + "--")
        # print(page.get_text("dict")["width"])
        # print(page.get_text("dict")["height"])
        for block in page.get_text("dict")["blocks"]:

            # escape images
            if block["type"] == 1: continue

            # # main content
            for line in block["lines"]:
                thisLine = False
                for span in line["spans"]:
                    if MainContentCheck(span, journal): 
                        plainText += span["text"]
                        thisLine = True
                        lastChar = span["text"][-1]
                    elif not referenceStart: 
                        referenceStart = ReferenceCheck(span, journal)
                    else:
                        references = FormatReference(span, references, journal)
                        
                # hyphenation of words (break into 2 parts)
                if thisLine: 
                    if lastChar == "-": plainText = plainText[0:-1]
                    else: plainText += " "

            # plainText += "\n"

            # debug: whole picture of PDF contents
            # for key, value in block.items():
            #     plainText += "# " + key + "\n"
            #     plainText += str(value)
            #     plainText += "\n"
            
    text_file = open(IFileName[:-4] + ".txt", "w", encoding="utf-8")
    text_file.write(plainText)
    text_file.close()


def MainContentCheck(span, journal):
    if journal == "IEEEaccess":
        if round(span["size"], 3) != 9.963 or span["color"] != 0:
            return False
        if span["font"] == "TimesLTStd-Roman" or span["font"] == "TimesLTStd-Italic":
            return True

def ReferenceCheck(span, journal):
    if journal == "IEEEaccess":
        if round(span["size"], 3) == 8.966 and span["font"] == "FormataOTF-Bold" and span["color"] == 29358 and span["text"] == "REFERENCES":
            return True
        else: return False

def FormatReference(span, references, journal):
    text = span["text"]
    number = re.search(r"z[[0-9]+\]", text)
    startTitle = text.find("‘‘")
    endTitle = text.find(",’’")

    if journal == "IEEEaccess":    
        # add new reference
        if number is not None:
            if int(number[0][1:-1]) is not len(references):
                print ("######### ERROR: incorrect reference order")
                return 0
            references.append({"id": len(references), "title": "", "journal": ""})
        
        # add reference title
        ##################### start here, create 2 flags for title start and title end, in case of long titles more than 3 lines
        if startTitle > 0:
            if endTitle > 0:
                references[-1]["title"] += text[startTitle+2: endTitle]
            else: 
                if text[-1] == "-": 
                    references[-1]["title"] += text[startTitle+2: -1]
                else: 
                    references[-1]["title"] += text[startTitle+2: ]
                    references[-1]["title"] += " "
        elif endTitle > 0:
            references[-1]["title"] += text[0: endTitle]
        
        # add journal title
        if span["font"] == "TimesLTStd-Italic" and round(span["size"], 3) == 7.582:
            references[-1]["journal"] += text


            
            



pdf2text("test/Abbas-2021-Securing Genetic Algorithm Enabled.pdf", "IEEEaccess")
                            


# def CheckContentStart(block, journal):
#     if journal == "IEEEaccess":
#         if "ABSTRACT" in block[4]:
#             print("Start content")
#             return True
#         else: return False

# def CheckEscape(block, journal):
#     if journal == "IEEEaccess":
#         if block[5] == 0: 
#             # print("Escape:\theader-1")
#             return True
#         if block[5] == 1: 
#             # print("Escape:\theader-2")
#             return True
#         if "VOLUME" in block[4]:
#             # print("Escape:\tfooter")
#             return True
#         if block[4][0:6] == "FIGURE":
#             # print("Escape:\tfigure")
#             return True
#         if block[4][0:5] == "TABLE":
#             # print("Escape:\ttable")
#             return True
#         if "The associate editor coordinating" in block[4]:
#             # print("Escape:\teditor review (1st page left bottom corner)-1")
#             return True
#         if "approving it for publication was" in block[4]:
#             # print("Escape:\teditor review (1st page left bottom corner)-2")
#             return True
#         # if block[4][1:9] == "https://" or block[4][1:8] == "http://":
#         #     print("Escape:\tfootnote www address")
#         #     return True
#         if "<image: " in block[4]:
#             # print("Escape:\timage label")
#             return True
#         else: return False

# def pdf2text(fileName):

#     # check file name
#     if fileName[-4:] == ".pdf": 
#         fileName = fileName[:-4]
#         #print(fileName)

#     # read pdf
#     reader = pdf.PdfReader(fileName + ".pdf")
#     plainText = ""
#     for pageNum in range(len(reader.pages)):
#         #print(pagepageNum)
#         page = reader.pages[pageNum]
#         page = RemoveSentence(page, "")
#         plainText += "\n\n\n----------------------------------------------------\n\n\n"
#         plainText += page.extract_text()

#     # save to txt
#     text_file = open(fileName + ".txt", "w", encoding="utf-8")
#     text_file.write(plainText)
#     text_file.close()

# crop page to remove footer and header
# def CropPDF(IFileName, OFileName, journal):

#     pdfReader = pdf.PdfReader(IFileName)
#     pdfWriter = pdf.PdfWriter()

#     # (footer height, header height)
#     mapJournalheights = {"IEEEaccess": (0.3, 0.3)} 

#     page = pdfReader.pages[0]
#     mediaBox = page.mediabox
#     x1, y1 = mediaBox.lower_left
#     x2, y2 = mediaBox.upper_right
#     footerHeight = round(float(y2 - y1) * mapJournalheights[journal][0], 3)
#     headerHeight = round(float(y2 - y1) * mapJournalheights[journal][1], 3)

#     for pageNum in range(len(pdfReader.pages)):
#         page = pdfReader.pages[pageNum]

#         page.mediabox.lower_left = (x1, float(y1) + footerHeight)
#         page.mediabox.upper_right = (x2, float(y2) - headerHeight)
#         #print("cropped lowerleft: " + str(page.mediabox.lower_left))
#         pdfWriter.add_page(page)

#     with open(OFileName, 'wb') as outputFile:
#         pdfWriter.write(outputFile)

# def RemoveSentence(page, key):
#     if len(key) == 0: return page
#     for line in page:
#         if key in line:
#             print("!! remove sentence: " + line)
#             page.remove(line)
#     return page