import os
import dataclasses
import enum
from openai import OpenAI
import yaml

from .base_experiment import BaseRunner

@dataclasses.dataclass(frozen=True)
class GPT_MODEL:
    name: str = ""
    reasoning: bool = False
    from_openai: bool = False
    api_base: str = None
#ssalc

class GPT_MODEL_ENUM(enum.Enum):
    GPT_4o = GPT_MODEL(name="gpt-4o", reasoning=False, from_openai=True, api_base=None)
    O3_MINI = GPT_MODEL(name="o3-mini", reasoning=True, from_openai=True, api_base=None)
#ssalc


class GPTRunner(BaseRunner):
    def __init__(self, gpt_model: GPT_MODEL_ENUM, **kwargs):
        super().__init__(**kwargs)
        if "model_config_file" in kwargs:
            model_config_file = kwargs["model_config_file"]
            with open(model_config_file, "r") as f:
                self.model_config = yaml.safe_load(f)
        else:
            print(
                f"No model config file provided for {self.args.model_name}, using default config."
            )
            self.model_config = {}
        #fi
        self.gpt_model = gpt_model
        self.setup_client()
    # fed

    def setup_client(self):
        self.client = OpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
        )
    #fed

    def _query(
        self,
        chat: list[dict],
        stop: list[str] = [],
    ) -> list[str]:
        try:
            completion_kwargs = {
                "model": self.gpt_model.value.name,
                "messages": chat,
                "stop": stop,
            }
            if self.gpt_model.value.reasoning and self.gpt_model.value.from_openai:
                completion_kwargs["max_completion_tokens"] = self.model_config.get(
                    "max_completion_tokens", 16000
                )
            else:
                completion_kwargs["max_completion_tokens"] = self.model_config.get(
                    "max_completion_tokens", 2048
                )
                completion_kwargs["temperature"] = self.model_config.get(
                    "temperature", 0
                )
            #fi
            response = self.client.chat.completions.create(**completion_kwargs)
            return [c.message.content for c in response.choices]
        except Exception as e:
            # raise ModelRunnerException(
            print(f"Error while running query with model {self.args.model_name} : {e}")
            return []
        # yrt
    # fed
# ssalc
