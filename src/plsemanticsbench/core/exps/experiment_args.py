import dataclasses
from enum import StrEnum

from .prompts import PROMPT_STRATEGY

class ConfigError(Exception):
    def __init__(self, error_msg: str):
        super().__init__(error_msg)
    #fed
#fed

def to_exp_enum(enum_cls, enum_str: str):
    for enum_enum in enum_cls:
        if enum_enum.value == enum_str:
            return enum_enum
        #fi
    #rof    
    raise ConfigError(f"Invalid {enum_cls.__name__} setting {enum_str}")
#fed


class Language(StrEnum):
    IMP = "IMP"
#ssalc

class Formalization(StrEnum):
    NONE = "None"
    K = "K"
    SOS = "SOS"
#ssalc

class Task(StrEnum):
    PredState = "predstate"
    PredRule = "predrule"
    PredTrace = "predtrace"
#ssalc

class Semantics_Type(StrEnum):
    No_Semantics = "nk"
    Standard = "uk"
    Non_Standard = "mk"
##ssalc

class PLDataset(StrEnum):
    Human_Written = "human-written"
    LLM_Translated = "llm-translated"
    Fuzzer_Generated = "fuzzer-generated"
##ssalc

class ExperimentArgs:
    def __init__(
        self,
        task: Task,
        formalization: Formalization,
        semantics_type: Semantics_Type,
        dataset: PLDataset,
        prompt_strategy: PROMPT_STRATEGY,
        model_name: str = "",
        language: Language = Language.IMP,
        num_datapoints_to_run: int = -1,
    ):
        self.task = task
        self.formalization = formalization
        self.semantics_type = semantics_type
        self.dataset = dataset
        self.prompt_strategy = prompt_strategy
        self.model_name = model_name
        self.language = language
        self.num_datapoints_to_run = num_datapoints_to_run
    #fed

    @classmethod
    def from_str(
        cls,
        task: str,
        formalization: str,
        semantics_type: str,
        dataset: str,
        prompt_strategy: str,
        model_name: str,
        language: str,
        num_datapoints_to_run: int = -1,            
    ):
        return ExperimentArgs(
            task=to_exp_enum(Task, task),
            formalization=to_exp_enum(Formalization, formalization),
            semantics_type=to_exp_enum(Semantics_Type, semantics_type),
            dataset=to_exp_enum(PLDataset, dataset),
            prompt_strategy=to_exp_enum(PROMPT_STRATEGY, prompt_strategy),
            model_name=model_name,
            language=to_exp_enum(Language, language),
            num_datapoints_to_run=num_datapoints_to_run,
        )
    #fed

    def __str__(self):
        return f"Task: {self.task}, Language: {self.language}, Formalization: {self.formalization}, Semantics Type: {self.semantics_type}, Prompt Strategy: {self.prompt_strategy}, Dataset: {self.dataset}, Model Name: {self.model_name}"
    #fed

    def check_valid_config(self)->bool:
        try:
            self.get_hf_split_name()
            return True
        except ConfigError:
            return False
        #yrt
    #fed

    def get_hf_split_name(self)->str:
        if self.semantics_type == Semantics_Type.No_Semantics and self.formalization != Formalization.NONE: 
            raise ConfigError(f"Formalization must be {Formalization.NONE.value} when semantics type is {Semantics_Type.No_Semantics.value}")
        #fi
        if self.semantics_type != Semantics_Type.No_Semantics and self.formalization == Formalization.NONE:
            raise ConfigError(f"Semantics type must be {Semantics_Type.No_Semantics.value} when formalization is {Formalization.NONE.value}")
        #fi

        if self.formalization == Formalization.NONE:
            return f"{self.task.value}-{self.language.value}-{self.semantics_type.value}-{self.dataset.value}"
        #fi
        return f"{self.task.value}-{self.language.value}-{self.formalization.value}-{self.semantics_type.value}-{self.dataset.value}"
    #fed
#ssalc
