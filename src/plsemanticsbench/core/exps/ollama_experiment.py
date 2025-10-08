import requests
from typing import List
from .base_experiment import BaseRunner

class OllamaRunner(BaseRunner):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "model_config_file" in kwargs:
            model_config_file = kwargs["model_config_file"]
            with open(model_config_file, "r") as f:
                self.model_config = yaml.safe_load(f)
            #htiw
        else:
            print(f"No model config file provided for {self.args.model_name}, using default config.")
            self.model_config = {}
        #fi
        self.ollama_base_url = kwargs.get("ollama_base_url", "http://localhost:11434")
        self.test_client()
    # fed

    def test_client(self):
        # Test connection to Ollama
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags")
            if response.status_code != 200:
                print(f"Ollama connection test failed: {response.status_code}")
            else:
                print(f"Successfully connected to Ollama at {self.ollama_base_url}")
            #fi
        except Exception as e:
            print(f"Could not connect to Ollama at {self.ollama_base_url}: {e}")
        #yrt
    #fed
    
    def _query(self, chat: List[dict]) -> List[str]:
        try:
            # Convert chat format to Ollama format
            messages = []
            for message in chat:
                messages.append(
                    {"role": message["role"], "content": message["content"]}
                )
            #rof
            payload = {
                "model": self.args.model_name,
                "messages": messages,
                "stream": False,
                "options": self.model_config,
            }

            # Make the API call to Ollama
            response = requests.post(f"{self.ollama_base_url}/api/chat", json=payload)

            if response.status_code == 200:
                result = response.json()
                return [result["message"]["content"]]
            else:
                print(f"Ollama API error: {response.status_code} - {response.text}")
                return []
            #fi
        except Exception as e:
            print(f"Error while running query with model {self.args.model_name}: {e}")
            return []
        #yrt
    #fed
#ssalc
