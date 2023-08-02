from nltk.tokenize import sent_tokenize, word_tokenize
# import warnings
 
# warnings.filterwarnings(action = 'ignore')
 
import gensim
from gensim.models import Word2Vec
def Tokenise(texts):
    f = texts.replace("\n", " ")
    data = []

    # iterate through each sentence in the file
    for i in sent_tokenize(f):
        temp = []
        # tokenize the sentence into words
        for j in word_tokenize(i):
            temp.append(j.lower())
            data.append(temp)
    # print(data)
 
    # Create CBOW model
    model1 = gensim.models.Word2Vec(data, min_count = 1, vector_size = 100, window = 5)

    print("Cosine similarity between 'blockchain' and 'moreover' - CBOW : ", model1.wv.similarity('blockchain', 'moreover'))
    print("Cosine similarity between 'blockchain' and 'data' - CBOW : ", model1.wv.similarity('blockchain', 'data'))
 
    # Create Skip Gram model
    model2 = gensim.models.Word2Vec(data, min_count = 1, vector_size = 100, window = 5, sg = 1)
 
    print("Cosine similarity between 'blockchain' and 'moreover' - Skip Gram : ", model2.wv.similarity('blockchain', 'moreover'))
    print("Cosine similarity between 'blockchain' and 'data' - Skip Gram : ", model2.wv.similarity('blockchain', 'data'))