import os
import sys

import argparse
import torch
import transformers

#from transformers import GenerationConfig, LlamaForCausalLM, LlamaTokenizer
from transformers import LlamaForCausalLM, LlamaTokenizer
if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

try:
    if torch.backends.mps.is_available():
        device = "mps"
except:  # noqa: E722
    pass

    #lora_weights: str = "tloen/alpaca-lora-7b",
def main(
    load_8bit: bool = False,
    base_model: str = "",
    prompts: str = ""
):
    base_model = base_model or os.environ.get("BASE_MODEL", "")
    assert (
        base_model
    ), "Please specify a --base_model, e.g. --base_model='huggyllama/llama-7b'"
    prompter = prompts

    tokenizer = LlamaTokenizer.from_pretrained(base_model)
    if device == "cuda":
        model = LlamaForCausalLM.from_pretrained(
            base_model,
            load_in_8bit=load_8bit,
            torch_dtype=torch.float16,
            device_map="auto",
        )

    elif device == "mps":
        model = LlamaForCausalLM.from_pretrained(
            base_model,
            device_map={"": device},
            torch_dtype=torch.float16,
        )

    else:
        model = LlamaForCausalLM.from_pretrained(
            base_model, device_map={"": device}, low_cpu_mem_usage=True
        )


    # unwind broken decapoda-research config
    model.config.pad_token_id = tokenizer.pad_token_id = 0  # unk
    model.config.bos_token_id = 1
    model.config.eos_token_id = 2

    if not load_8bit:
        model.half()  # seems to fix bugs for some users.

    model.eval()
    if torch.__version__ >= "2" and sys.platform != "win32":
        model = torch.compile(model)

    def evaluate(
        instruction,
        num_beams=4,
        max_new_tokens=512,
        **kwargs,
    ):
        prompt = instruction
        inputs = tokenizer(prompt, return_tensors="pt")
        input_ids = inputs["input_ids"].to(device)
        '''generation_config = GenerationConfig(
            
            num_beams=num_beams,
            **kwargs,
        )'''



        with torch.no_grad():
            generation_output = model.generate(
                input_ids=input_ids,
                #generation_config=generation_config,
                return_dict_in_generate=True,
                output_scores=True,
                max_new_tokens=max_new_tokens,
            )
        s = generation_output.sequences[0]
        output = tokenizer.decode(s)
        print("output:")
        print(output)
        # return prompter.get_response(output)
        return output
    return evaluate(prompts)
def get_generations(base_model='/home/a/Documents/rl4f-master/llama2-7b',prompts_list=[]):
    result=[]
    for i in prompts_list:
        text=main(base_model=base_model,prompts=i)
        result.append(text)
    return result



if __name__ == "__main__":
    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_model', default=None, type=str, required=True)
    ''' parser.add_argument('--lora_weights', default=None, type=str,
                        help="If None, perform inference on the base model")'''
    parser.add_argument('--load_8bit', action='store_true',
                        help='only use CPU for inference')
    args = parser.parse_args()
    main(args.load_8bit, args.base_model,  "")
    # args.lora_weights,

