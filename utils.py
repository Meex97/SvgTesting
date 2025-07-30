from sentence_transformers import SentenceTransformer, util

import spacy
from nltk.corpus import wordnet as wn
import nltk
nlp = spacy.load("it_core_news_sm")
nltk.download('omw-1.4')
wn.synsets(b'\xe7\x8a\xac'.decode('utf-8'), lang='ita')

exclude_words = ["essere"]


def lemmatizer(word):
    doc = nlp(word)
    for token in doc:
        return token.lemma_
    return None


def lemmatizer_sentence(sentence):
    doc = nlp(sentence)
    return [token.lemma_ for token in doc if not token.is_punct and not token.is_space]


def filter_synonyms(word, sentence, synonyms_list):
    model = SentenceTransformer('distiluse-base-multilingual-cased-v1')
    
    embedding_frase = model.encode(sentence, convert_to_tensor=True)
    
    sinonimi_classificati = []
    for s in synonyms_list:
        if len(s) > 1 and '_' not in s:
            frase_con_sinonimo = sentence.replace(word, s)
            emb = model.encode(frase_con_sinonimo, convert_to_tensor=True)
            score = util.pytorch_cos_sim(embedding_frase, emb).item()
            sinonimi_classificati.append((s, score))
    
    sinonimi_classificati.sort(key=lambda x: x[1], reverse=True)
    
    print("Sorted Synonyms: ")
    filtered_syns = []
    for s, score in sinonimi_classificati:
        if score > 0.8:
            filtered_syns.append(s)
        print(f"{s}: {score:.2f}")
    return filtered_syns

def get_all_synonyms(word):
    if word in exclude_words:
        return []

    print("Word " + word)
    syns = wn.synonyms(word, lang='ita')
    syns = [elem for sublist in syns if sublist for elem in sublist]
    print("Synonyms: " + syns.__str__())
    return syns


def substitute(i, synonyms_list, question):
    metamorphed_qs = []
    for syn in synonyms_list:
        metamorphed_q = ""
        for index, word in question.split():
            if i == index:
                metamorphed_q += syn + " "
            else:
                metamorphed_q += word + " "
        metamorphed_qs.append(metamorphed_q)
        print("Follow-up: " + metamorphed_q)
    return metamorphed_qs


def metamorph_sentence_synonyms(question):
    metamorphed_qs = []
    for i, word in lemmatizer_sentence(question):
        synonyms_list = get_all_synonyms(word)
        synonyms_list = filter_synonyms(word, question, synonyms_list)
        metamorphed_qs.append(substitute(i, synonyms_list, question))
    return metamorphed_qs