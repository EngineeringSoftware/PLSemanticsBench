import re
import json
from typing import List
from abc import ABC, abstractmethod
from tqdm import tqdm
from datasets import load_dataset

from .prompt_maker import (
    make_predstate_prompt,
    make_predrule_prompt,
    make_predtrace_prompt,
)
from .experiment_args import ExperimentArgs, Task
from .prompts import system_prompt

class BaseRunner(ABC):
    def __init__(self, args: ExperimentArgs):
        self.args = args
        self._system: List[dict[str, str]] = [
            {
                "role": "system",
                "content": system_prompt,
            },
        ]
        print(f"Querying model: {args.model_name}")
    #fed

    @abstractmethod
    def _query(self, chat: List[dict]) -> List[str]:
        """Must be implemented in inherited classes"""
        pass
    #fed

    def do_experiment(self, result_file: str = None):
        dataset: List = self.load_dataset()
        results = self.run(dataset)
        # Always save in JSONL format
        if not isinstance(results, list):
            results = [results]
        #fi
        if result_file:
            with open(result_file, "w") as f:
                json.dump(results, f)
            #htiw
        #fi
        return results
    #fed

    def load_dataset(self) -> List:
        """
        Load the dataset from huggingface
        """
        print(f"Loading dataset for experiment args {str(self.args)} ....")
        dataset = load_dataset("EngineeringSoftware/PLSemanticsBench", name=self.args.get_hf_split_name())['train']
        num_datapoints_to_run: int = 0
        if self.args.num_datapoints_to_run == -1:
            num_datapoints_to_run = len(dataset)
        elif self.args.num_datapoints_to_run <= len(dataset):
            num_datapoints_to_run = self.args.num_datapoints_to_run
        #fi
        # Convert columnar to row format
        dataset = dataset.flatten()
        row_orient_dataset: List[dict] = []
        keys = dataset.column_names
        for i in range(num_datapoints_to_run):
            row_dict: dict = {}
            for key in keys:
                row_dict[key] = dataset[key][i]
            #rof
            row_orient_dataset.append(row_dict)
        #rof
        return row_orient_dataset
    #fed

    def run(self, dataset: List) -> List:
        """
        Run the experiments on the provided dataset
        """
        print(f"Start running experiments: {str(self.args)} ...")
        # temp = 0.0
        results = []
        for p in tqdm(dataset, total=len(dataset)):
            chat_prompt = self._prepare_prompt(p)
            result = self.query_llm(p, chat_prompt=chat_prompt)
            results.append(result)
        #rof
        return results
    #fed

    def query_llm(self, dt: dict, chat_prompt: List[dict]) -> dict:
        """
        Query LLM with the **single** data.
        """
        res = {}
        res.update(
            {
                key: value
                for key, value in dt.items()
                if key not in {"syntax", "semantics"}
            }
        )
        # query llm
        chat = self._assemble_chat(chat_prompt)
        model_responses = self._query(chat)
        if model_responses:
            res["model-prediction"] = model_responses[0]
        else:
            res["model-prediction"] = ""
        #fi
        return res
    #fed

    def _assemble_chat(self, chat_prompt: List[dict[str, str]]) -> List[dict[str, str]]:
        """Create the chat format for LLMs."""
        if "deepseek" in self.args.model_name:
            # remove system prompt according to the deepseek model card
            chat = chat_prompt
        else:
            chat = self._system + chat_prompt
        #fi
        return chat
    #fed

    def _prepare_prompt(self, dt: dict) -> List[dict]:
        """Return the prompt string given the data."""
        chat = []
        match self.args.task:
            case Task.PredState:
                chat = make_predstate_prompt(self.args, dt)
            case Task.PredRule:
                chat = make_predrule_prompt(self.args, dt)
            case Task.PredTrace:
                chat = make_predtrace_prompt(self.args, dt)
            case _:
                raise NotImplementedError(
                    f"Prompt for {str(self.args)} is not implemented yet."
                )
        #hctam   
        return chat
    #fed
