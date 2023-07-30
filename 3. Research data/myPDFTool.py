# import PyPDF2 as pdf
import fitz, pickle, re
#### sustainability one file test OK
#### next: run testing file

def pdf2text(IFileName, journal):
    PDFDocument = fitz.open(IFileName)
    
    plainText = ""
    references = [{"id": 0, "title": "", "journal": ""}]
    section = "main" # "main" -> "reference" -> "done"
    longTitle = False
    for pageNum in range(PDFDocument.page_count):
        page = PDFDocument.load_page(pageNum)

        print("-- PAGE " + str(pageNum) + "--")
        # print(page.get_text("dict")["width"])
        # print(page.get_text("dict")["height"])
        for block in page.get_text("dict")["blocks"]:
            # print("-- block " + str(block["number"]) + "--")
            # escape images
            if block["type"] == 1: continue

            # main content
            for line in block["lines"]:
                thisLine = ""
                for span in line["spans"]:
                    section = SectionCheck(section, span, journal)
                    if section == "done": break
                    if section == "main" and MainContentCheck(span, journal):
                            thisLine += span["text"]

                    elif section == "reference": 
                        references, longTitle = FormatReference(span, longTitle, references, journal)
                        section = ReferenceEnd(span, journal)
                        
                # hyphenation of words (break into 2 parts)
                if len(thisLine) > 0: 
                    plainText += EndOfLine(thisLine)
            # plainText += "\n"

            # debug: whole picture of PDF contents
            # for key, value in block.items():
            #     plainText += "# " + key + "\n"
            #     plainText += str(value)
            #     plainText += "\n"

    with open(IFileName[:-4] + ".txt", "w", encoding="utf-8") as textFile:
        textFile.write(plainText)
    with open(IFileName[:-4] + ".pkl", "wb") as pkl:
        pickle.dump(references, pkl)
    # unpickling
    # with open(IFileName[:-4] + ".pkl", "rb") as pkl:
    #     references = pickle.load(pkl)


def MainContentCheck(span, journal):
    if journal == "IEEEaccess":
        if round(span["size"], 3) != 9.963 or span["color"] != 0:
            return False
        if span["font"] == "TimesLTStd-Roman" or span["font"] == "TimesLTStd-Italic":
            return True
    
    if journal == "sustain2016":
        if (span["size"] > 9.5 and span["size"] < 10.5) and span["font"] == "URWPalladioL-Roma":
            # print("#### pass content check")
            return True

    return False


def SectionCheck(section, span, journal):
    scan = ""
    if journal == "IEEEaccess":
        if round(span["size"], 3) == 8.966 and span["font"] == "FormataOTF-Bold" and span["color"] == 29358:
            # connect several lines of chapter title
            if section[-1] == "-": 
                scan = section[:-1] + span["text"]
            else: 
                scan = span["text"]
            
            if "APPENDIX" in scan:
                return "appendix-"
            if scan == "REFERENCES":
                return "reference-"   
        elif section[-1] == "-":
            return section[:-1]
    
    if journal == "sustain2016":
        if round(span["size"], 3) == 9.963 and span["font"] == "URWPalladioL-Bold":
            if section[-1] == "-": 
                scan = section[:-1] + span["text"]
            else: 
                scan = span["text"]
            
            if "Appendix" in scan:
                return "appendix-"
            if scan == "References":
                print("#### REFERENCE START")
                return "reference-"   
        elif section[-1] == "-":
            return section[:-1]
    return section




def ReferenceEnd(span, journal):
    if journal == "IEEEaccess":
        if round(span["size"], 3) == 7.97 and span["font"] == "FormataOTFMd":
            return "done"
    return "reference"


def FormatReference(span, longTitle, references, journal):
    text = span["text"]
    number = None
    startTitle = -1
    endTitle = -1
    journalName = ""
    addJournal = False
    addTitle = False

    if journal == "IEEEaccess":
        if (span["font"] != "TimesLTStd-Roman" or span["font"] != "TimesLTStd-Italic") and round(span["size"], 3) != 7.582:
            return references, longTitle

        if (span["origin"][0] > 278 and span["origin"][0] < 305) or span["origin"][0] < 44: 
            number = re.search(r"\[[0-9]+\]", text)

        if number is not None: 
            number = int(number[0][1:-1])

        startTitle = text.find("‘‘")
        endTitle = text.find("’’")
        addTitle = True

        if span["font"] == "TimesLTStd-Italic":
            journalName = EndOfLine(text)
        if len(journalName) > 0: addJournal = True
    
    if journal == "sustain2016":
        if "URWPalladioL" not in span["font"] or span["size"] < 8.5 or span["size"] > 9.5:
            return references, longTitle

        if round(span["origin"][0], 3) == 36:
            number = int(text[:-1])
            # print("new ref: " + str(number))
        
        elif span["font"] == "URWPalladioL-Roma" and len(references[-1]["journal"]) == 0:
            addTitle = True
            # print("add title: " + text)
            if not longTitle:
                startTitle = text.find(". ")
                endTitle = text[startTitle+2:].find(". ")
                if endTitle > 0: endTitle += startTitle + 2
            else: 
                endTitle = text.find(". ")
            
            # print("---start from: " + str(startTitle))
            # print("---to: " + str(endTitle))
        
        elif span["font"] == "URWPalladioL-Ital":
            # print("add journal: " + text)
            addJournal = True
            journalName = EndOfLine(text)
            longTitle = False



    # add new reference
    if number is not None:
        if number != references[-1]["id"] + 1:
            print ("######### ERROR: incorrect reference order")
            print("detected reference number: " + str(number) + ", len(reference list): " + str(len(references)))
            return 0
        else:
            references.append({"id": len(references), "title": "", "journal": ""})
        # print (references[-1])
    
    # add reference title
    if addTitle:
        if longTitle:
            if endTitle >= 0:
                references[-1]["title"] += text[0: endTitle]
                longTitle = False
            else: 
                references[-1]["title"] += EndOfLine(text)
                longTitle = True
        else:
            if startTitle >= 0 and endTitle >= 0:
                references[-1]["title"] += text[startTitle+2: endTitle]
                longTitle = False
            elif startTitle >= 0 and endTitle < 0:
                if startTitle + 2 < len(text): 
                    references[-1]["title"] += EndOfLine(text[startTitle+2:])
                longTitle = True
        # print(references[-1]["title"])
    
    # add journal name
    if addJournal: references[-1]["journal"] += journalName

    # print("long title: " + str(longTitle))
    return references, longTitle

def EndOfLine(text):
    if text[-1] == "-": 
        text = text[:-1]
    else:
        text += " "
    return text


pdf2text("test_sustain2016/Adamashvili-2021-Blockchain-Based Wine Supply.pdf", "sustain2016")
with open("test_sustain2016/Adamashvili-2021-Blockchain-Based Wine Supply.pkl", "rb") as pkl:
    references = pickle.load(pkl)
for ref in references:
    for key, value in ref.items():
        print(key + "\t" + str(value))
                            


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