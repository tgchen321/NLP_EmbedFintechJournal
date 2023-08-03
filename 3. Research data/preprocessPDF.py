import os, pickle
from pathlib import Path
import myPDFTool, myNLPTool
from matplotlib import pyplot as plt


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

if __name__ == "__main__":
	targetFolder = "IEEEaccess"
	journal = targetFolder
	repoFolder = "."
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
	with open("dataList.pkl", "rb") as pkl:
		dataset = pickle.load(pkl)
	sentences, words = myNLPTool.Tokenise(dataset[0]["fullText"])
	api_token = "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"
	# result = myNLPTool.DistilBERT(api_token, dataset[0]["citeSent"], sentences) #0.649-0.838
	result = myNLPTool.miniLMBERT(api_token, dataset[0]["citeSent"], sentences) #-0.086-0.517
	fig, ax = plt.subplots(figsize =(10, 7))
	ax.hist(result)
	plt.show()
	print("Average similarity(cosine sim.): " + str(sum(result)/len(result)))
	print("Maximum similarity(cosine sim.): " + str(max(result)))
	print("Minimum similarity(cosine sim.): " + str(min(result)))
