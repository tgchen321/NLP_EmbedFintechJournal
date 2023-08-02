# import PyPDF2 as pdf
import fitz, pickle, re, os
####### manage to put the main content of the reference paper and its citaiton sentences in the same place

def pdf2text(IFileName, journal):
    PDFDocument = fitz.open(IFileName)
    
    plainText = ""
    references = [{"id": 0, "title": "", "journal": ""}]
    section = "main" # "main" -> "reference" -> "done"
    longTitle = False
    for pageNum in range(PDFDocument.page_count):
        page = PDFDocument.load_page(pageNum)

        # print("-- PAGE " + str(pageNum) + "--")
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
        # if pageNum == 1: break

    with open(IFileName[:-4] + ".txt", "w", encoding="utf-8") as textFile:
        textFile.write(plainText)
    with open(IFileName[:-4] + ".pkl", "wb") as pkl:
        pickle.dump(references, pkl)
    # unpickling
    # with open(IFileName[:-4] + ".pkl", "rb") as pkl:
    #     references = pickle.load(pkl)


def MainContentCheck(span, journal):
    if journal == "IEEEaccess":
        if round(span["size"], 3) != 9.963:
            # print(span["color"])
            # print(span["text"])
            return False
        if span["font"] == "TimesLTStd-Roman" or span["font"] == "TimesLTStd-Italic":
            # print("#### pass content check")
            return True
    
    if journal == "Sustainability":
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
    
    if journal == "Sustainability":
        if round(span["size"], 3) == 9.963 and span["font"] == "URWPalladioL-Bold":
            if section[-1] == "-": 
                scan = section[:-1] + span["text"]
            else: 
                scan = span["text"]
            
            if "Appendix" in scan:
                return "appendix-"
            if scan == "References":
                # print("#### REFERENCE START")
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
    
    if journal == "Sustainability":
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
            references.append({"id": len(references), "title": "", "journal": "", "sentences": []})
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


def CitationSentence(IFileName):
    count = 0
    with open(IFileName, "rb") as textFile:
        text = str(textFile.read())
    with open(IFileName[0:-4] + ".pkl", "rb") as pkl:
        references = pickle.load(pkl)
    sentences = re.split(r'(?<=\D)\.(?=.)|(?<=\d)\.(?=\D)', text)
    citeSents = []
    for sentence in sentences:

        # citation numbers
        citeNums = []
        citations = re.findall(r'\[[0-9]+\]', sentence)
        if len(citations) > 0:
            for num in citations:
                citeNums.append(int(num[1:-1]))
        groupOfCites = re.findall(r'\[[0-9]+[-][0-9]+\]', sentence)
        if len(groupOfCites) > 0:
            for group in groupOfCites:
                tmp = group.split("-")
                start = int(tmp[0][1:])
                end = int(tmp[1][:-1])
                citeNums += list(range(start, end+1))

        # extract citation sentences
        if len(citeNums) > 0:
            # debug: convert special characters utf-8
            sentence = Unicode2Str(sentence)
            if "\\" in sentence: print(sentence)

            # serialisation
            citeSents.append(sentence)

            # match bibliography (dictionary) and citation sentence
            removeBrackets = re.sub(r'\[[0-9]+[-]?[0-9]*\]', '', sentence)
            # print(removeBrackets)
            for citeNum in citeNums:
                # print(citeNum)
                if citeNum >= len(references): continue
                if "sentences" not in references[citeNum].keys():
                    references[citeNum]["sentences"] = []
                references[citeNum]["sentences"].append(removeBrackets)
                count += 1

    with open(IFileName[:-4] + "_citeSents.pkl", "wb") as pkl:
        pickle.dump(citeSents, pkl)
    with open(IFileName[:-4] + ".pkl", "wb") as pkl:
        pickle.dump(references, pkl)
    
    return count


def MatchRefFile(IFileName, repoFolder):

    dirList = {}
    for scanFile in os.listdir(repoFolder):
        if os.path.isdir(os.path.join(repoFolder, scanFile)):
            dirList[scanFile.lower()] = scanFile
    # print(dirList)

    with open(IFileName, "rb") as pkl:
        references = pickle.load(pkl)
    for ref in references:
        folder = ref["journal"].lower().replace(" ", "")
        # print(folder)
        filename = ref["title"].lower()
        if folder not in dirList.keys(): continue
        print("find: " + filename)
        for scanner in os.listdir(os.path.join(repoFolder, dirList[folder])):
            if re.findall(r'[\S]+' + filename[0:20] + r'[\S\s]+' + ".txt", scanner.lower()):
                print(scanner)
    ############ keep edit here





def Unicode2Str(str):
    str = re.sub(r'\\xc2\\x[ab][0-9a-f]', '', str)
    str = re.sub(r'\\xc3\\x[8a][0-6]', 'a', str)
    str = re.sub(r'\\xc3\\x[8a]7', 'c', str)
    str = re.sub(r'\\xc3\\x[8a][89ab]', 'e', str)
    str = re.sub(r'\\xc3\\x[8a][c-f]', 'i', str)
    str = re.sub(r'\\xc3\\x[9b][0]', 'd', str)
    str = re.sub(r'\\xc3\\x[9b][1]', 'n', str)
    str = re.sub(r'\\xc3\\x[9b][2-68]', 'o', str)
    str = re.sub(r'\\xc3\\x[9b]7', '', str)
    str = re.sub(r'\\xc3\\x[9b][9a-c]', 'u', str)
    str = re.sub(r'\\xc3\\x[9b]d', 'y', str)
    str = re.sub(r'\\xc3\\x[9b]e', 'p', str)
    str = re.sub(r'\\xc3\\x[9b]f', 's', str)
    str = re.sub(r'\\xc4\\x8[0-5]', 'a', str)
    str = re.sub(r'\\xc4\\x8[6-9a-d]', 'c', str)
    str = re.sub(r'\\xc4\\x8[ef]', 'd', str)
    str = re.sub(r'\\xc4\\x9[01]', 'd', str)
    str = re.sub(r'\\xc4\\x9[2-9ab]', 'e', str)
    str = re.sub(r'\\xc4\\x9[c-f]', 'g', str)
    str = re.sub(r'\\xc4\\xa[0-3]', 'g', str)
    str = re.sub(r'\\xc4\\xa[4-7]', 'h', str)
    str = re.sub(r'\\xc4\\xa[89a-f]', 'i', str)
    str = re.sub(r'\\xc4\\xb[01]', 'i', str)
    str = re.sub(r'\\xc4\\xb[23]', '', str)
    str = re.sub(r'\\xc4\\xb[45]', 'j', str)
    str = re.sub(r'\\xc4\\xb[6-8]', 'k', str)
    str = re.sub(r'\\xc4\\xb[9a-f]', 'l', str)
    str = re.sub(r'\\xc5\\x8[0-2]', 'l', str)
    str = re.sub(r'\\xc5\\x8[3-9ab]', 'n', str)
    str = re.sub(r'\\xc5\\x8[c-f]', 'o', str)
    str = re.sub(r'\\xc5\\x9[01]', 'o', str)
    str = re.sub(r'\\xc5\\x9[23]', 'oe', str)
    str = re.sub(r'\\xc5\\x9[4-9]', 'r', str)
    str = re.sub(r'\\xc5\\x9[a-f]', 's', str)
    str = re.sub(r'\\xc5\\xa[01]', 's', str)
    str = re.sub(r'\\xc5\\xa[2-7]', 't', str)
    str = re.sub(r'\\xc5\\xa[89a-f]', 'u', str)
    str = re.sub(r'\\xc5\\xb[0-3]', 'u', str)
    str = re.sub(r'\\xc5\\xb[45]', 'w', str)
    str = re.sub(r'\\xc5\\xb[6-8]', 'y', str)
    str = re.sub(r'\\xc5\\xb[9a-e]', 'z', str)
    str = re.sub(r'\\xc[bc]\\x[89ab][0-9a-f]', '', str)
    str = re.sub(r'\\xe2\\x80\\x9[89ab]', '\'', str)
    str = re.sub(r'\\xe2\\x80\\x9[c-f]', '\'\'', str)
    str = re.sub(r'\\xe2\\x80\\x9[1-5]', '\'\'', str)
    str = str.replace("\\xef\\xac\\x80", "ff")
    str = str.replace("\\xef\\xac\\x81", "fi")
    str = str.replace("\\xef\\xac\\x82", "fl")
    str = str.replace("\\xef\\xac\\x83", "ffi")
    str = str.replace("\\xef\\xac\\x84", "ffl")
    str = re.sub(r'\\xef\\xac\\x8[56]', 'st', str)
    return str


# pdf2text("test/Nizamani-2021-A Novel Hybrid Textual-Graphical.pdf", "IEEEaccess")
# with open("IEEEaccess/Hu-2019-Collaborative Optimization of Distribu.pkl", "rb") as pkl:
#     references = pickle.load(pkl)
# for ref in references:
#     for key, value in ref.items():
#         print(key + "\t" + str(value))

# CitationSentence("IEEEaccess/Hu-2019-Collaborative Optimization of Distribu.txt")
# with open("IEEEaccess/Hu-2019-Collaborative Optimization of Distribu.pkl", "rb") as pkl:
#     CiteSents = pickle.load(pkl)
# for sent in CiteSents:
#     print(sent)

MatchRefFile("IEEEaccess/Abbas-2021-Securing Genetic Algorithm Enabled.pkl", "./")