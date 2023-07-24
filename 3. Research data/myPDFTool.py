# import PyPDF2 as pdf
import fitz

def pdf2text(IFileName, journal):
    pdf_document = fitz.open(IFileName)

    plainText = ""
    contentStart = False
    for pageNum in range(pdf_document.page_count):
        page = pdf_document.load_page(pageNum)

        plainText += "\n\n-------- page: " + str(pageNum) + ", " + str(len(page.get_text("blocks"))) + " blocks --------\n\n"
        print("-- PAGE " + str(pageNum) + "--")
        for block in page.get_text("blocks"):
            plainText += "\n-------- block " + str(block[5]) + " --------\n"
            if pageNum == 0 and not contentStart: 
                contentStart = CheckContentStart(block, journal)
            if not contentStart: continue
            if CheckEscape(block, journal): continue
            #print(block)
            plainText += block[4]
            
    text_file = open(IFileName[:-4] + ".txt", "w", encoding="utf-8")
    text_file.write(plainText)
    text_file.close()


def CheckContentStart(block, journal):
    if journal == "IEEEaccess":
        if "ABSTRACT" in block[4]:
            print("Start content")
            return True
        else: return False

def CheckEscape(block, journal):
    if journal == "IEEEaccess":
        if block[5] == 0: 
            print("Escape:\theader-1")
            return True
        if block[5] == 1: 
            print("Escape:\theader-2")
            return True
        if "VOLUME" in block[4]:
            print("Escape:\tfooter")
            return True
        if block[4][0:6] == "FIGURE":
            print("Escape:\tfigure")
            return True
        if block[4][0:5] == "TABLE":
            print("Escape:\ttable")
            return True
        if "The associate editor coordinating" in block[4]:
            print("Escape:\teditor review (1st page left bottom corner)-1")
            return True
        if "approving it for publication was" in block[4]:
            print("Escape:\teditor review (1st page left bottom corner)-2")
            return True
        else: return False





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