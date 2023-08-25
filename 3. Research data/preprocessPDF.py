import os, pickle, math
# from pathlib import Path
# import myPDFTool
import myNLPTool, csv
import numpy as np
from matplotlib import pyplot as plt
import fasttext


# move PDFs out from folders
def BatchMovePDF(targetFolder):
	cwd = str(os.getcwd())
	for root, dirs, files in os.walk(targetFolder):
		# root: (string) 'test\0001864237'
		# dirs: list []
		# files (list) ['Podolchak-2022-UKRAINIAN ECOSYSTEM TRANSFORMAT.pdf']

		if len(dirs) == 0 and len(files) > 0:
			before = Path(cwd).joinpath(root, files[0])
			# ....\test\0001864237\Nasir-2021-Trends and Directions of Financial.pdf
			after = Path(cwd).joinpath(targetFolder, files[0])
			# ....\test\Nasir-2021-Trends and Directions of Financial.pdf
			# print (before)
			# print (after)
			os.rename(before, after)
			print("Rename:\t" + files[0][0:-4] + "...")


# convert PDFs to plain texts
def BatchPDF2text(targetFolder, journal):
	for file in os.listdir(targetFolder):
		if not file.endswith((".pdf")): continue

		myPDFTool.pdf2text(str(Path(targetFolder).joinpath(file)), journal)
		print("Plain: \t" + file[0:-4] + "...")


def BatchCitationSentence(targetFolder):
	citeCount = {}
	for file in os.listdir(targetFolder):
		if not file.endswith((".txt")): continue
		
		citeCount[file[0:-4]] = myPDFTool.CitationSentence(str(Path(targetFolder).joinpath(file)))
		print("Sentences: \t" + file[0:-4] + "...")
	return citeCount

def BatchMatchReferenceFile(targetFolder, repoFolder):

	dataset = []
	for file in os.listdir(targetFolder):
		if not file.endswith((".pkl")): continue
		if file.endswith(("_citeSents.pkl")): continue

		[refNum, FullTextNum, dataset] = myPDFTool.MatchRefFile(str(Path(targetFolder).joinpath(file)), repoFolder, dataset)
		print("Match: \t" + file[0:-4] + "...")
		print("-----> " + str(FullTextNum) + " out of " + str(refNum) + " txt files are found")
	return dataset

def Evaluation(result, fileName):
	print("# RESULTS: ")
	print(str(len(result)) + " pairs of citation sentence-reference article")
	result.sort(reverse = True)
	print("Maximum similarity(cosine sim.): " + str(result[0]))
	print("Minimum similarity(cosine sim.): " + str(result[-1]))
	print("Average similarity(cosine sim.): " + str(np.mean(result)))
	print("standard Deviation (cosine sim.): " + str(np.std(result)))

	# if len(result) > 10:
	# 	top10 = math.ceil(len(result)/10)
	# 	print("Top 10% average similarity(cosine sim.): " + str(sum(result[:top10])/top10))
	# 	_, ax = plt.subplots(figsize =(10, 7))
	# 	ax.hist(result)
	# 	plt.show()
	result = np.reshape(result, (-1, 1))
	with open(fileName, 'w') as csvfile: 
		csvwriter = csv.writer(csvfile) 
		csvwriter.writerows(result)
	print()

if __name__ == "__main__":
	# targetFolder = "IEEEaccess"
	# journal = targetFolder
	# repoFolder = "."
	# BatchMovePDF(targetFolder)
	# BatchPDF2text(targetFolder, journal)
	# dictionary = BatchCitationSentence(targetFolder)
	# count = dictionary.values()
	# for key, value in dictionary.items():
	# 	print(key + ":\t" + str(value))
	# print("Average citation sentences: " + str(sum(count)/len(count)))
	# print("Maximum citation sentences: " + str(max(count)))
	# print("Minimum citation sentences: " + str(min(count)))
	# dataset = BatchMatchReferenceFile(targetFolder, repoFolder)
	# print("---> " + str(len(dataset)) + " records (data)")
	# with open("dataList.pkl", "wb") as pkl:
	# 	pickle.dump(dataset, pkl)

	# print("## Read dataset")
	# with open("dataList.pkl", "rb") as pkl:
	# 	dataset = pickle.load(pkl)
	# print(len(dataset))

	# print("## Tokenise")
	# listOfTargetSents = []
	# listOfTargetWords = []
	# listOfWholeFileInWords = []
	# listOfQueryWords = []
	# for dict in dataset:
	# 	targetSents, targetWords, wholeFileInWords = myNLPTool.Tokenise(dict["fullText"])
	# 	_, _, queryWords = myNLPTool.Tokenise(dict["citeSent"])
	# 	listOfTargetSents.append(targetSents)
	# 	listOfTargetWords.append(targetWords)
	# 	listOfWholeFileInWords.append(wholeFileInWords)
	# 	listOfQueryWords.append(queryWords)
	# 	if len(listOfTargetSents)%100 == 0:
	# 		tmp = math.floor(len(listOfTargetSents)/100)
	# 		print("# " + str(tmp) + "00 - " + str(tmp+1) + "00...")
	# with open("targetSentences.pkl", "wb") as pkl:
	# 	pickle.dump(listOfTargetSents, pkl)
	# with open("targetWords.pkl", "wb") as pkl:
	# 	pickle.dump(listOfTargetWords, pkl)
	# with open("wholeFileIntoWords.pkl", "wb") as pkl:
	# 	pickle.dump(listOfWholeFileInWords, pkl)
	# with open("queryWords.pkl", "wb") as pkl:
	# 	pickle.dump(listOfQueryWords, pkl)

	print("## Read dataset")
	with open("targetWords.pkl", "rb") as pkl:
		listOfTargetWords = pickle.load(pkl)
	with open("queryWords.pkl", "rb") as pkl:
		listOfQueryWords = pickle.load(pkl)

	print("## Concate dataset")
	corpus = []
	idList = []
	idCurrent = 0
	for targetWords, queryWords in zip(listOfTargetWords, listOfQueryWords):
		corpus += targetWords
		targetID = list(range(idCurrent, idCurrent + len(targetWords)))
		idCurrent += len(targetWords)
		corpus.append(queryWords)
		idList.append({"fullText": targetID, "citeSent": [idCurrent]})
		idCurrent += 1
		
	# plainText = ""
	# for dict in dataset:
	# 	plainText += dict["fullText"]
	# 	plainText += "\n"
	# 	plainText += dict["citeSent"]
	# 	plainText += "\n"
	# with open("FastTextInput.txt", "w", encoding="utf-8") as textFile:
	# 	textFile.write(plainText)
	# api_token = "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"
	# (mCBOW, mSkipGram) = myNLPTool.TrainWord2Vec(targetWords, "word2vec")
	# mCBOW = fasttext.load_model("fastText_CBOW.model")
	# mSkipGram = fasttext.load_model("fastText_SG.model")
	# (mCBOW, mSkipGram) = myNLPTool.TrainFastText("FastTextInput.txt", "fastText")


	# print("### TFIDF - sent. embed.: ")
	# TFIDFmodel = myNLPTool.TrainTFIDF(corpus) #TFIDFMatrix, BoWCorpus, num_terms
	# with open("TFIDFmodel.pkl", "wb") as pkl:
	# 	pickle.dump(TFIDFmodel, pkl)
	# with open("TFIDFmodel.pkl", "rb") as pkl:
	# 	TFIDFmodel = pickle.load(pkl)
	# (TFIDFMatrix, _, _, _, num_terms) = TFIDFmodel
	# Evaluation(myNLPTool.ApplyTFIDF(TFIDFMatrix, num_terms, corpus, idList), "TFIDF_overall_performance.csv")

	print("### LSA - sent. embed.: ")
	with open("TFIDFmodel.pkl", "rb") as pkl:
		TFIDFmodel = pickle.load(pkl)
		(TFIDFMatrix, _, dictionary, num_docs, num_terms) = TFIDFmodel
	Evaluation(myNLPTool.ApplyLSA(corpus, TFIDFMatrix, dictionary, num_docs, num_terms)) # Coherence Score: 0.25487534698403475

	# SENTENCE EMBEDDING
	 #0.228|0.077|0.014
	
	# mCBOW = Word2Vec.load("test" + "_CBOW.model")
	# print("### Word2Vec - CBOW - sent. embed.: ")
	# Evaluation(myNLPTool.SimWord2Vec(mCBOW, queryWords, targetWords)) #0.994|0.991|0.978
	# mSkipGram = Word2Vec.load("test" + "_SG.model")
	# print("### Word2Vec - SkipGram - sent. embed.: ")
	# Evaluation(myNLPTool.SimWord2Vec(mSkipGram, queryWords, targetWords)) #0.999|0.999|0.999
	# print("### FastText - CBOW - sent. embed.: ")
	# Evaluation(myNLPTool.SimFastText(mCBOW, queryWords, targetWords)) #0.893|0.841|0.636
	# print("### FastText - CBOW - sent. embed.: ")
	# Evaluation(myNLPTool.SimFastText(mSkipGram, queryWords, targetWords)) #0.887|0.801|0.661
	# print("### distil BERT - pretrained - sent. embed.:")
	# Evaluation(myNLPTool.DistilBERT(api_token, dataset[0]["citeSent"], targetSents)) #0.841|0.794|0.747
	# print("### miniLM BERT - pretrained - sent. embed.:")
	# Evaluation(myNLPTool.miniLMBERT(api_token, dataset[0]["citeSent"], targetSents)) #0.517|0.354|0.152

	# DOCUMENT EMBEDDING
	# mCBOW = Word2Vec.load("test" + "_CBOW.model")
	# print("### Word2Vec - CBOW - doc. embed.: ")
	# Evaluation(myNLPTool.SimWord2Vec(mCBOW, queryWords, [wholeFileInWords])) #0.855
	# mSkipGram = Word2Vec.load("test" + "_SG.model")
	# print("### Word2Vec - SkipGram - doc. embed.: ")
	# Evaluation(myNLPTool.SimWord2Vec(mSkipGram, queryWords, [wholeFileInWords])) #0.849
	# print("### FastText - CBOW - doc. embed.: ")
	# Evaluation(myNLPTool.SimFastText(mCBOW, queryWords, [wholeFileInWords])) #0.764
	# print("### FastText - CBOW - doc. embed.: ")
	# Evaluation(myNLPTool.SimFastText(mSkipGram, queryWords, [wholeFileInWords])) #0.791
	# print("### distil BERT - pretrained - doc. embed.:")
	# Evaluation(myNLPTool.DistilBERT(api_token, dataset[0]["citeSent"], [dataset[0]["fullText"]])) #0.752
	# print("### miniLM BERT - pretrained - doc. embed.:")
	# Evaluation(myNLPTool.miniLMBERT(api_token, dataset[0]["citeSent"], [dataset[0]["fullText"]])) #0.257