import csv
import json
import re
import xml.etree.ElementTree as ET
import random

from main import get_number_list

exclude_words = ["essere"]

def clean_strings(string):
    string = string.lower()
    string = string.strip()
    string = re.sub(r'[^a-zA-ZàèéìòóùÀÈÉÌÒÓÙ\s]', '', string)
    string = re.sub(r'\s+', ' ', string)

    return string

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
                     ["automaton", "finite automaton", "machine", "state machine"],
                     ["describe", "specify", "define", "outline"],
                     ["transition", "state transition", "arc"],
                     ["state", "configuration"],
                     ["cycle", "loop"],
                     ["final", "goal", "end"]
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
                        #print(" ".join(question.split()[:i]) + " " + syn + " " + " ".join(question.split()[i + 1:]))
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


def average_list(list_metrics):
    acc = 0
    rel = 0
    cor = 0
    for item in list_metrics:
        acc += item[0]
        rel += item[1]
        cor += item[2]
    if len(list_metrics) != 0:
        rel /= len(list_metrics)
        acc /= len(list_metrics)
        cor /= len(list_metrics)
        return [acc, rel, cor]
    else:
        return []


ref = "reference"
para = "paraphrase"
miss = "missing_detail"
sw = "swap"
contr = "contradiction"
extr = "extra"
off = "off_topic"
typ = "typo"
ambig = "ambiguous"

def create_dict(reference, paraphrase, detail, swap, contradiction, extra, topic, typo, ambiguous, metric):
    d = {
        ref: reference[metric] if metric < len(reference) else -1,
        para: paraphrase[metric] if metric < len(paraphrase) else -1,
        miss: detail[metric] if metric < len(detail) else -1,
        sw: swap[metric] if metric < len(swap) else -1,
        contr: contradiction[metric] if metric < len(contradiction) else -1,
        extr: extra[metric] if metric < len(extra) else -1,
        off: topic[metric] if metric < len(topic) else -1,
        typ: typo[metric] if metric < len(typo) else -1,
        ambig: ambiguous[metric] if metric < len(ambiguous) else -1
    }

    sorted_d = dict(sorted(d.items(), key=lambda x: x[1], reverse=True))

    return sorted_d


def get_evaluation_list(file_name, mode = True):
    line = 0

    ground_truth_list_acc = []
    ground_truth_list_rel = []
    ground_truth_list_cor = []

    with open(file_name, newline="", encoding="latin1") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")

        for row in reader:
            line += 1
            if line != 1:
                request = row[0]
                reference = row[1]
                eva_reference = get_number_list(row[2], mode)
                paraphrase = row[3]
                eva_paraphrase = average_list(get_number_list(row[4], mode))
                missing_detail = row[5]
                eva_missing_detail = average_list(get_number_list(row[6], mode))
                swap = row[7]
                eva_swap = average_list(get_number_list(row[8], mode))
                contradiction = row[9]
                eva_contradiction = average_list(get_number_list(row[10], mode))
                extra = row[11]
                eva_extra = average_list(get_number_list(row[12], mode))
                off_topic = row[13]
                eva_off_topic = average_list(get_number_list(row[14], mode))
                typo = row[15]
                eva_typo = average_list(get_number_list(row[16], mode))
                ambiguous = row[17]
                eva_ambiguous = average_list(get_number_list(row[18], mode))

                ground_truth_list_acc.append(create_dict(eva_reference, eva_paraphrase, eva_missing_detail,
                                                               eva_swap, eva_contradiction, eva_extra, eva_off_topic,
                                                               eva_typo, eva_ambiguous, 0))
                ground_truth_list_rel.append(create_dict(eva_reference, eva_paraphrase, eva_missing_detail,
                                                               eva_swap, eva_contradiction, eva_extra, eva_off_topic,
                                                               eva_typo, eva_ambiguous, 1))
                ground_truth_list_cor.append(create_dict(eva_reference, eva_paraphrase, eva_missing_detail,
                                                               eva_swap, eva_contradiction, eva_extra, eva_off_topic,
                                                               eva_typo, eva_ambiguous, 2))

    return ground_truth_list_acc, ground_truth_list_rel, ground_truth_list_cor


def compare_ranks(ground_truth_list, comparison_list):
    distance = 0
    tot = 0

    for ground, comparison in zip(ground_truth_list, comparison_list):
        i = 0

        #print("RAGAS")
        #print(ground.keys())
        #print("LLM")
        #print(comparison.keys())

        for meta, value in ground.items():
            if value != -1:
                tot += 1
                comp_meta, comp_value = list(comparison.items())[i]

                copy_i = i
                if meta != comp_meta:
                    pos = list(comparison.keys()).index(meta)
                    if pos > i:
                        while list(comparison.values())[pos] == list(comparison.values())[pos - 1] and pos != i:
                            pos -= 1
                        if i < pos:
                            while list(ground.values())[copy_i] == list(ground.values())[copy_i + 1] and pos != copy_i:
                                copy_i += 1
                    else:
                        while list(comparison.values())[pos] == list(comparison.values())[pos + 1] and pos != i:
                            pos += 1
                        if i > pos:
                            while list(ground.values())[copy_i] == list(ground.values())[copy_i - 1] and pos != copy_i:
                                copy_i -= 1

                    distance += abs(copy_i - pos)
            i += 1

    print("Total distance: " + str(distance) + ", Total positions: " + str(tot) + " - Average distance: " + str(distance / tot))


def randomize_intent(intent):
    intent_list = ["fsa-theoretical", "fsa-practical", "None"]

    available = [i for i in intent_list if i != intent]
    new = random.choice(available)
    print(f"{intent} ---> {new}")

    return new


def randomize_argument(argument):
    argument_list = ["Automaton", "Language", "Pattern", "State", "Transition", "Alphabet", "None"]

    available = [i for i in argument_list if i != argument]
    new = random.choice(available)
    print(str(argument) + " ---> " + new)

    return new


def randomize_dialogue_act(dialogue_act):
    dialogue_act_list = ["AutoF:autoNegative", "DS:opening, SOM:initGreeting", "DS:suggest, OCM:selfCorrection",
                         "SOM:initGoodbye", "SOM:returnGreeting", "SOM:thanking", "Ta:answer", "Ta:checkQuestion",
                         "Ta:propositionalQuestion", "Ta:request", "Ta:setQuestion", "TuM:turnAccept"]

    available = [i for i in dialogue_act_list if i != dialogue_act]
    new = random.choice(available)
    print(str(dialogue_act) + " ---> " + new)

    return new


def randomize_frame(frame):

    frame_list = {
        "alphabet": ["?", "[“1”,“0”]", "[“2”,“4”]"],
        "automatonType": ["deterministic", "nonDeterministic", "finite", "?"],
        "finalStates": ["[“Q1”, “Q2”]", "[“Q3”]", "?"],
        "graphicRepresentation": ["pentagon", "triangle", "?"],
        "initialState": ["[“Q1”, “Q2”]", "[“Q3”]", "?"],
        "input": ["11000","1100011000", "?", "[0,1]", "not 11100", "symbol", "longerThanThreeOnesFollowedByTwoZeros", "differenceBetweenDeterministicAndNonDeterministicFSA", "notMatching"],
        "languageType": ["deterministic", "non-regular", "regular"],
        "numberOfFinalStates": ["2", "5", "?"],
        "numberOfStates": ["2", "5", "?"],
        "numberOfTransitions": ["2", "7", "?"],
        "optimalSpatialRepresentation": ["?"],
        "output": ["accepted", "denied", "?"],
        "patternType": ["clockwise", "anti-clockwise", "?"],
        "patternExistence": ["?"],
        "stateFrom": ["q3", "?"],
        "stateTo": ["q1", "?"],
        "stateWithMostTransitions": ["q3", "?"],
        "stateWithoutTransitions": ["q3", "?"],
        "states": ["q1", "q2", "?"],
        "transitions": ["[“Q0”,“Q1”,“1”]", "[“Q1”,“Q2”,“0”]", "[“?”,“Q4”,“?”]", "[“Q1”,“?”,“?”]", "[“Q1”,“Q2”,“?”]", "?"]
    }

    if isinstance(frame, dict):
        data = frame
    else:
        try:
            data = json.loads(frame)
        except Exception:
            key = random.choice(list(frame_list.keys()))
            val = random.choice(frame_list[key])
            return json.dumps({key: val}, indent=4)

    result = data.copy()

    key = random.choice(list(frame_list.keys()))
    val = random.choice(frame_list[key])
    return json.dumps({key: val}, indent=4)


    # Operazioni possibili
    #operations = ["add", "delete"]

    # Non eliminare se vuoto
    #if not result:
    #    operations.remove("delete")

    #op = random.choice(operations)

    # -------- MODIFY --------
    #tag = random.choice(list(result.keys()))

    #if tag in frame_list:
    #    possible_vals = frame_list[tag]
    #    new_vals = [v for v in possible_vals if v != result[tag]]
    #    if new_vals:
    #        result[tag] = random.choice(new_vals)

    # -------- ADD --------
    #elif op == "add":
    #    possible_tags = [k for k in frame_list.keys() if k not in result]
    #    if possible_tags:
    #        tag = random.choice(possible_tags)
    #        result[tag] = random.choice(frame_list[tag])

    # -------- DELETE --------
    #elif op == "delete" and len(result) > 1:
    #    tag_to_delete = random.choice(list(result.keys()))
    #    del result[tag_to_delete]

    # Ritorna come JSON string
    #print(frame)
    #print("\n ----- ")
    #print(json.dumps(result, indent=4))

    #return json.dumps(result, indent=4)