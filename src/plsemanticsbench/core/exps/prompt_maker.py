from typing import List

from .experiment_args import ExperimentArgs, Semantics_Type
from .prompts import PROMPT_STRATEGY
from .prompts import (
    predstate_nk_prompt_da,
    predstate_nk_prompt_cot,
    predstate_sos_prompt_da,
    predstate_sos_prompt_cot,
    predstate_k_prompt_da,
    predstate_k_prompt_cot,
    predrule_sos_prompt_da,
    predrule_sos_prompt_cot,
    predrule_k_prompt_da,
    predrule_k_prompt_cot,
    predtrace_sos_prompt_da,
    predtrace_sos_prompt_cot,
    predtrace_k_prompt_da,
    predtrace_k_prompt_cot,
    PREDRULE_QUESTIONS,
)

PROMPTS_DICT: dict = {
    # PredState
    "predstate-None-da": predstate_nk_prompt_da,
    "predstate-None-cot": predstate_nk_prompt_cot,
    "predstate-SOS-da": predstate_sos_prompt_da,
    "predstate-SOS-cot": predstate_sos_prompt_cot,
    "predstate-K-da": predstate_k_prompt_da,
    "predstate-K-cot": predstate_k_prompt_cot,
    # PredRule
    "predrule-SOS-da": predrule_sos_prompt_da,
    "predrule-SOS-cot": predrule_sos_prompt_cot,
    "predrule-K-da": predrule_k_prompt_da,
    "predrule-K-cot": predrule_k_prompt_cot,
    # PredTrace
    "predtrace-SOS-da": predtrace_sos_prompt_da,
    "predtrace-SOS-cot": predtrace_sos_prompt_cot,
    "predtrace-K-da": predtrace_k_prompt_da,
    "predtrace-K-cot": predtrace_k_prompt_cot,
}

SEMANTICS_MUTATIONS = {
    "KeywordSwap": {
        "PLUS_OP": "-",
        "MINUS_OP": "+",
        "MUL_OP": "/",
        "DIV_OP": "*",
        "LT_OP": ">",
        "GT_OP": "<",
        "LTEQ_OP": ">=",
        "GTEQ_OP": "<=",
        "EQ_OP": "!=",
        "NEQ_OP": "==",
        "AND_OP": "||",
        "OR_OP": "&&",
    },
    "KeywordObf": {
        "PLUS_OP": "𐕐",
        "MINUS_OP": "𐕙",
        "MUL_OP": "𐕊",
        "DIV_OP": "𐕏",
        "MOD_OP": "𐕖",
        "ASSIGN_OP": "𐕂",
        "LT_OP": "𐔳",
        "GT_OP": "𐕃",
        "LTEQ_OP": "𐔷",
        "GTEQ_OP": "𐕛",
        "EQ_OP": "𐕟",
        "NEQ_OP": "𐕀",
        "AND_OP": "𐕜",
        "OR_OP": "𐔻",
        "NOT_OP": "𐔰",
        "BREAK": "𐔾",
        "IF": "𐔸",
        "ELSE": "𐕎",
        "WHILE": "𐕕",
        "HALT": "𐔱",
        "CONTINUE": "𐔲",
        "LOOP": "𐕣",
        "LE": "𐕠",
        "ERROR": "𐕞",
    }
}

def make_predstate_prompt(args: ExperimentArgs, dt: dict) -> List[dict[str, str]]:
    """Prepare the prompt for the PredState task."""
    prompt_template: str = PROMPTS_DICT[f"{args.task.value}-{args.formalization.value}-{args.prompt_strategy.value}"]
    program: str = dt["program"] if "Standard" in dt["mutation-pattern"] else dt["mutated-program"]
    match args.semantics_type:
        case  Semantics_Type.Non_Standard:
            if "KeywordSwap" in dt["mutation-pattern"]:
                prompt: str = prompt_template.format(
                    language=dt["language"],
                    syntax=dt["syntax"],
                    semantics=dt["semantics"],
                    program=program,
                    ERROR="ERROR",
                    HALT="halt",
                    ASSIGN_OP="=",
                    ADD_OP=SEMANTICS_MUTATIONS["KeywordSwap"]["PLUS_OP"],
                )
            elif "KeywordObf" in dt["mutation-pattern"]:
                prompt: str = prompt_template.format(
                    language=dt["language"],
                    syntax=dt["syntax"],
                    semantics=dt["semantics"],
                    program=program,
                    ERROR=DatasetProcessor.SEMANTICS_MUTATIONS["KeywordObf"]["ERROR"],
                    HALT=DatasetProcessor.SEMANTICS_MUTATIONS["KeywordObf"]["HALT"],
                    ASSIGN_OP=DatasetProcessor.SEMANTICS_MUTATIONS["KeywordObf"]["ASSIGN_OP"],
                    ADD_OP=DatasetProcessor.SEMANTICS_MUTATIONS["KeywordObf"]["PLUS_OP"],
                )
            else:
                raise NotImplementedError(f"Unsupported non-standard semantics {dt['mutation-pattern']}")
            #fi
        case  Semantics_Type.Standard:    
            if "Standard" in dt["mutation-pattern"]:
                prompt: str = prompt_template.format(
                    language=dt["language"],
                    syntax=dt["syntax"],
                    semantics=dt["semantics"],
                    program=program,
                    ERROR="ERROR",
                    HALT="halt",
                    ASSIGN_OP="=",
                    ADD_OP="+",
                )
            else:
                raise NotImplementedError(f"Unsupported standard semantics {dt['mutation-pattern']}")
            #fi
        case  Semantics_Type.No_Semantics:    
            prompt: str = prompt_template.format(
                language=dt["language"],
                program=program,
                ERROR="ERROR",
                HALT="halt",
                ASSIGN_OP="=",
                ADD_OP="+",
            )
    #hctam
    chat: List[dict[str, str]] = [{"role": "user", "content": prompt}]
    return chat
#fed

def make_predrule_prompt(args: ExperimentArgs, dt: dict) -> List[dict[str, str]]:
    """Prepare the prompt for the PredRule task."""
    prompt_template: str = PROMPTS_DICT[f"{args.task.value}-{args.formalization.value}-{args.prompt_strategy.value}"]
    program: str = dt["program"] if "standard" in dt["mutation-pattern"] else dt["mutated-program"]
    if "KeywordSwap" in dt["mutation-pattern"]:
        prompt: str = prompt_template.format(
            language=dt["language"],
            syntax=dt["syntax"],
            semantics=dt["semantics"],
            questions=_prepare_predrule_questions(dt, program),
            LTEQ_OP=SEMANTICS_MUTATIONS["KeywordSwap"]["LTEQ_OP"],
            NOT_OP="!",
            ERROR="ERROR",
            HALT="halt",
            WHILE="while",
            LOOP="loop",
            IF="if",
            ELSE="else",
        )
    elif "KeywordObf" in dt["mutation-pattern"]:
        prompt: str = prompt_template.format(
            language=dt["language"],
            syntax=dt["syntax"],
            semantics=dt["semantics"],
            questions=_prepare_predrule_questions(dt, program),
            LTEQ_OP=DatasetProcessor.SEMANTICS_MUTATIONS["KeywordObf"]["LTEQ_OP"],
            NOT_OP=DatasetProcessor.SEMANTICS_MUTATIONS["KeywordObf"]["NOT_OP"],
            ERROR=DatasetProcessor.SEMANTICS_MUTATIONS["KeywordObf"]["ERROR"],
            HALT=DatasetProcessor.SEMANTICS_MUTATIONS["KeywordObf"]["HALT"],
            WHILE=DatasetProcessor.SEMANTICS_MUTATIONS["KeywordObf"]["WHILE"],
            LOOP=DatasetProcessor.SEMANTICS_MUTATIONS["KeywordObf"]["LOOP"],
            IF=DatasetProcessor.SEMANTICS_MUTATIONS["KeywordObf"]["IF"],
            ELSE=DatasetProcessor.SEMANTICS_MUTATIONS["KeywordObf"]["ELSE"],
        )
    else:
        prompt: str = prompt_template.format(
            language=dt["language"],
            syntax=dt["syntax"],
            semantics=dt["semantics"],
            questions=_prepare_predrule_questions(dt, program),
            LTEQ_OP="<=",
            NOT_OP="!",
            ERROR="ERROR",
            HALT="halt",
            WHILE="while",
            LOOP="loop",
            IF="if",
            ELSE="else",
        )
    #fi
    chat: List[dict[str, str]] = [{"role": "user", "content": prompt}]
    return chat
#fed

def make_predtrace_prompt(args: ExperimentArgs, dt: dict) -> List[dict[str, str]]:
    """Prepare prompt for the PredTrace task."""
    prompt_template: str = PROMPTS_DICT[f"{args.task.value}-{args.formalization.value}-{args.prompt_strategy.value}"]
    program: str = dt["program"] if "standard" in dt["mutation-pattern"] else dt["mutated-program"]
    if "KeywordSwap" in dt["mutation-pattern"]:
        prompt = prompt_template.format(
            language=dt["language"],
            syntax=dt["syntax"],
            semantics=dt["semantics"],
            program=program,
            ERROR="ERROR",
            HALT="halt",
            WHILE="while",
            ASSIGN_OP="=",
            LT_OP=SEMANTICS_MUTATIONS["KeywordSwap"]["LT_OP"],
            PLUS_OP=SEMANTICS_MUTATIONS["KeywordSwap"]["PLUS_OP"],
            IF="if",
            ELSE="else",
        )
    elif "KeywordObf" in dt["mutation-pattern"]:
        prompt = prompt_template.format(
            language=dt["language"],
            syntax=dt["syntax"],
            semantics=dt["semantics"],
            program=program,
            ERROR=DatasetProcessor.SEMANTICS_MUTATIONS["KeywordObf"]["ERROR"],
            HALT=DatasetProcessor.SEMANTICS_MUTATIONS["KeywordObf"]["HALT"],
            WHILE=DatasetProcessor.SEMANTICS_MUTATIONS["KeywordObf"]["WHILE"],
            ASSIGN_OP=DatasetProcessor.SEMANTICS_MUTATIONS["KeywordObf"]["ASSIGN_OP"],
            LT_OP=DatasetProcessor.SEMANTICS_MUTATIONS["KeywordObf"]["LT_OP"],
            PLUS_OP=DatasetProcessor.SEMANTICS_MUTATIONS["KeywordObf"]["PLUS_OP"],
            IF=DatasetProcessor.SEMANTICS_MUTATIONS["KeywordObf"]["IF"],
            ELSE=DatasetProcessor.SEMANTICS_MUTATIONS["KeywordObf"]["ELSE"],
        )
    else:
        prompt = prompt_template.format(
            language=dt["language"],
            syntax=dt["syntax"],
            semantics=dt["semantics"],
            program=program,
            ERROR="ERROR",
            HALT="halt",
            WHILE="while",
            ASSIGN_OP="=",
            LT_OP="<",
            PLUS_OP="+",
            IF="if",
            ELSE="else",
        )
    #fi
    chat = [{"role": "user", "content": prompt}]
    return chat
#fed

###
# Helper functions
###


def _prepare_predrule_questions(dt: dict, program: str) -> str:
    """Prepare questions for the PredRule task."""
    predrule_data = dt["sampled-statements"]
    question_prompt = ""
    for i, srp_dt in enumerate(predrule_data):
        question_prompt += PREDRULE_QUESTIONS.format(
            index=i + 1,
            program_state=srp_dt["prior_state"],
            statement=srp_dt["cleaned_stmt"],
            control_stack=srp_dt["control_stack"],
        )
        question_prompt += "\n\n"
    #rof
    return question_prompt
#fed
