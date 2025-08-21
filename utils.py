from sentence_transformers import SentenceTransformer, util

import re
import xml.etree.ElementTree as ET

import spacy
from nltk.corpus import wordnet as wn
import nltk


exclude_words = ["essere"]


def lemmatizer(word):
    nlp = spacy.load("it_core_news_sm")
    nltk.download('omw-1.4')
    wn.synsets(b'\xe7\x8a\xac'.decode('utf-8'), lang='ita')

    doc = nlp(word)
    for token in doc:
        return token.lemma_
    return None


def lemmatizer_sentence(sentence):
    nlp = spacy.load("it_core_news_sm")
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
    print(synonyms_list)
    for syn in synonyms_list:
        metamorphed_q = ""
        for index, word in enumerate(question.split()):
            if i == index:
                metamorphed_q += syn + " "
            else:
                metamorphed_q += word + " "
        metamorphed_qs.append(metamorphed_q)
        print("Follow-up: " + metamorphed_q)
    return metamorphed_qs


def metamorph_sentence_synonyms(question):
    metamorphed_qs = []
    i = 0
    for word in lemmatizer_sentence(question):
        synonyms_list = get_all_synonyms(word)
        synonyms_list = filter_synonyms(word, question, synonyms_list)
        metamorphed_qs.extend(substitute(i, synonyms_list, question))
        i+=1
    return metamorphed_qs


def metamorph_sentence_synonyms_simple(question):
    synonyms_list = [["cerchio", "tondo", "circonferenza", "anello", "insieme", "gruppo", "disco"],
                     ["cerchi", "tondi", "circonferenze", "anelli", "insiemi", "gruppi", "dischi"],
                     ["freccia", "vettore", "indicatore", "puntatore"],
                     ["frecce", "vettori", "indicatori", "puntatori"],
                     ["connesso", "collegato", "unito", "associato"],
                     ["connessa", "collegata", "unita", "associata"],
                     ["connessi", "collegati", "uniti", "associati"],
                     ["descrivi", "spiega", "racconta"],
                     ["descrivimi", "spiegami", "raccontami"],
                     ]

    metamorphed_qs = []
    word_count = len(question.split())
    i = 0
    for i in range(0, word_count):
        tmp_word = re.sub(r'[^\w\s]', '', question.split()[i].lower())

        for syns in synonyms_list:
            if tmp_word in syns:
                for syn in syns:
                    if syn != tmp_word:
                        metamorphed_qs.append(" ".join(question.split()[:i]) + " " + syn + " " + " ".join(question.split()[i + 1:]))
                        print(" ".join(question.split()[:i]) + " " + syn + " " + " ".join(question.split()[i + 1:]))
        i+=1

    return metamorphed_qs


def extract_couples(svg_path):
    links = get_svg_link_ids(svg_path)
    couples = []

    for link in links:
        tmp = link.split("-")
        if check_couple(tmp[1], tmp[2], links):
            couples.append([f"A cos'è connesso l'elemento {tmp[1]}", f"A cos'è connesso l'elemento {tmp[2]}"])

    return couples


def get_svg_link_ids(svg_path):
    tree = ET.parse(svg_path)
    root = tree.getroot()

    ids = []
    for elem in root.iter():
        elem_id = elem.attrib.get("id")
        if elem_id and "link" in elem_id:
            ids.append(elem_id)
    return ids


def check_couple(param1, param2, links):
    domain = 0
    codomain = 0
    for link in links:
        if param1 in link:
            domain += 1
        if param2 in link:
            codomain += 1

    return domain == 1 and codomain == 1