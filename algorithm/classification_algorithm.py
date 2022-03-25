import spacy
from spacy.lang.pt.examples import sentences
import pandas as pd
import numpy as np
import nltk
nltk.download('punkt', quiet=True)
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import json
import sys

#-----------------------------------------------Normalização----------------------------------------------------#

def setup_abbr():
    file = open("algorithm/dic_portuguese.txt", encoding='utf-8')
    abbr_dict = {}

    for line in file:
        w = line.split(";")
        abbr_dict[w[0]] = w[1].replace("\n", "")
    file.close()

    return abbr_dict

def lemmatizer(doc_corrected):
    lemma_sentence = []
    for token in doc_corrected: 
        if token.pos_ == 'VERB':
            lemma = token.lemma_
            lemma_sentence.append(lemma)
        else:
            lemma_sentence.append(token.text)
    lemmatized_sentence = ' '.join(lemma_sentence)
    return lemmatized_sentence

def remove_stopword(lemmatized_sentence): 
    stop_words = set(stopwords.words('portuguese')+ \
    ["{user}", "{url}", "<br/>", "myfitnesspal", "sigaa", "neste"]) 
    stop_words.remove("não")
    stop_words.remove("sem")
    word_tokens = word_tokenize(lemmatized_sentence)
    filtered_sentence = [w for w in word_tokens if not w in stop_words] 
    filtered_sentence = [] 
    for w in word_tokens: 
        if w not in stop_words: 
            filtered_sentence.append(w)
    result = ' '.join(filtered_sentence)
    return result

#data = pd.read_csv('prus.csv')
#s = '{"data": [{"comment": "Não consegui nem abri o app tive ótimas recomendações mas desse jeito não dá né é vergonhoso"},{"comment": "Estava gostando porém de uns dias pra cá começou a dar erro ao adicionar alimentos"},{"comment": "Não consegui adicionar uma receita"}]}'

inputJson = sys.argv[1]

data = pd.read_json(inputJson)
nlp = spacy.load('pt_core_news_sm')
cln = []
abbr_dict = setup_abbr()

for i in range(len(data)):
    doc = nlp(data['comment'][i]['text'])
    doc_lower = doc.text.lower()
    doc_punctuation = re.sub('[^a-zãàáâéêíõóôúç \n]', ' ', doc_lower)
    doc_corrected = nlp(" ".join([abbr_dict.get(w, w) for w in doc_punctuation.split()])) 
    lemmatized_sentence = lemmatizer(doc_corrected)
    result = remove_stopword(lemmatized_sentence)
    cln.append(result)
clean = pd.DataFrame(data=np.array(cln), columns= ['comment_clean'])

#-----------------------------------------------Classificação---------------------------------------------------#

def pattern1(pru):
    functionality = ''
    hypothesis = ''
    j = 0
    while (j < (len(pru)-3)):
        if pru[j].pos_ == 'ADV':
            if pru[j+1].pos_ == 'VERB':
                if pru[j+2].pos_ == 'VERB' and (pru[j+3].pos_ == 'NOUN' or pru[j+3].pos_ == 'ADJ'):
                    func = [pru[j+2].text, pru[j+3].text]
                    functionality = ' '.join(func)
                    hypothesis = '3'
                    return functionality, hypothesis
                elif pru[j+2].pos_ == 'NOUN' or pru[j+2].pos_ == 'VERB' or pru[j+2].pos_ == 'PROPN':
                    func = [pru[j+1].text, pru[j+2].text]
                    functionality = ' '.join(func)
                    hypothesis = '1'
                    return functionality, hypothesis
        j = j + 1
    return functionality, hypothesis

def pattern2(pru):
    functionality = ''
    hypothesis = ''
    j = 0
    while (j < (len(pru)-3)):
        if pru[j].pos_ == 'VERB':
            if pru[j+1].pos_ == 'VERB' and pru[j+2].pos_ == 'NOUN':
                func = [pru[j+1].text, pru[j+2].text]
                functionality = ' '.join(func)
                hypothesis = '1'
                return functionality, hypothesis
            elif pru[j+1].pos_ == 'NOUN' and (pru[j+2].pos_ == 'ADJ' or pru[j+2].pos_ == 'NOUN' or pru[j+2].pos_ == 'VERB') and pru[j+3].pos_ == 'NOUN':
                func = [pru[j+2].text, pru[j+3].text]
                functionality = ' '.join(func)
                hypothesis = '1'
                return functionality, hypothesis
            elif (pru[j+1].pos_ == 'ADV' or pru[j+1].pos_ == 'AUX') and pru[j+2].pos_ == 'VERB' and pru[j+3].pos_ == 'NOUN':
                func = [pru[j+2].text, pru[j+3].text]
                functionality = ' '.join(func)
                hypothesis = '1'
                return functionality, hypothesis
        j = j + 1
    return functionality, hypothesis

def pattern3(pru):
    functionality = ''
    hypothesis = ''
    j = 0
    while (j < (len(pru)-3)):
        if pru[j].pos_ == 'ADJ' and pru[j+1].pos_ == 'VERB' and pru[j+2].pos_ == 'NOUN':
            func = [pru[j+1].text, pru[j+2].text]
            functionality = ' '.join(func)
            hypothesis = '1'
            return functionality, hypothesis
        j = j + 1
    return functionality, hypothesis

def hypothesis_2(pru):
    j = 0
    while (j < (len(pru)-3)):
        if pru[j].text == 'não' and pru[j+1].text == 'conseguir':
            return 1
        else:
            j = j + 1
    return 0

functionalities = []
hypotheses = []
h2 = 0

for i in range(len(cln)):
    pru = nlp(clean['comment_clean'][i])
    functionality = '' 
    hypothesis = ''
    if len(pru) > 3:
        functionality, hypothesis = pattern1(pru) 
        if len(functionality) == 0:
            functionality, hypothesis = pattern2(pru) 
        if len(functionality) == 0:
            functionality, hypothesis = pattern3(pru) 
        if len(functionality) == 0:
            functionality, hypothesis = 'none', 'none'
    else:
        functionality, hypothesis = 'none', 'none'
    h2 = h2 + hypothesis_2(pru)
    functionalities.append(functionality)
    hypotheses.append(hypothesis)

#Hipótese 2 = 264

func = pd.DataFrame(data=np.array(functionalities), index= range(len(data)), columns= ['functionality'])
hypo = pd.DataFrame(data=np.array(hypotheses), index= range(len(data)), columns= ['hypothesis'])
df = pd.concat([data, func, hypo], axis=1)

#Converting dataframe to json string
jsonOut = df.to_json(orient='table', index=False)

print(json.dumps(jsonOut))