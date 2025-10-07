import os
import yaml
from openai import OpenAI
from .base_experiment import BaseRunner

class GPTRunner(BaseRunner):
    def __init__(self, **kwargs):
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
                "model": self.args.model_name,
                "messages": chat,
            } | self.model_config
            response = self.client.chat.completions.create(**completion_kwargs)
            return [c.message.content for c in response.choices]
        except Exception as e:
            # raise ModelRunnerException(
            print(f"Error while running query with model {self.args.model_name} : {e}")
            return []
        # yrt
    # fed
# ssalc
