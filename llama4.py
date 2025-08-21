from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, pipeline
import torch
#import tensorflow as tf


def load_model():
    model_id = "meta-llama/Llama-3.2-3B-Instruct"

    # Configurazione quantizzazione 4-bit
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype="float16",
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype="auto"
    )

    tokenizer = AutoTokenizer.from_pretrained(model_id)

    return pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device_map="auto",
    )

def ask_llama(prompt: str):

    print(torch.__version__)  # deve stampare 2.4.1
    print(torch.version.cuda)  # deve stampare 12.1
    print(torch.zeros(1).cuda())
    print(torch.cuda.is_available())  # deve dare True
    print(torch.cuda.get_device_name(0))  # dovrebbe dire "NVIDIA GeForce RTX 4070"

    generator = load_model()
    output = generator(
        prompt,
        max_new_tokens=200,
        temperature=0.7,
        top_p=0.9
    )
    print("_________")
    print(output[0]["generated_text"])
    print("_________")