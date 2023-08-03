from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from gensim.models import Word2Vec
import requests
from scipy import spatial

# tokenise sentences -> tokenise words -> remove stopwords -> 
def Tokenise(texts):
    texts = texts.replace("\n", " ")
    text2sent2word = []
    text2sent = []
    stopWords = set(stopwords.words('english'))

    for sentence in sent_tokenize(texts):
        text2sent.append(sentence)
        sent2word= []
        # cleanSentence = ""
        for word in word_tokenize(sentence):
            if word.lower() in stopWords: continue
            sent2word.append(word)
            # cleanSentence += (word + " ")
            text2sent2word.append(sent2word)
        # text2sent.append(cleanSentence)
    return text2sent, text2sent2word



def ApplyWord2Vec(words):
    model1 = Word2Vec(words, min_count = 1, vector_size = 100, window = 5)

    # print("Cosine similarity between 'blockchain' and 'moreover' - CBOW : ", model1.wv.similarity('blockchain', 'moreover')) # 0.664
    # print("Cosine similarity between 'blockchain' and 'data' - CBOW : ", model1.wv.similarity('blockchain', 'data')) # 0.830
    model2 = Word2Vec(words, min_count = 1, vector_size = 100, window = 5, sg = 1)
 
    # print("Cosine similarity between 'blockchain' and 'moreover' - Skip Gram : ", model2.wv.similarity('blockchain', 'moreover')) # 0.304
    # print("Cosine similarity between 'blockchain' and 'data' - Skip Gram : ", model2.wv.similarity('blockchain', 'data')) # 0.274


def DistilBERT(api_token, querySent, targetSents):
    API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/msmarco-distilbert-base-tas-b"
    headers = {"Authorization": f"Bearer {api_token}"}

    def query(payload):
        response = requests.post(API_URL, headers = headers, json = payload)
        return response.json()
    
    parameters = {"inputs": {"source_sentence": querySent, "sentences": targetSents}, "wait_for_model": "true"}
    print("Query: " + querySent)
    print("...Compare to " + str(len(targetSents)) + " sentences...")
    return query(parameters)


def miniLMBERT(api_token, querySent, targetSents):
    API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    headers = {"Authorization": f"Bearer {api_token}"}

    def query(payload):
        response = requests.post(API_URL, headers = headers, json = payload)
        return response.json()
    
    parameters = {"inputs": {"source_sentence": querySent, "sentences": targetSents}, "wait_for_model": "true"}
    print("Query: " + querySent)
    print("...Compare to " + str(len(targetSents)) + " sentences...")
    return query(parameters)