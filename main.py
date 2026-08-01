import ast
import csv
import os

import re

from openai import OpenAI

from collections import defaultdict
import ragas_utils
import utils
from metamorph_utils import *
from test import *
from utils import *
import config
import xml.etree.ElementTree as ET
import numpy as np

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

start = 0

system_domain = "A humanoid robot with which students interact to ask questions about concepts to be learned/studied, which the robot displays on its tablet. Currently, the robot displays an image with a finite state machine. The description of the automata shown is as follows: There are 5 states: q0, q1, q2, q3 e q4. q0 is both the initial and the final state. The transitions are: q0 with value 1 goes to q1, q1 with value 1 goes to q2, q2 with value 0 goes to q3, q3 with value 0 goes to q4, q4 with value 0 goes to q0."


def multiple_question(question, index, domain = True):
    print("\nTest case: " + question + "\n____________________")
    metamorphed_qs = []
    if domain:
        file_path = "res/corpus.txt"

        tmp_q = question
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    question2 = line.strip()
                    if i != index and random.random() < 0.2:
                        tmp_q += " " + question2
                        print("Follow-up: " + tmp_q)
                        metamorphed_qs.append((question2, tmp_q))
                        tmp_q = question

        except FileNotFoundError:
            print(f"file '{file_path}' not found.")
        except Exception as e:
            print(f"Error reading file: {e}")

    else:
        file_path = "res/corpus.csv"

        tmp_q = question
        with open(file_path, newline="", encoding="latin1") as csvfile:
            reader = csv.reader(csvfile, delimiter=";")
            i = 0
            for row in reader:
                participant = row[3]
                question2 = row[4]
                if participant == "U":
                    i += 1
                    if i != index and i not in config.EXCLUDE and random.random() < 0.01 and len(metamorphed_qs) < 2:
                        tmp_q += ". " + question2
                        print("Follow-up: " + tmp_q)
                        metamorphed_qs.append((question2, tmp_q))
                        tmp_q = question

    return metamorphed_qs


def test_multiple_questions(question, i, domain = True):
    metamorphed_qs = multiple_question(question, i, domain)

    if domain:
        test_case1 = get_dialogue_answer(question)
    else:
        test_case1 = get_dialogue_answer_states(question)

    if test_case1[0] == "Potresti essere più specifico?":
        config.EXCLUDE.append(i)
    else:

        print("{:<8} {:<8} {:<8} {:<8} {:<8} {:<8}".format("text1", "multi1", "text2", "multi2","text_cnc", "multi_cnc"))
        print("-" * 70)

        for q2, m in metamorphed_qs:
            #print(question + "____" + q2)
            if domain:
                test_case2 = get_dialogue_answer(q2)
            else:
                test_case2 = get_dialogue_answer_states(q2)
            if domain:
                follow_up = get_dialogue_answer(m)
            else:
                follow_up = get_dialogue_answer_states(m)


            compare_multiple(test_case1, test_case2, follow_up, question, q2, m)


def test_mr_6():
    n = 1
    svg_path = f"res/esempio{n}.svg"
    for couple in extract_couples(svg_path):
        test_same(couple[0], [couple[1]], n)


def main():
    print("Start SVG-AIML testing\n")

    #ask_llama("Rendi questa frase passiva, rispondi solo con la frase: \"Cosa vuol dire \"A\" e \"B\" sopra i cerchi?\"")

    file_path = "res/corpus.txt"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                question = line.strip()
                # print(f" {i}: {question}")
                # get_dialogue_answer(question)

                # 1: filler words
                #test_same(question, get_metamorphed_questions(question, 1))

                # 3: sentence inversion / anastrophe
                # test_same(question, get_metamorphed_questions(i, 3))
                # 5: active passive sentence
                # test_same(question, get_metamorphed_questions(i, 5))

                # 7: synonyms
                # test_same(question, get_metamorphed_questions(question, 7))
                # 8: mistakes
                #test_same(question, get_metamorphed_questions(question, 8))

                # 10: multiple questions
                #test_multiple_questions(question, i)

    except FileNotFoundError:
        print(f"file '{file_path}' not found.")
    except Exception as e:
        print(f"Error reading file: {e}")


    # 6: domain/codomain
    #test_mr_6()


def get_last_value(path_csv):
    with open(path_csv, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=";")
        righe = list(reader)

        if not righe:  # se il file è vuoto
            print("File vuoto.")
            return None

        ultima_riga = righe[-1]

        if not ultima_riga or not ultima_riga[0].isdigit():
            print("Nessun intero valido nella prima colonna.")
            return None

        print(int(ultima_riga[0]))
        return int(ultima_riga[0])


def test_mr(file_path, file_name, mr, corpus_type):
    #config.FILE_NAME = file_name
    config.TEST_RELATION = mr

    path_csv = "res/results/" + str(config.TEST_RELATION) + ".csv"
    global start
    start = 0
    if not os.path.isfile(path_csv):
        with open(path_csv, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(
                ["TEST_CASE_NUMBER", "TEST CASE", "FOLLOW UP", "TEST CASE TEXT", "TEST CASE MULTI", "FOLLOW UP TEXT",
                 "FOLLOW UP MULTI", "COMPARE TEXT", "COMPARE MULTI"])
    else:
        start = get_last_value(path_csv)


    with open(file_path, newline="", encoding="latin1") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        for row in reader:
            config.TEST_CASE_NUMBER = row[0]
            question = row[1]
            mrs = row[2]
            if int(config.TEST_CASE_NUMBER) > start and corpus_type in mrs:
                test_same(question, [question], domain = False, file_name = file_name)


def create_follow(follow_up, ids):
    #ids = json.loads(ids)
    ids = [ids]

    for id in ids:
        follow_up = re.sub(r"(this|that|theese|those)", id, follow_up, count=1)

    follow_up = follow_up.replace("stato", "state")
    follow_up = follow_up.replace("valore", "transition value")
    follow_up = follow_up.replace("-", " ")
    follow_up = follow_up.replace("transizione", "transition")

    print(follow_up)

    return follow_up

def main_states():
    path_csv = "res/accuracy/corpus/gpt_certainty.csv"
    global start
    start = 0
    if not os.path.isfile(path_csv):
        with open(path_csv, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            #writer.writerow(["TEST_CASE_NUMBER", "TEST CASE", "FOLLOW UP", "TEST CASE TEXT", "TEST CASE MULTI", "FOLLOW UP TEXT", "FOLLOW UP MULTI", "COMPARE TEXT", "COMPARE MULTI"])
            writer.writerow(["QUESTION", "NLU OUTPUT", "BEST FRAME", "CERTAINTY SCORE", "TEXTUAL RESPONSE", "VISUAL RESPONSE"])

        #with open(path_csv, "w", newline="", encoding="utf-8") as file:
        #    writer = csv.writer(file, delimiter=";")
        #    writer.writerow(["TEST_CASE_NUMBER", "TEST CASE1", "TEST CASE2", "FOLLOW UP", "TEST CASE TEXT1", "TEST CASE MULTI1", "TEST CASE TEXT2", "TEST CASE MULTI2", "FOLLOW UP TEXT", "FOLLOW UP MULTI", "COMPARE TEXT1", "COMPARE MULTI1", "COMPARE TEXT2", "COMPARE MULTI2", "COMPARE COMBO", "COMPARE COMBO"])


    else:
        start = get_last_value(path_csv)

    file_path = "res/corpus.csv"

    clean_corpus = []
    tmp_corpus = []

    #with open(file_path, newline="", encoding="latin1") as csvfile:
    #    reader = csv.reader(csvfile, delimiter=";")
    #    i = 0
    #    for row in reader:
    #        participant = row[3]
    #        question = row[4]
    #        if participant == "U":
    #            i += 1
    #            if i > start:
    #                config.TEST_CASE_NUMBER = i

    #                if utils.clean_strings(question) not in tmp_corpus:
    #                    tmp_corpus.append(utils.clean_strings(question))
    #                    clean_corpus.append(question)
    #                    print(question)

                    #print(i.__str__() + ";" + question + ";")
                    #get_dialogue_answer_states(question)

                    # 1: filler words
                    # test_same(question, get_metamorphed_questions(question, 1), domain=False)

                    # 2: sentence inversion / anastrophe
                    # test_same(question, get_metamorphed_questions(i, 3), domain=False)

                    # 3: active passive sentence
                    # test_same(question, get_metamorphed_questions(i, 5), domain=False)

                    # 4: synonyms
                    # test_same(question, get_metamorphed_questions(question, 7), domain=False)
                    # 5: mistakes
                    # test_same(question, get_metamorphed_questions(question, 8), domain=False)

                    # 6: multiple questions
                    # test_multiple_questions(question, i, domain=False)
    #print(len(clean_corpus))

    with open("res/gpt_corpus.csv", newline="", encoding="latin1") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        for row in reader:
            question = row[0]
            response = get_dialogue_answer_states(question)

            with open(path_csv, "a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file, delimiter=";")
                #"QUESTION", "NLU OUTPUT", "BEST FRAME", "CERTAINTY SCORE", "TEXTUAL RESPONSE", "VISUAL RESPONSE"
                writer.writerow(
                    [question, response["nlu_output"], response["best_frame"], response["certainty_score"], response["response"], response["svg_elements"] ])


def check_mr_res():
    test_cases = 0
    total = 0
    errors = 0
    multi_errors = 0
    number = 0
    with open("res/results/7.csv", newline="", encoding="latin1") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        for row in reader:
            if row[0].isdigit() and number != row[0]:
                test_cases += 1
            number = row[0]
            question = row[1]
            follow_up = row[2]
            test_case_text = row[3]
            follow_text = row[5]
            compare_text = row[7]
            compare_multi = row[8]

            #test_case_text = row[4]
            #follow_text = row[8]
            #compare_text = row[14]
            #compare_multi = row[15]
            if number.isdigit():
                #if follow_up != "[NOT TRANSFORMABLE]":
                    #if not("Potresti essere" in follow_text or "Potresti essere" in test_case_text):
                        total += 1
                        if compare_text == "False":
                            errors += 1
                        if compare_multi == "False":
                            multi_errors += 1

    print(test_cases)
    print(errors)
    print(multi_errors)
    print(total)
    print(errors / total)
    print(multi_errors / total)


def ask_GPT(domain_description, n=30):
    client = OpenAI()

    prompt = f"""
        I describe you a system: {domain_description}.
        List {n} realistic varied, and natural questions that a student learning finite state machine for the first time might ask this system. 
        Questions should be both about the image shown (eg. is it possible to go from q2 to q4?, what is the value of the transition from q1 to q2?) and more general concepts.
        Write them in natural language, one per line, without numbering them.
        """

    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {"role": "system", "content": "You are a young student interacting with a humanoid robot in order to learn."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_completion_tokens=1500,
    )

    text = response.choices[0].message.content.strip()
    print(text)
    return text


def generate_test_GPT(domain_description, n=30):
    client = OpenAI()

    prompt = f"""
        I describe you a system: {domain_description}.
        
        Tell me five natural questions that a high school student learning finite state machine for the first time might ask this system. 
        The question should be both about the image shown (eg. is it possible to go from q2 to q4?, what is the value of the transition from q1 to q2?) and more general concepts.
        The question should try to expose failures in the system / cases where the system doesn't respond properly to the question.
        The system replies to questions extracting from the user input elements related to four categories of a frame and then uses just this frame filled with information to find the best matching answer.
        The frame is composed by: dialogue act, argument, intent and slots.
        
        The dialogue act is extracted with this prompt: Given the label “dialogue act” and the following possible values: AutoF:autoNegative,
        DS:opening, SOM:initGreeting, DS:suggest, OCM:selfCorrection, SOM:initGoodbye,
        SOM:returnGreeting, SOM:thanking, Ta:answer, Ta:checkQuestion, Ta:propositionalQuestion, Ta:request, Ta:setQuestion, TuM:turnAccept.
        
        The argument is extracted with this prompt: Given the label “argument” and the following possible values: Automata, Language, Pattern, State, Transition, Null
        You must extract the argument from the user input.
        Examples:
        - Example 1: User input: “How many transitions are there in the automaton?”
        System response: “Transition”
        - Example 2: User input: “There are a total of 3 states: q0, q1, and q2. q0 is
        both initial and final state.” System response: “State”
        - Example 3: User input: “What is the language of an automaton?” System
        response: “Language”
        
        The intent is extracted with this prompt: Given the label “intent” and the following possible values: fsa-theoretical, fsapractical, Null
        You must extract the argument from the user input.
        Examples:
        - Example 1: User input: “How many transitions are there in the automaton?”
        System response: “fsa-practical”
        - Example 2: User input: “There are a total of 3 states: q0, q1, and q2. q0 is
        both initial and final state.” System response:“fsa-practical”,
        - Example 3: User input: “What is the final state of an automaton?” System
        response: “fsa-theoretical”,
        
        The slots are extracted with this prompt: Given the following slot names:
        - alphabet: The system or user asks or provides information about the alphabet
        of the automaton (e.g. “alphabet”:[“1”,“0”] or “alphabet”:“?”)
        - automatonType: The system or user asks or provides information about the
        typology of the automaton (e.g. “automatonType”: “deterministic” or “automatonType”:“?”)
        - finalStates: The system or user asks or provides information about the final
        states of the automaton (e.g. “finalStates”: [“Q1”, “Q2”] or “finalStates”:“?”)
        - graphicRepresentation: The system or user asks or provides information
        about the graphical representation of the automaton (e.g. “graphicRepresentation”:
        “pentagon” or “graphicRepresentation”:“?”)
        - initialState: The system or user asks or provides information about the initial
        state of the automaton (e.g. “initialState”: “Q0” or “initialState”:“?”)
        - input: The system or user asks or provides information about the input of
        the automaton (e.g. “input”: [“11000”,“1100011000”] or “input”:“?”)
        - languageType: The system or user asks or provides information about the language
        type of the automaton (e.g. “languageType”: “regular” or “languageType”:“?”)
        - numberOfFinalStates: The system or user asks or provides information about
        the number of final states of the automaton (e.g. “numberOfFinalStates”: “2”
        or “numberOfFinalStates”:“?”)
        - numberOfStates: The system or user asks or provides information about the
        number of states of the automaton (e.g. “numberOfStates”: “5” or “numberOf-
        States”:“?”)
        - numberOfTransitions: The system or user asks or provides information about
        the number of transitions of the automaton (e.g. “numberOfTransitions”: “7”
        or “numberOfTransitions”:“?”)
        - optimalSpatialRepresentation: The system or user asks or provides information
        about the optimal spatial representation of the automaton (e.g. “optimalSpatialRepresentation”:“?”)
        - output: The system or user asks or provides information about the output
        of the automaton (e.g. “output”: “accepted/denied” or “output”:“?”)
        - patternType: The system or user asks or provides information about the
        pattern type of the automaton (e.g. “patternType”: “clockwise” or “pattern-
        Type”:“?”)
        - stateFrom: The system or user requests or provides information about a specific
        starting state (e.g.“stateFrom”: “q3” or “stateFrom”:“?”)
        - stateTo: The system or user requests or provides information about a specific
        ending state (e.g.“stateTo”: “q3” or “stateTo”:“?”)
        - stateWithMostTransitions: The system or user asks or provides information
        about the state with most transitions (e.g.“stateWithMostTransitions”: “q3” or
        “stateWithMostTransitions”:“?”)
        - stateWithoutTransitions: The system or user asks or provides information
        about the states without transitions (e.g.“stateWithoutTransitions”: “q3” or
        “stateWithoutTransitions”:“?”)
        - states: The system or user asks or provides information about the states of
        the automaton (e.g. “states”: [“Q1”,“Q2”] or “states”:“?”)
        - transitions: The system or user asks or provides information about the transitions
        of the automaton (e.g. “transitions”: [[“Q0”,“Q1”,“1”],[“Q1”,“Q2”,“0”]] or
        “transitions”:“?”)
        You must respond with a JSON containing information extracted from the
        user input.
        Examples:
        - Example 1: User input: “How many transitions are there in the automaton?”
        System response: “slot names”: [“numberOfTransitions”], “slot values”: [“?”]
        - Example 2: User input: “There are a total of 3 states: q0, q1, and q2. q0 is
        both initial and final state.” System response: “slot names”: [“numberOfStates”,
        “states”, “initialState”, “finalStates”], “slot values”: [“3”, [“q0”, “q1”, “q2”], “q0”,
        [“q0”]]
        - Example 3: User input: “What is the final state of an automaton?” System
        response: “slot names”: [“finalStates”], “slot values”: [“?”]
        

        Generate five simple question, as different from each other as possible, separated by the symbol ";". They must be a single sentence containing only one request. Do not produce multi-part or compound questions.
        Examples of the format: How many states does the automaton have?;What happens when reading 101 from state q2?;...
        Avoid long or step-by-step questions.
        """

    # Generate five simple question, as different from each other as possible, separated by the symbol ";". They must be a single sentence containing only one request. Do not produce multi-part or compound questions.
    #         Examples of the format: How many states does the automaton have?;What happens when reading 101 from state q2?;...
    #         Avoid long or step-by-step questions.

    # Generate one simple question. They must be a single sentence containing only one request. Do not produce multi-part or compound questions.
    #         Examples of the format: How many states does the automaton have?;What happens when reading 101 from state q2?;...
    #         Avoid long or step-by-step questions.

    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {"role": "system", "content": "You are a question generator for a dialogue system."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_completion_tokens=500,
    )

    text = response.choices[0].message.content.strip()
    print(text)

    file_path = "res/results/mutation_res/questions.txt"

    with open(file_path, "w", encoding="utf-8") as f:
        for q in text.split(";"):
            f.write(q + "\n")


    #return text.split(";")

def get_next_question():
    file_path = "res/results/mutation_res/questions.txt"

    if not os.path.exists(file_path):
        return None, 6

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        os.remove(file_path)
        return None, 6

    question = lines[0].strip()

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines[1:])

    if len(lines) == 1:
        os.remove(file_path)

    return question, 6 - len(lines)


def check_not_accurate(file, threshold):
    inaccurate = 0
    tot = 0
    with open(file, newline="", encoding="latin1") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        for row in reader:
            if tot != 0: #and tot < 10:
                question = row[0]
                response = row[4]

                #llm_judge_response(question, response)

                certainty = float(row[3])
                if certainty < threshold:
                    inaccurate += 1
            tot += 1

    print("Inaccurate count: " + str(inaccurate) + "/" + str(tot - 1))


def llm_judge_response(question, response, multi):
    response = response.replace("MUTATION ", "")

    prompt = f"""
    Evaluate the answer to this question considering this description of the system domain: {system_domain}.

    Question: {question}
    System answer: {response}
    System visual update: {multi}

    Give a score as a real number from 0.0 to 1.0 (0=irrelevant or incomprehensible, 1=perfectly relevant and clear)
    for each dimension: 
    1 - AnswerAccuracy: measures the agreement between a model’s response and a reference ground truth (inferred from the system description) for a given question.
    2 - AnswerRelevancy: The evaluation metric, Answer Relevancy, focuses on assessing how pertinent the generated answer is to the given prompt. A lower score is assigned to answers that are incomplete or contain redundant information and higher scores indicate better relevancy. 
    3 - AnswerCorrectness: measures how many of the relevant documents (or pieces of information) were successfully retrieved. It focuses on not missing important results. Higher recall means fewer relevant documents were left out. In short, recall is about not missing anything important. 
    4 - VisualRelevancy: This evaluation metric assesses how relevant the System Visual Update is to the given prompt. The System Visual Update consists of the IDs of the SVG image elements that should be enlightened. These elements are expected to be relevant to and reflect the content of the generated response. Lower scores are assigned when the selected elements are incomplete, unrelated, or contain redundant information, while higher scores indicate that the selected SVG elements accurately support the response. If the generated response is generic and does not refer to any specific visual element, an empty System Visual Update is considered the correct output and should receive a high score.
    
    Return only JSON, example:
    {{
        "AnswerAccuracy": 0.85,
        "AnswerRelevancy": 0.239,
        "AnswerCorrectness": 1.0,
        "VisualRelevancy": 0.7
    }}
    """

    client = OpenAI()
    resp = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {"role": "system", "content": "You are an impartial and analytical evaluator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_completion_tokens=150  # max_tokens=150,
    )

    content = resp.choices[0].message.content.strip()

    if content.startswith("```"):
        content = content.strip("`")
        content = content.replace("json\n", "", 1).strip()

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        result = None

    #print(result.values())
    print(result)
    return result


def judge_templates():
    tree = ET.parse("res/accuracy/automa.aiml")
    root = tree.getroot()

    correct_judge = []
    wrong_judge = []

    i = 0
    for category in root.findall("category"):
        #i += 1

        request = category.get("request")
        template_elem = category.find("template")
        response = (template_elem.text or "").strip()
        wrong = ast.literal_eval(category.get("wrong")) if category.get("wrong") else []

        if request:
            correct_judge.append([request, response] + list(llm_judge_response(request, response).values()))

            if wrong != []:
                for w in wrong:
                    wrong_judge.append([request,w] + list(llm_judge_response(request, w).values()))

        if i == 5:
            break

    for correct in correct_judge:
        with open("res/accuracy/corpus/correct.csv", "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(correct)

    for wrong in wrong_judge:
        with open("res/accuracy/corpus/wrong.csv", "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(wrong)


def calculate_accuracy(file):
    relevance = []
    clarity = []
    completeness = []
    with open(file, newline="", encoding="latin1") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        for row in reader:
            relevance.append(float(row[2]))
            clarity.append(float(row[3]))
            completeness.append(float(row[4]))

    print("\n\nCases " + file + ": " + str(len(relevance)))
    print("AnswerAccuracy: AV = " + str(np.mean(relevance)) + " - SD = " + str(np.std(relevance, ddof=1)))
    print("AnswerRelevancy: AV = " + str(np.mean(clarity)) + " - SD = " + str(np.std(clarity, ddof=1)))
    print("AnswerCorrectness: AV = " + str(np.mean(completeness)) + " - SD = " + str(np.std(completeness, ddof=1)))

    gui_table(file + ": " + str(len(relevance)), ["Accuracy", "Relevancy", "Correctness"], [np.mean(relevance), np.mean(clarity), np.mean(completeness)], [np.std(relevance, ddof=1), np.std(clarity, ddof=1), np.std(completeness)])


def gui_table(title, conditions, avs, sds):

    root = tk.Tk()
    root.title(title)
    root.geometry("600x400")

    # === FRAME sinistro: tabella ===
    frame_tabella = ttk.Frame(root)
    frame_tabella.pack(side="left", fill="y", padx=10, pady=10)

    ttk.Label(frame_tabella, text="Stats", font=("Arial", 12, "bold")).pack()

    tabella = ttk.Treeview(frame_tabella, columns=("AV", "SD"), show="headings", height=5)
    tabella.heading("AV", text="AV")
    tabella.heading("SD", text="Dev. Std")
    tabella.column("AV", width=80, anchor="center")
    tabella.column("SD", width=80, anchor="center")

    for cond, m, sd in zip(conditions, avs, sds):
        tabella.insert("", "end", values=(f"{m:.2f}", f"{sd:.2f}"), text=cond)

    tabella.pack(pady=10)

    # === FRAME destro: grafico con barre di errore ===
    frame_grafico = ttk.Frame(root)
    frame_grafico.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    fig, ax = plt.subplots(figsize=(4, 3))
    x = np.arange(len(conditions))

    ax.bar(x, avs, yerr=sds, capsize=6, color="#69b3a2", alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(conditions)
    ax.set_ylim(0, 1.2)
    ax.set_ylabel("Average value")
    ax.set_title("Averages with Standard Deviation")

    # Inserisci il grafico nella GUI
    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    # === Avvio interfaccia ===
    root.mainloop()


def judge_responses(file):
    with open(file, newline="", encoding="latin1") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        i = 0
        for row in reader:
            if i == 0:
                i += 1
            else:
                question = row[0]
                response = row[4]

                with open("res/accuracy/corpus/original/" + os.path.basename(file), "a", newline="", encoding="utf-8") as f_out:
                    writer = csv.writer(f_out, delimiter=";")
                    writer.writerow([question, response] + list(llm_judge_response(question, response).values()))


def judge_mutant(aiml_mutant):
    with open("res/accuracy/corpus/clean_corpus_certainty.csv", newline="", encoding="latin1") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        i = 0
        for row in reader:
            if i == 0:
                i += 1
            else:
                question = row[0]
                nlu = row[1]

                response = get_dialogue_answer_states_nlu(nlu, aiml_mutant)

                with open("res/accuracy/corpus/mutant/clean_" + aiml_mutant + ".csv", "a", newline="",
                          encoding="utf-8") as f_out:
                    writer = csv.writer(f_out, delimiter=";")
                    writer.writerow([question, response] + list(llm_judge_response(question, response).values()))


    with open("res/accuracy/corpus/gpt_certainty.csv", newline="", encoding="latin1") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        i = 0
        for row in reader:
            if i == 0:
                i += 1
            else:
                question = row[0]
                nlu = row[1]

                response = get_dialogue_answer_states_nlu(nlu, aiml_mutant)

                with open("res/accuracy/corpus/mutant/gpt_" + aiml_mutant + ".csv", "a", newline="",
                          encoding="utf-8") as f_out:
                    writer = csv.writer(f_out, delimiter=";")
                    writer.writerow([question, response] + list(llm_judge_response(question, response).values()))


def evaluate_all_gpt(meta_list, request):
    eva = []
    if meta_list and any(x not in (None, '') for x in meta_list):
        for meta in meta_list:
            eva.append(llm_judge_response(request, meta))

    return eva


def judge_templates_ragas(ragas = True):
    tree = ET.parse("res/accuracy/automa.aiml")
    root = tree.getroot()

    correct_judge = []
    wrong_judge = []

    judge = []
    i = 0
    for category in root.findall("category"):
        #i += 1

        request = category.get("request")
        template_elem = category.find("template")
        response = (template_elem.text or "").strip()
        wrong = ast.literal_eval(category.get("wrong")) if category.get("wrong") else []
        meta_str = category.attrib.get('metamorph')
        if meta_str:
            metamorph = json.loads(meta_str)

            if ragas:
                paraphrase = ragas_utils.evaluate_all(metamorph["paraphrase"], request, response)
                missing_detail = ragas_utils.evaluate_all(metamorph["missing_detail"], request, response)
                swap = ragas_utils.evaluate_all(metamorph["swap"], request, response)
                contradiction = ragas_utils.evaluate_all(metamorph["contradiction"], request, response)
                extra = ragas_utils.evaluate_all(metamorph["extra"], request, response)
                off_topic = ragas_utils.evaluate_all(metamorph["off_topic"], request, response)
                typo = ragas_utils.evaluate_all(metamorph["typo"], request, response)
                ambiguous = ragas_utils.evaluate_all(metamorph["ambiguos"], request, response)

                judge.append([request, response, ragas_utils.ragas_evaluate(request, response, response),
                              metamorph["paraphrase"], paraphrase, metamorph["missing_detail"], missing_detail,
                              metamorph["swap"], swap, metamorph["contradiction"], contradiction, metamorph["extra"],
                              extra, metamorph["off_topic"], off_topic, metamorph["typo"], typo, metamorph["ambiguos"],
                              ambiguous])

            else:
                paraphrase = evaluate_all_gpt(metamorph["paraphrase"], request)
                missing_detail = evaluate_all_gpt(metamorph["missing_detail"], request)
                swap = evaluate_all_gpt(metamorph["swap"], request)
                contradiction = evaluate_all_gpt(metamorph["contradiction"], request)
                extra = evaluate_all_gpt(metamorph["extra"], request)
                off_topic = evaluate_all_gpt(metamorph["off_topic"], request)
                typo = evaluate_all_gpt(metamorph["typo"], request)
                ambiguous = evaluate_all_gpt(metamorph["ambiguos"], request)

                judge.append([request, response, llm_judge_response(request, response),
                              metamorph["paraphrase"], paraphrase, metamorph["missing_detail"], missing_detail,
                              metamorph["swap"], swap, metamorph["contradiction"], contradiction, metamorph["extra"],
                              extra, metamorph["off_topic"], off_topic, metamorph["typo"], typo, metamorph["ambiguos"],
                              ambiguous])

        #if request:
        #    correct_judge.append([request, response] + ragas_utils.ragas_evaluate(request, response, response))

        #    if wrong != []:
        #        for w in wrong:
        #            wrong_judge.append([request, w] + ragas_utils.ragas_evaluate(request, w, response))

        if i == 3:
            break

    #for correct in correct_judge:
    #    with open("res/accuracy/corpus/correct_ragas.csv", "a", newline="", encoding="utf-8") as file:
    #        writer = csv.writer(file, delimiter=";")
    #        writer.writerow(correct)

    #for wrong in wrong_judge:
    #    with open("res/accuracy/corpus/wrong_ragas.csv", "a", newline="", encoding="utf-8") as file:
    #        writer = csv.writer(file, delimiter=";")
    #        writer.writerow(wrong)

    with open("res/accuracy/corpus/metamorphed_gpt5_1.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["REQUEST", "REFERENCE", "EVA_REFERENCE", "PARAPHRASE", "EVA_PARAPHRASE", "MISSING_DETAILS", "EVA_MISSING_DETAILS", "SWAP", "EVA_SWAP", "CONTRADICTION", "EVA_CONTRADICTION", "EXTRA", "EVA_EXTRA", "OFF_TOPIC", "EVA_OFF_TOPIC", "TYPO", "EVA_TYPO", "AMBIGUOUS", "EVA_AMBIGUOUS"])

    for j in judge:
        with open("res/accuracy/corpus/metamorphed_gpt5_1.csv", "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(j)


def get_number_list(s, mode = True):
    if mode:

        try:
            obj = ast.literal_eval(s)

            if isinstance(obj, dict):
                return [
                    obj["AnswerAccuracy"],
                    obj["AnswerRelevancy"],
                    obj["AnswerCorrectness"]
                ]

                # Caso 2: è una lista di dizionari
            elif isinstance(obj, list):
                return [
                    [d["AnswerAccuracy"], d["AnswerRelevancy"], d["AnswerCorrectness"]]
                    for d in obj
                ]
            else:
                data = []
        except Exception:
            data = []

        print(data)

        return data
    else:
        clean = re.sub(r'np\.float64\(([^)]+)\)', r'\1', s)

        print(clean)

        try:
           data = ast.literal_eval(clean)
        except Exception:
           data = []

        return data


def is_not_empty(x):
    if isinstance(x, list):
        return any(is_not_empty(i) for i in x)
    return x is not None


def distance_from_interval(value, a, b):
    # Assicurati che a < b
    a, b = min(a, b), max(a, b)

    if a <= value <= b:
        return 0.0
    elif value < a:
        return a - value
    else:
        return value - b


def compare_metamorphed(metamorph, param, eva, expected):
    if not is_not_empty(eva):
        return

    res_accuracy = 0
    res_relevancy = 0
    res_correctness = 0
    distance_accuracy = 0
    distance_relevancy = 0
    distance_correctness = 0
    print("\nMetamorph: " + metamorph)
    for e in eva:
        if e:
            d1 = param[0] - e[0]
            d2 = param[1] - e[1]
            d3 = param[2] - e[2]

            if not(expected[0][0] + param[0] >= e[0] >= param[0] + expected[0][1]):
                res_accuracy += 1
                distance_accuracy = distance_from_interval(e[0], expected[0][0] + param[0], expected[0][1] + param[0])
            if not(expected[1][0] + param[1] >= e[1] >= param[1] + expected[1][1]):
                res_relevancy += 1
                distance_relevancy = distance_from_interval(e[1], expected[1][0] + param[1], expected[1][1] + param[1])
            if not(expected[2][0] + param[2] >= e[2] >= param[2] + expected[2][1]):
                res_correctness += 1
                distance_correctness = distance_from_interval(e[2], expected[2][0] + param[2], expected[2][1] + param[2])

            print(f'Values: {e[0]} - {e[1]} - {e[2]}, Reference: {param[0]} - {param[1]} - {param[2]}, Distance: {d1} - {d2} - {d3}, Range: {expected}')
    if res_accuracy == 0 and res_relevancy == 0 and res_correctness == 0:
        print("Worked as expected")
    else:
        print("Didn't work as expected")

    return [distance_accuracy, distance_relevancy, distance_correctness]


def calculate_av_sd(metamorph, eva_list):
    #print(eva_list)
    filtered = [row for row in eva_list if row is not None and len(row) == 3]
    arr = np.array(filtered)

    means = np.mean(arr, axis=0)
    stds = np.std(arr, axis=0, ddof=1)

    print("______ " + metamorph + "_______")
    print(" Average Accuracy: ", means[0])
    print(" Standard Dev. Accuracy: ", stds[0])
    print(" Average Relevancy: ", means[1])
    print(" Standard Dev. Relevancy: ", stds[1])
    print(" Average Correctness: ", means[2])
    print(" Standard Dev. Correctness: ", stds[2])

def compare_metrics(ranking, metric):
    print("\n\n______________ Comparing " + ["Accuracy", "Relevancy", "Correctness"][metric] + " ______________")
    i = 0
    values = []
    for level in ranking:
        i += 1
        print("======= Level " + str(i) + " =======")
        tmp = []
        for name, data in level.items():
            if data[1]:
                #print("________-")
                #print(data[0])
                #print(data[1])

                for meta in data[1]:
                    if meta:
                        tmp.append(meta[metric])
                        print(name + ": " + str(meta[metric]))
        values.append(tmp)

    failures = 0
    tot = 0
    for i in range(0, len(values) - 1):
        high_val = values[i]
        low_val = values[i + 1]

        for high in high_val:
            for low in low_val:
                tot += 1
                if high < low:
                    failures += 1

    print("Failures: " + str(failures) + ", Total: " + str(tot))

    return failures, tot


def judge_metamorphed():
    para = []
    missing = []
    swaping = []
    contr = []
    extr = []
    off = []
    typ = []
    ambig = []

    accuracy_failures = 0
    accuracy_total = 0
    relevancy_failures = 0
    relevancy_total = 0
    correctness_failures = 0
    correctness_total = 0

    miss = []

    line = 0
    with open("res/accuracy/corpus/metamorphed_gpt5_1.csv", newline="", encoding="latin1") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")


        for row in reader:
            request = row[0]
            reference = row[1]
            eva_reference = get_number_list(row[2])
            paraphrase = row[3]
            eva_paraphrase = get_number_list(row[4])
            missing_detail = row[5]
            eva_missing_detail = get_number_list(row[6])
            swap = row[7]
            eva_swap = get_number_list(row[8])
            contradiction = row[9]
            eva_contradiction = get_number_list(row[10])
            extra = row[11]
            eva_extra = get_number_list(row[12])
            off_topic = row[13]
            eva_off_topic = get_number_list(row[14])
            typo = row[15]
            eva_typo = get_number_list(row[16])
            ambiguous = row[17]
            eva_ambiguous = get_number_list(row[18])

            line += 1
            if line != 1:

                tmp = ast.literal_eval(missing_detail)
                eva_tmp = eva_missing_detail

                if tmp and eva_missing_detail:
                    tmp.append(reference)
                    eva_tmp.append(eva_reference)
                    #print("Missing Detail: " + missing_detail)
                    #print("Missing Detail: " + eva_missing_detail.__str__())

                    miss.append([tmp, eva_tmp])

                #chat = [{"Paraphrase": [paraphrase, eva_paraphrase], "Typo": [typo, eva_typo]},
                #         {"Missing details": [missing, eva_missing_detail], "Ambiguous": [ambiguous, eva_ambiguous]},
                #         {"Extra": [extra, eva_extra], "Swap": [swap, eva_swap]},
                #         {"Off topic": [off_topic, eva_off_topic], "Contradiction": [contradiction, eva_contradiction]},
                #         ]

                acc_fail, acc_tot = compare_metrics([{"Paraphrase": [paraphrase, eva_paraphrase], "Typo": [typo, eva_typo]},
                                                     {"Missing details": [missing, eva_missing_detail], "Ambiguous": [ambiguous, eva_ambiguous], "Extra": [extra, eva_extra]},
                                                     {"Off topic": [off_topic, eva_off_topic], "Contradiction": [contradiction, eva_contradiction], "Swap": [swap, eva_swap]},
                                                     ], 0)
                accuracy_failures += acc_fail
                accuracy_total += acc_tot

                rel_fail, rel_tot = compare_metrics([
                                                     {"Paraphrase": [paraphrase, eva_paraphrase], "Missing details": [missing, eva_missing_detail], "Swap": [swap, eva_swap], "Contradiction": [contradiction, eva_contradiction], "Typo": [typo, eva_typo]},
                                                     {"Ambiguous": [ambiguous, eva_ambiguous], "Extra": [extra, eva_extra]},
                                                     {"Off topic": [off_topic, eva_off_topic]},
                                                     ], 1)
                relevancy_failures += rel_fail
                relevancy_total += rel_tot

                cor_fail, cor_tot = compare_metrics([{"Paraphrase": [paraphrase, eva_paraphrase], "Typo": [typo, eva_typo]},
                                                     {"Missing details": [missing, eva_missing_detail], "Ambiguous": [ambiguous, eva_ambiguous], "Extra": [extra, eva_extra]},
                                                     {"Off topic": [off_topic, eva_off_topic], "Contradiction": [contradiction, eva_contradiction], "Swap": [swap, eva_swap]},
                                                     ], 2)
                correctness_failures += cor_fail
                correctness_total += cor_tot

                very_low = 0.2
                low = 0.3
                moderate = 0.5
                high = 0.8

                #para.append(compare_metamorphed('Paraphrase', eva_reference, eva_paraphrase, [[very_low,-very_low],[very_low,-very_low],[very_low,-very_low]]))  # Paraphrase (accuracy≈1, relevancy≈1, correctness≈1)
                #missing.append(compare_metamorphed('Missing details', eva_reference, eva_missing_detail, [[0,-moderate],[very_low,-very_low],[0,-moderate]]))  # Missing details (partial) (accuracy ↓ moderate, relevancy ≈1, correctness ↓ moderate)
                #swaping.append(compare_metamorphed('Swap', eva_reference, eva_swap, [[0,-high],[very_low,-very_low],[0,-high]]))  # Wrong fact (single swap) (accuracy ↓ a lot, relevancy ≈1, correctness ↓ a lot)
                #contr.append(compare_metamorphed('Contradiction', [0,1,0], eva_contradiction, [[very_low,-very_low],[very_low,-very_low],[very_low,-very_low]]))  # Contradiction (accuracy ≈0, relevancy ≈1, correctness ≈0)
                #extr.append(compare_metamorphed('Extra', eva_reference, eva_extra, [[0.0,-low],[1,-1],[0.0,-low]]))  # extra invented facts (accuracy ↓, could be high or not, correctness ↓)
                #off.append(compare_metamorphed('Off topic', [0,0,0], eva_off_topic, [[very_low,-very_low],[very_low,-very_low],[very_low,-very_low]]))  # Off-topic / Irrelevant (accuracy ≈0, relevancy ≈0, correctness ≈0)
                #typ.append(compare_metamorphed('Typo', eva_reference, eva_typo, [[0.0,-low],[1.0,-1.0],[0.0,-low]]))  # Noisy / token-level changes (accuracy small change, correctness small change)
                #ambig.append(compare_metamorphed('Ambiguous', [0.5,0.8,1], eva_ambiguous, [[very_low,-very_low],[very_low,-very_low],[1.0,-1.0]]))  # Ambiguous / vague (accuracy medium, relevancy high)

    print("\n\n\nAccuracy: " + str(accuracy_failures / accuracy_total * 100) + "% - " + str(accuracy_failures) + "/" + str(accuracy_total))
    print("Relevancy: " + str(relevancy_failures / relevancy_total * 100) + "% - " + str(relevancy_failures) + "/" + str(relevancy_total))
    print("Correctness: " + str(correctness_failures / correctness_total * 100) + "% - " + str(correctness_failures) + "/" + str(correctness_total))

    #calculate_av_sd("Paraphrase", para)
    #calculate_av_sd("Missing details", missing)
    #calculate_av_sd("Swap", swaping)
    #calculate_av_sd("Contradiction", contr)
    #calculate_av_sd("Extra", extr)
    #calculate_av_sd("Off topic", off)
    #calculate_av_sd("Typo", typ)
    #calculate_av_sd("Ambiguous", ambig)

    acc_miss_failure = 0
    rel_miss_failure = 0
    cor_miss_failure = 0
    miss_total = 0

    for missing, eva_missing in miss:
        print(missing)
        print(eva_missing)

        if len(missing) > 3:
            for i in range(0, len(eva_missing) - 1):
                #print(missing[i])
                miss_total += 1
                if eva_missing[i][0] > eva_missing[i + 1][0]:
                    acc_miss_failure += 1
                if eva_missing[i][1] > eva_missing[i + 1][1]:
                    rel_miss_failure += 1
                if eva_missing[i][2] > eva_missing[i + 1][2]:
                    cor_miss_failure += 1

    print("\n\n\nAccuracy missing details: " + str(acc_miss_failure / miss_total * 100) + "% - " + str(acc_miss_failure) + "/" + str(miss_total))
    print("Relevancy missing details: " + str(rel_miss_failure / miss_total * 100) + "% - " + str(rel_miss_failure) + "/" + str(miss_total))
    print("Correctness missing details: " + str(cor_miss_failure / miss_total * 100) + "% - " + str(cor_miss_failure) + "/" + str(miss_total))


def compare_LLM_results(ground_truth, comparison):

    ground_truth_list_acc, ground_truth_list_rel, ground_truth_list_cor = utils.get_evaluation_list(ground_truth, False)
    comparison_list_acc, comparison_list_rel, comparison_list_cor = utils.get_evaluation_list(comparison)

    print("Compare Accuracy")
    utils.compare_ranks(ground_truth_list_acc, comparison_list_acc)
    print("Compare Relevancy")
    utils.compare_ranks(ground_truth_list_rel, comparison_list_rel)
    print("Compare Correctness")
    utils.compare_ranks(ground_truth_list_cor, comparison_list_cor)


def generate_question_from_nlu(nlu_intent, nlu_argument, nlu_dialogue_act, nlu_frame):
    client = OpenAI()

    prompt = f"""
            I describe you a system: {system_domain}. This system uses a dialogue system that leverages an LLM in its NLU part to generate a frame.

            Given a frame composed as follows: dialogue act = {nlu_dialogue_act}, argument = {nlu_argument}, intent = {nlu_intent} and slots = {nlu_frame}.
            generate a sentence that causes the extraction system to generate that frame, consider the following prompts used to extract parts of the frame.
            Reply only with the generated phrase.

            The dialogue act is extracted with this prompt: Given the label “dialogue act” and the following possible values: AutoF:autoNegative,
            DS:opening, SOM:initGreeting, DS:suggest, OCM:selfCorrection, SOM:initGoodbye,
            SOM:returnGreeting, SOM:thanking, Ta:answer, Ta:checkQuestion, Ta:propositionalQuestion, Ta:request, Ta:setQuestion, TuM:turnAccept.

            The argument is extracted with this prompt: Given the label “argument” and the following possible values: Automata, Language, Pattern, State, Transition, Null
            You must extract the argument from the user input.
            Examples:
            - Example 1: User input: “How many transitions are there in the automaton?”
            System response: “Transition”
            - Example 2: User input: “There are a total of 3 states: q0, q1, and q2. q0 is
            both initial and final state.” System response: “State”
            - Example 3: User input: “What is the language of an automaton?” System
            response: “Language”

            The intent is extracted with this prompt: Given the label “intent” and the following possible values: fsa-theoretical, fsapractical, Null
            You must extract the argument from the user input.
            Examples:
            - Example 1: User input: “How many transitions are there in the automaton?”
            System response: “fsa-practical”
            - Example 2: User input: “There are a total of 3 states: q0, q1, and q2. q0 is
            both initial and final state.” System response:“fsa-practical”,
            - Example 3: User input: “What is the final state of an automaton?” System
            response: “fsa-theoretical”,

            The slots are extracted with this prompt: Given the following slot names:
            - alphabet: The system or user asks or provides information about the alphabet
            of the automaton (e.g. “alphabet”:[“1”,“0”] or “alphabet”:“?”)
            - automatonType: The system or user asks or provides information about the
            typology of the automaton (e.g. “automatonType”: “deterministic” or “automatonType”:“?”)
            - finalStates: The system or user asks or provides information about the final
            states of the automaton (e.g. “finalStates”: [“Q1”, “Q2”] or “finalStates”:“?”)
            - graphicRepresentation: The system or user asks or provides information
            about the graphical representation of the automaton (e.g. “graphicRepresentation”:
            “pentagon” or “graphicRepresentation”:“?”)
            - initialState: The system or user asks or provides information about the initial
            state of the automaton (e.g. “initialState”: “Q0” or “initialState”:“?”)
            - input: The system or user asks or provides information about the input of
            the automaton (e.g. “input”: [“11000”,“1100011000”] or “input”:“?”)
            - languageType: The system or user asks or provides information about the language
            type of the automaton (e.g. “languageType”: “regular” or “languageType”:“?”)
            - numberOfFinalStates: The system or user asks or provides information about
            the number of final states of the automaton (e.g. “numberOfFinalStates”: “2”
            or “numberOfFinalStates”:“?”)
            - numberOfStates: The system or user asks or provides information about the
            number of states of the automaton (e.g. “numberOfStates”: “5” or “numberOf-
            States”:“?”)
            - numberOfTransitions: The system or user asks or provides information about
            the number of transitions of the automaton (e.g. “numberOfTransitions”: “7”
            or “numberOfTransitions”:“?”)
            - optimalSpatialRepresentation: The system or user asks or provides information
            about the optimal spatial representation of the automaton (e.g. “optimalSpatialRepresentation”:“?”)
            - output: The system or user asks or provides information about the output
            of the automaton (e.g. “output”: “accepted/denied” or “output”:“?”)
            - patternType: The system or user asks or provides information about the
            pattern type of the automaton (e.g. “patternType”: “clockwise” or “pattern-
            Type”:“?”)
            - stateFrom: The system or user requests or provides information about a specific
            starting state (e.g.“stateFrom”: “q3” or “stateFrom”:“?”)
            - stateTo: The system or user requests or provides information about a specific
            ending state (e.g.“stateTo”: “q3” or “stateTo”:“?”)
            - stateWithMostTransitions: The system or user asks or provides information
            about the state with most transitions (e.g.“stateWithMostTransitions”: “q3” or
            “stateWithMostTransitions”:“?”)
            - stateWithoutTransitions: The system or user asks or provides information
            about the states without transitions (e.g.“stateWithoutTransitions”: “q3” or
            “stateWithoutTransitions”:“?”)
            - states: The system or user asks or provides information about the states of
            the automaton (e.g. “states”: [“Q1”,“Q2”] or “states”:“?”)
            - transitions: The system or user asks or provides information about the transitions
            of the automaton (e.g. “transitions”: [[“Q0”,“Q1”,“1”],[“Q1”,“Q2”,“0”]] or
            “transitions”:“?”)
            You must respond with a JSON containing information extracted from the
            user input.
            Examples:
            - Example 1: User input: “How many transitions are there in the automaton?”
            System response: “slot names”: [“numberOfTransitions”], “slot values”: [“?”]
            - Example 2: User input: “There are a total of 3 states: q0, q1, and q2. q0 is
            both initial and final state.” System response: “slot names”: [“numberOfStates”,
            “states”, “initialState”, “finalStates”], “slot values”: [“3”, [“q0”, “q1”, “q2”], “q0”,
            [“q0”]]
            - Example 3: User input: “What is the final state of an automaton?” System
            response: “slot names”: [“finalStates”], “slot values”: [“?”]
            """

    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {"role": "system", "content": "You are a question generator for a dialogue system."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_completion_tokens=500,
    )

    text = response.choices[0].message.content.strip()
    print(text)
    return text


def multimodal_switch(generated_question):
    ids = []

    generated_question = generated_question.lower()

    count = 0
    replace = ["this", "that", "that", "that", "that", "that"]


    for i in range(0, 6):

        # transition value
        target = f"transition value from state q{i} to state q{i + 1}"
        if target in generated_question:
            generated_question = generated_question.replace(target, replace[count], 1)
            ids.append(f"valore-q{i}-q{i + 1}")
            count += 1

        target = f"transition value from q{i} to q{i + 1}"
        if target in generated_question:
            generated_question = generated_question.replace(target, replace[count], 1)
            ids.append(f"valore-q{i}-q{i + 1}")
            count += 1

        # transition
        target = f"transition from state q{i} to state q{i + 1}"
        if target in generated_question:
            generated_question = generated_question.replace(target, replace[count], 1)
            ids.append(f"transizione-q{i}-q{i + 1}")
            count += 1

        target = f"transition from q{i} to q{i + 1}"
        if target in generated_question:
            generated_question = generated_question.replace(target, replace[count], 1)
            ids.append(f"transizione-q{i}-q{i + 1}")
            count += 1

        # final state
        target = f"final state q{i}"
        if target in generated_question:
            generated_question = generated_question.replace(target, replace[count], 1)
            ids.append(f"stato-q{i}-finale")
            count += 1

        # initial state
        target = f"initial state q{i}"
        if target in generated_question:
            generated_question = generated_question.replace(target, replace[count], 1)
            ids.append(f"start-q{i}")
            count += 1

        # state
        target = f"state q{i}"
        if target in generated_question:
            generated_question = generated_question.replace(target, replace[count], 1)
            ids.append(f"stato-q{i}")
            count += 1

    generated_question = generated_question.replace("the this", "this")
    generated_question = generated_question.replace("the that", "that")

    if not ids:
        ids = None
    return generated_question, ids


def ea_1_1(metric, file):
    i = 0

    file_questions_path = "res/results/mutation_res/questions.txt"

    if not os.path.exists(file_questions_path):
        generate_test_GPT(system_domain)

    output_file = "res/results/mutation_res/" + file + ".csv"

    if not os.path.exists(output_file):
        with open(output_file, "a", newline="", encoding="utf-8") as f_out:
            writer = csv.writer(f_out, delimiter=";")
            writer.writerow(
                ["METRIC", "ITERATION", "QUESTION", "ANSWER", "VISUAL_ANSWER", "JUDGE_VALUE", "FAILS", "MUTED", "NLU_OUTPUT"])

    while True:
        no_improve = 0
        tot_mutations = 0
        best_fail = 10
        budget = 15
        tot_fails = []
        next_mutable = ""

        generated_question, i = get_next_question()
        print(generated_question)
        ids = None
        if generated_question is None:
            break

        while no_improve < 5 and tot_mutations < budget:
            tot_mutations += 1
            print("Tot mutations: ", tot_mutations)

            generated_answer = get_dialogue_answer_states(generated_question, file_name = file, ids=ids)
            print("Generated answer: ", generated_answer)
            visual = [
                element["symbol"]
                for element in generated_answer.get("svg_elements", [])
            ]
            generated_result = llm_judge_response(generated_question, generated_answer["response"], visual)


            if list(generated_result.values())[metric] <= best_fail:
                no_improve = 0
                best_fail = list(generated_result.values())[metric]
                next_mutable = generated_answer
            else:
                no_improve += 1

            if list(generated_result.values())[metric] <= 0.3:
                tot_fails.append([generated_question, list(generated_result.values())[metric]])

            with open(output_file, "a", newline="", encoding="utf-8") as f_out:
                writer = csv.writer(f_out, delimiter=";")
                writer.writerow(
                    [["Accuracy", "Relevancy", "Correctness", "VisualRelevancy"][metric], i, generated_question, generated_answer["response"], visual,
                     list(generated_result.values())[metric], len(tot_fails), "MUTATION" in generated_answer["response"], generated_answer["nlu_output"]])

            nlu_intent = next_mutable["nlu_output"]["intent"]
            nlu_argument = next_mutable["nlu_output"]["argument"]
            nlu_dialogue_act = next_mutable["nlu_output"]["dialogue_act"]
            nlu_frame = next_mutable["nlu_output"]["frame"]

            r = random.randint(0, 3)
            match r:
                case 0:
                    nlu_intent = randomize_intent(nlu_intent)
                case 1:
                    nlu_argument = randomize_argument(nlu_argument)
                case 2:
                    nlu_dialogue_act = randomize_dialogue_act(nlu_dialogue_act)
                case 3:
                    nlu_frame = randomize_frame(nlu_frame)

            generated_question = generate_question_from_nlu(nlu_intent, nlu_argument, nlu_dialogue_act, nlu_frame)

            rm = random.randint(0, 1)
            if rm == 1:
                generated_question, ids = multimodal_switch(generated_question)
            else:
                ids = None

            print("No improvement: " + str(no_improve) + " - Total fails (<= 0.3): " + str(len(tot_fails)))

            print("_____ ALL FAILS _____: ", tot_fails)


def get_slots():
    with open("res/results/0.csv", newline="", encoding="latin1") as csvfile:
        set_intent = set()
        set_argument = set()
        set_dialogue_act = set()
        dict_frame = defaultdict(set)

        reader = csv.reader(csvfile, delimiter=";")
        i = 0
        for row in reader:
            if i == 0:
                i += 1
            else:
                frame_in = ast.literal_eval(row[1])
                frame_out = ast.literal_eval(row[2])

                set_intent.add(frame_in.get("intent"))
                set_intent.add(frame_out.get("intent"))

                set_argument.add(frame_in.get("argument"))
                set_argument.add(frame_out.get("argument"))

                set_dialogue_act.add(frame_in.get("dialogue_act"))
                set_dialogue_act.add(str(frame_out.get("dialogue_acts_list")))

                for frame in [frame_in.get("frame"), frame_out.get("correctedFrame")]:
                    if frame:
                        for key, value in frame.items():
                            dict_frame[key].add(str(value))

        print("intent:", set_intent)
        print("argument:", set_argument)
        print("dialogue_act:", set_dialogue_act)
        print("frame:", dict_frame)




if __name__ == "__main__":
    #main()
    #main_states()

    #check_not_accurate("res/results/clean_corpus_certainty.csv", 0.3)
    #check_not_accurate("res/results/gpt_certainty.csv", 0.3)


    #judge_templates()
    #judge_templates_ragas(False)
    #judge_metamorphed()

    #ragas_utils.ragas_evaluate("How many transitions does the automaton have, and what are their values?", "The automaton has 1 transitions: q0 with value 1 goes to q1.", "The automaton has 5 transitions: q0 with value 1 goes to q1, q1 with value 1 goes to q2, q2 with value 0 goes to q3, q3 with value 0 goes to q4, q4 with value 0 goes to q0.")
    #ragas_utils.ragas_evaluate("How many transitions does the automaton have, and what are their values?", "The automaton has 2 transitions: q0 with value 1 goes to q1, q1 with value 1 goes to q2.", "The automaton has 5 transitions: q0 with value 1 goes to q1, q1 with value 1 goes to q2, q2 with value 0 goes to q3, q3 with value 0 goes to q4, q4 with value 0 goes to q0.")
    #ragas_utils.ragas_evaluate("How many transitions does the automaton have, and what are their values?", "The automaton has 3 transitions: q0 with value 1 goes to q1, q1 with value 1 goes to q2, q2 with value 0 goes to q3.", "The automaton has 5 transitions: q0 with value 1 goes to q1, q1 with value 1 goes to q2, q2 with value 0 goes to q3, q3 with value 0 goes to q4, q4 with value 0 goes to q0.")
    #ragas_utils.ragas_evaluate("How many transitions does the automaton have, and what are their values?", "The automaton has 4 transitions: q0 with value 1 goes to q1, q1 with value 1 goes to q2, q2 with value 0 goes to q3, q3 with value 0 goes to q4.", "The automaton has 5 transitions: q0 with value 1 goes to q1, q1 with value 1 goes to q2, q2 with value 0 goes to q3, q3 with value 0 goes to q4, q4 with value 0 goes to q0.")

    #calculate_accuracy("res/accuracy/corpus/correct_ragas.csv")
    #calculate_accuracy("res/accuracy/corpus/wrong_ragas.csv")

    #judge_mutant("mutation_text1")
    #judge_mutant("mutation_text2")
    #judge_mutant("mutation_text3")
    #judge_mutant("mutation_text4")
    #judge_mutant("mutation_frame1")
    #judge_mutant("mutation_frame2")
    #judge_mutant("mutation_frame3")

    #calculate_accuracy("res/accuracy/corpus/mutant/clean_mutation_text1.csv")
    #calculate_accuracy("res/accuracy/corpus/mutant/gpt_mutation_text1.csv")
    #calculate_accuracy("res/accuracy/corpus/mutant/clean_mutation_text2.csv")
    #calculate_accuracy("res/accuracy/corpus/mutant/gpt_mutation_text2.csv")
    #calculate_accuracy("res/accuracy/corpus/mutant/clean_mutation_text3.csv")
    #calculate_accuracy("res/accuracy/corpus/mutant/gpt_mutation_text3.csv")
    #calculate_accuracy("res/accuracy/corpus/mutant/clean_mutation_text4.csv")
    #calculate_accuracy("res/accuracy/corpus/mutant/gpt_mutation_text4.csv")
    #calculate_accuracy("res/accuracy/corpus/mutant/clean_mutation_frame1.csv")
    #calculate_accuracy("res/accuracy/corpus/mutant/gpt_mutation_frame1.csv")
    #calculate_accuracy("res/accuracy/corpus/mutant/clean_mutation_frame2.csv")
    #calculate_accuracy("res/accuracy/corpus/mutant/gpt_mutation_frame2.csv")
    #calculate_accuracy("res/accuracy/corpus/mutant/clean_mutation_frame3.csv")
    #calculate_accuracy("res/accuracy/corpus/mutant/gpt_mutation_frame3.csv")

    #judge_responses("res/accuracy/corpus/clean_corpus_certainty.csv")
    #judge_responses("res/accuracy/corpus/gpt_certainty.csv")


    #generate_corpus_domain = "A humanoid robot with which students interact to ask questions about concepts to be learned/studied, which the robot displays on its tablet. Currently, the robot displays an image with a finite state machine. The description of the automata shown is as follows: There are 5 states: q0, q1, q2, q3 e q4. q0 is both the initial and the final state. The transitions are: q0 with value 1 goes to q1, q1 with value 1 goes to q2, q2 with value 0 goes to q3, q3 with value 0 goes to q4, q4 with value 0 goes to q0."
    #generate_corpus_domain = "A humanoid robot with which students interact to ask questions about the concepts to be learned/studied, which the robot displays on its tablet. Currently, the robot displays an image with 5 circles/circumferences, named q0, q1, q2, q3, and q4. q0 has an arrow pointing to it with the word “start” written on it and is the only one with two concentric circles. The various circles are connected by arrows: from q0, an arrow goes to q1 with a value of 1; from q1, an arrow goes to q2 with a value of 1; from q2, an arrow goes to q3 with a value of 0; from q3, an arrow goes to q4 with a value of 0; and from q4, an arrow goes to q0 with a value of 0."

    #corpus = ask_GPT(generate_corpus_domain)

    #test_mr("res/corpus8.csv", "rules_9a", 91, "C")
    #test_mr("res/corpus8.csv", "rules_9b", 92, "C")

    #test_mr("res/corpus8.csv", "rules_10a", 101, "S")
    #test_mr("res/corpus8.csv", "rules_10b", 102, "S")

    #test_mr("res/corpus8.csv", "rules_11", 11, "C")

    #test_mr("res/corpus8.csv", "rules_12", 12, "V")

    #test_mr("res/corpus8.csv", "rules_13a", 131, "E")
    #test_mr("res/corpus8.csv", "rules_13b", 132, "E")
    
    #check_mr_res()

    #compare_LLM_results("res/accuracy/corpus/ragas_metamorphed_gpt5.csv", "res/accuracy/corpus/metamorphed_gpt5_1.csv")
    
    #get_slots()

    files = ["mutation_text2", "mutation_text3", "mutation_text4"]  # "mutation_frame1", "mutation_frame2", "mutation_frame3", "mutation_text1", "mutation_text2", "mutation_text3", "mutation_text4"
    metrics = [0,1,2,3]

    ea_1_1(1, "mutation_text1")
    ea_1_1(2, "mutation_text1")
    ea_1_1(3, "mutation_text1")

    for file in files:
        for metric in metrics:
            print(["Accuracy", "Relevancy", "Correctness", "VisualRelevancy"][metric] + " - " + file)
            ea_1_1(metric, file)

