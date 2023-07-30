import os
from pathlib import Path
from myPDFTool import pdf2text


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

		pdf2text(str(Path(targetFolder).joinpath(file)), journal)
		print("Plain: \t" + file[0:-4] + "...")


if __name__ == "__main__":
	targetFolder = "tmp"
	journal = "IEEEaccess"
	# BatchMovePDF(targetFolder)
	BatchPDF2text(targetFolder, journal)




# # convert PDFs to plain texts
# def BatchPDF2text(targetFolder):
# 	for file in os.listdir(targetFolder):
# 		# files: 'Podolchak-2022-UKRAINIAN ECOSYSTEM TRANSFORMAT.pdf'
# 		if not file.endswith((".pdf")): continue

# 		# print(targetFolder + "/" + file)
# 		# test/Nasir-2021-Trends and Directions of Financial.pdf
# 		pdf2text(str(Path(targetFolder).joinpath(file)))
# 		print("Plain Text:\t" + file[0:-4] + "...")
