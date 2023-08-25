from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from gensim.models import Word2Vec, TfidfModel, LsiModel
from gensim.corpora import Dictionary
from gensim.matutils import corpus2dense
from gensim.models.coherencemodel import CoherenceModel
from sklearn.decomposition import TruncatedSVD
import requests, math
import numpy as np
from matplotlib import pyplot as plt
import fasttext

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

### not using anymore
def TFIDF(fullText, citeSent):
    fullText.append(citeSent)
    dictionary = Dictionary()
    BoWCorpus = [dictionary.doc2bow(sentence, allow_update=True) for sentence in fullText]
    num_docs = dictionary.num_docs
    print("# of sentences: " + str(num_docs))
    num_terms = len(dictionary.keys())
    print("# of terms: " + str(num_terms))

    TFIDFMatrix = TfidfModel(BoWCorpus)[BoWCorpus]
    denseMatrix = corpus2dense(TFIDFMatrix, num_terms, num_docs).T # sentences * words
    queryWV = denseMatrix[-1]
    print(queryWV.shape)

    result = []
    for targetWV in denseMatrix[0:-1]: 
        result.append(queryWV.dot(targetWV) / (np.linalg.norm(queryWV) * np.linalg.norm(targetWV)))
    return result


def TrainTFIDF(corpus):
    dictionary = Dictionary()
    BoWCorpus = [dictionary.doc2bow(sentence, allow_update=True) for sentence in corpus]
    num_docs = dictionary.num_docs
    print("# of sentences: " + str(num_docs))
    num_terms = len(dictionary.keys())
    print("# of terms: " + str(num_terms))
    # TFIDFMatrix = TfidfModel(BoWCorpus)[BoWCorpus]
    TFIDFMatrix = TfidfModel(BoWCorpus)[BoWCorpus]
    
    # denseMatrix = corpus2dense(TFIDFMatrix, num_terms, num_docs).T # sentences * words
    return TFIDFMatrix, BoWCorpus, dictionary, num_docs, num_terms


def ApplyTFIDF(TFIDFMatrix, num_terms, corpus, idList):
    counter = 0
    batchResult = []
    for dataN in range(len(idList)):
        targetID = idList[dataN]["fullText"]
        queryID = idList[dataN]["citeSent"][0]

        if len(corpus[queryID]) == 0: continue
        queryWV = corpus2dense([TFIDFMatrix[queryID]], num_terms, 1).T

        result = []
        for id in targetID:
            if len(corpus[id]) == 0: continue
            targetWV = corpus2dense([TFIDFMatrix[id]], num_terms, 1)
            tmp = np.dot(queryWV, targetWV) / (np.linalg.norm(queryWV) * np.linalg.norm(targetWV))
            result.append(tmp[0][0])
            counter += 1
        batchResult.append(Top10Avg(result))
    print (str(counter) + " pairs of citation sentence-reference sentence")
    return batchResult

### not using anymore
def LSA(fullText, citeSent):
    fullText.append(citeSent)
    dictionary = Dictionary(fullText)
    BoWCorpus = [dictionary.doc2bow(sentence) for sentence in fullText]
    num_docs = dictionary.num_docs
    print("# of sentences: " + str(num_docs))
    num_terms = len(dictionary.keys())
    print("# of terms: " + str(num_terms))

    TFIDFMatrix = TfidfModel(BoWCorpus)[BoWCorpus]
    denseMatrix = corpus2dense(TFIDFMatrix, num_terms, num_docs).T # sentences * words

    validation = []
    num_topic = 0
    x = range(1, min(num_docs, num_terms))
    for n in x:
        svd = TruncatedSVD(n_components=n).fit(denseMatrix)
        rf = svd.explained_variance_ratio_.sum()
        validation.append(rf)
        if rf >= 0.9 and num_topic == 0:
            num_topic = n

    plt.plot(x, validation)
    plt.xlabel("Number of Topics")
    plt.legend(("explained variance ratio"), loc='best')
    plt.show()

    lsamodel = LsiModel(BoWCorpus, num_topics=num_topic, id2word = dictionary)
    print(lsamodel.print_topics(num_topics=n, num_words=num_terms))
    coherenceScore = CoherenceModel(model=lsamodel, texts=fullText, dictionary=dictionary, coherence='c_v').get_coherence()
    print("Coherence Score: " + str(coherenceScore))

    svdMatrix = lsamodel[BoWCorpus]
    denseMatrix = corpus2dense(svdMatrix, num_terms, num_docs).T
    queryWV = denseMatrix[-1]
    print(queryWV.shape)

    result = []
    for targetWV in denseMatrix[0:-1]: 
        result.append(queryWV.dot(targetWV) / (np.linalg.norm(queryWV) * np.linalg.norm(targetWV)))
    return result

def ApplyLSA(corpus, TFIDFMatrix, dictionary, num_docs, num_terms):
    # validation = []
    # num_topic = 0
    # x = range(1, min(num_docs, num_terms))
    # for n in x:
    #     svd = TruncatedSVD(n_components=n).fit(TFIDFMatrix)
    #     rf = svd.explained_variance_ratio_.sum()
    #     validation.append(rf)
    #     if rf >= 0.9 and num_topic == 0:
    #         num_topic = n

    # plt.plot(x, validation)
    # plt.xlabel("Number of Topics")
    # plt.legend(("explained variance ratio"), loc='best')
    # plt.show()

    lsamodel = LsiModel(TFIDFMatrix, num_topics=400, id2word = dictionary)
    save the model
    # print(lsamodel.print_topics(num_topics=400, num_words=num_terms))
    # coherenceScore = CoherenceModel(model=lsamodel, texts=corpus, dictionary=dictionary, coherence='c_v').get_coherence()
    # print("Coherence Score: " + str(coherenceScore))

    svdMatrix = lsamodel[TFIDFMatrix]
    print(svdMatrix.shape)
    print(lsamodel.projection.u.shape)
    print(lsamodel.projection.s.shape)
    # denseMatrix = corpus2dense(svdMatrix, num_terms, num_docs).T
    # queryWV = denseMatrix[-1]
    # print(queryWV.shape)

    # result = []
    # for targetWV in denseMatrix[0:-1]: 
    #     result.append(queryWV.dot(targetWV) / (np.linalg.norm(queryWV) * np.linalg.norm(targetWV)))
    # return result



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

def TrainFastText(trName, modelName):
    modelCBOW = fasttext.train_unsupervised(trName, model = "cbow", min_count = 1, dim = 100, ws = 5)
    modelCBOW.save_model(modelName + "_CBOW.model")

    modelSkipGram = fasttext.train_unsupervised(trName, model = "skipgram", min_count = 1, dim = 100, ws = 5)
    modelSkipGram.save_model(modelName + "_SG.model")
    return (modelCBOW, modelSkipGram)


def SimFastText(model, querySent, targetSents):
    queryWV = np.zeros(shape=(100,))
    count = 0
    print("# QUERY SENTENCE: ")
    for word in querySent:
        if word in model.words:
            queryWV += model.get_word_vector(word)
            count += 1
        else: print("\"" + word + "\" not in training corpus")
    queryWV = queryWV/count

    result = []
    print("# TARGET SENTENCES: ")
    for sentence in targetSents:
        targetWV = np.zeros(shape=(100,))
        count = 0
        for word in sentence:
            if word in model.words:
                targetWV += model.get_word_vector(word)
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


def Top10Avg(result):
    result.sort(reverse = True)
    top10 = math.ceil(len(result)/10)
    top10avg = sum(result[:top10])/top10
    return top10avg