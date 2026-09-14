import asyncio
import sys
import time

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import AnswerAccuracy, AnswerRelevancy, AnswerCorrectness
from langchain_openai import ChatOpenAI

#llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


llm = ChatOpenAI(model="gpt-4o", temperature=0)

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


def ragas_evaluate(user_input, response, reference):
    time.sleep(1)

    dataset = Dataset.from_dict({
        "user_input": [user_input],
        "response": [response],
        "reference": [reference]
    })

    results = evaluate(
        dataset=dataset,
        metrics=[AnswerAccuracy(), AnswerRelevancy(), AnswerCorrectness()],
        llm=llm,
    )

    print("___")
    print(results.scores[0])

    return list(results.scores[0].values())


def evaluate_all(meta_list, request, response):
    eva = []
    if meta_list and any(x not in (None, '') for x in meta_list):
        for meta in meta_list:
            eva.append(ragas_evaluate(request, meta, response))

    return eva