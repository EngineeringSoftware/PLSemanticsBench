"""C* source transformations and prompt construction for the interactive demo."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping

DATASET_ID = "EngineeringSoftware/PLSemanticsBench"
MAX_PROGRAM_CHARS = 6_000

INTERVENTIONS = {
    "Standard": {},
    "KeywordSwap": {
        "+": "-",
        "-": "+",
        "*": "/",
        "/": "*",
        "<": ">",
        ">": "<",
        "<=": ">=",
        ">=": "<=",
        "==": "!=",
        "!=": "==",
        "&&": "||",
        "||": "&&",
    },
    "KeywordObf": {
        "+": "𐕐",
        "-": "𐕙",
        "*": "𐕊",
        "/": "𐕏",
        "%": "𐕖",
        "=": "𐕂",
        "<": "𐔳",
        ">": "𐕃",
        "<=": "𐔷",
        ">=": "𐕛",
        "==": "𐕟",
        "!=": "𐕀",
        "&&": "𐕜",
        "||": "𐔻",
        "!": "𐔰",
        "break": "𐔾",
        "if": "𐔸",
        "else": "𐕎",
        "while": "𐕕",
        "halt": "𐔱",
        "continue": "𐔲",
    },
}

FORMALIZATIONS = {
    "Small-step (S)": "S",
    "K semantics": "K",
}

_TOKEN_PATTERN = re.compile(
    r"""
    "(?:\\.|[^"\\])*"             | # string literal
    '(?:\\.|[^'\\])*'             | # character literal
    //[^\n]*                       | # line comment
    /\*.*?\*/                      | # block comment
    <=|>=|==|!=|&&|\|\|            | # multi-character operators
    [+\-*/%=<>!]                   | # single-character operators
    [A-Za-z_][A-Za-z0-9_]*           # identifiers and keywords
    """,
    re.DOTALL | re.MULTILINE | re.VERBOSE,
)


@dataclass(frozen=True)
class SemanticsSpec:
    syntax: str
    semantics: str


def validate_program(program: str) -> str:
    program = program.strip()
    if not program:
        raise ValueError("Enter a C* program before running the model.")
    if len(program) > MAX_PROGRAM_CHARS:
        raise ValueError(
            f"Keep the program under {MAX_PROGRAM_CHARS:,} characters for this demo."
        )
    return program


def transform_program(program: str, intervention: str) -> str:
    """Apply the benchmark's lexical intervention to standard C* source."""
    try:
        replacements = INTERVENTIONS[intervention]
    except KeyError as exc:
        raise ValueError(f"Unknown semantic intervention: {intervention}") from exc

    if not replacements:
        return program

    def replace_token(match: re.Match[str]) -> str:
        token = match.group(0)
        if token.startswith(('"', "'", "//", "/*")):
            return token
        return replacements.get(token, token)

    return _TOKEN_PATTERN.sub(replace_token, program)


def build_predstate_prompt(
    *,
    program: str,
    intervention: str,
    formalization: str,
    specs: Mapping[tuple[str, str], SemanticsSpec],
) -> tuple[str, str]:
    """Build the benchmark-style PredState prompt and transformed source."""
    program = validate_program(program)
    try:
        formalization_key = FORMALIZATIONS[formalization]
    except KeyError as exc:
        raise ValueError(f"Unknown formalization: {formalization}") from exc

    transformed_program = transform_program(program, intervention)
    try:
        spec = specs[(formalization_key, intervention)]
    except KeyError as exc:
        raise ValueError(
            f"No semantics found for {formalization} / {intervention}."
        ) from exc

    if formalization_key == "S":
        formalization_intro = f"""Here is the C* syntax in EBNF:
```
{spec.syntax}
```

Here is the complete small-step operational semantics:
```
{spec.semantics}
```"""
        termination_note = (
            "Execution finishes at one of the terminal configurations "
            "〈ε, σ, χ〉, 〈halt, σ, χ〉, or 〈ERROR, σ, χ〉."
        )
    else:
        formalization_intro = f"""Here is the complete K-framework formalization:
```
{spec.semantics}
```"""
        termination_note = ""

    prompt = f"""You are an interpreter for C*. Use only the supplied formal
semantics, even when a symbol conflicts with its conventional meaning. Assume
the supplied rules are correct.

{formalization_intro}

Here is the C* program:
```
{transformed_program}
```

Predict the values of every declared variable after execution.
{termination_note}
- If execution does not terminate, return <answer>##timeout##</answer>.
- If execution has an error or undefined behavior, return <answer>##error##</answer>.
- Otherwise, put every variable in its own XML tag inside <answer>.

Return only the <answer> XML block. Do not include reasoning or commentary."""

    return prompt, transformed_program
