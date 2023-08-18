from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from gensim.models import Word2Vec
from sklearn.feature_extraction.text import TfidfVectorizer
import requests
import numpy as np

# tokenise sentences -> tokenise words -> remove stopwords -> lemmatisation
def Tokenise(texts):
    texts = texts.replace("\n", " ")
    text2sent2word = []
    text2sent = []
    text2word = []
    stopWords = set(stopwords.words('english'))
    wnl = WordNetLemmatizer()

    for sentence in sent_tokenize(texts):
        text2sent.append(sentence)
        sent2word= []
        for word in word_tokenize(sentence):
            if word.lower() in stopWords: continue
            sent2word.append(wnl.lemmatize(word))
            text2word.append(wnl.lemmatize(word))
            text2sent2word.append(sent2word)
    return text2sent, text2sent2word, text2word


def TrainTFIDF(trCorpus):
    tf = TfidfVectorizer(analyzer='word')
    tf.fit_transform(trCorpus)
    return tf


def SimTFIDF(tf, querySent, targetSents):
    queryWV = tf.transform([querySent]).toarray()[0]

    result = []
    for sentence in targetSents:
        targetWV = tf.transform([sentence]).toarray()[0]
        result.append(queryWV.dot(targetWV) / (np.linalg.norm(queryWV) * np.linalg.norm(targetWV)))
    return result


def TrainWord2Vec(trCorpus, modelName):
    modelCBOW = Word2Vec(trCorpus, min_count = 1, vector_size = 100, window = 5)
    modelSkipGram = Word2Vec(trCorpus, min_count = 1, vector_size = 100, window = 5, sg = 1)
    # print("Cosine similarity between 'blockchain' and 'moreover' - Skip Gram : ", model2.wv.similarity('blockchain', 'moreover')) # 0.304
    modelCBOW.save(modelName + "_CBOW.model")
    modelSkipGram.save(modelName + "_SG.model")
    return (modelCBOW, modelSkipGram)


def SimWord2Vec(model, querySent, targetSents):
    queryWV = np.zeros(shape=(100,))
    count = 0
    print("# QUERY SENTENCE: ")
    for word in querySent:
        if word in model.wv.key_to_index.keys():
            # print(model.wv[word].shape)
            queryWV += model.wv[word]
            count += 1
        else: print("\"" + word + "\" not in training corpus")
    queryWV = queryWV/count

    result = []
    print("# TARGET SENTENCES: ")
    for sentence in targetSents:
        targetWV = np.zeros(shape=(100,))
        count = 0
        for word in sentence:
            if word in model.wv.key_to_index.keys():
                # print(model.wv[word].shape)
                targetWV += model.wv[word]
                count += 1
            else: print("\"" + word + "\" not in training corpus")
        targetWV = targetWV/count
        result.append(queryWV.dot(targetWV) / (np.linalg.norm(queryWV) * np.linalg.norm(targetWV)))
    return result


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