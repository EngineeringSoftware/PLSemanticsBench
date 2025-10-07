from enum import StrEnum

# ============================================================================
# Constants and Enums
# ============================================================================

class PROMPT_STRATEGY(StrEnum):
    """Strategy for generating prompts."""
    COT = "cot"  # Chain of Thought
    DA = "da"  # Direct Answer
#ssalc


# ============================================================================
# Base Prompts
# ============================================================================

# System-level prompts
system_prompt = """You are an expert in Programming Language and Formal Methods."""
concise_reason_prompt = """Keep the reasoning concise and to the point"""

# ============================================================================
# Task Descriptions
# ============================================================================

# Final State Prediction (PredState) Task
predstate_task_desc = """## TASK:
predict the values of all the declared variables after executing the above program.
- If you think the program will never terminate, answer with the special word '##timeout##':

    <answer>##timeout##</answer>

- If you believe the program has an error or has undefined behavior, answer with the special word '##error##':

    <answer>##error##</answer>

- Otherwise, provide the predicted values of all the declared variables in the following format:

    <answer>[Your answer]</answer>


Here is one example:
** Program **
```
int a;
int b;
int ans;
int c;
a {ASSIGN_OP} 10;
b {ASSIGN_OP} 23;
c {ASSIGN_OP} 12;
ans {ASSIGN_OP} a {ADD_OP} b;
```

The final expected output is:
<answer>
  <a>10</a>
  <b>23</b>
  <c>12</c>
  <ans>33</ans>
</answer>
"""

predstate_task_da_desc = (
    predstate_task_desc
    + """
Only write the answer. You **MUST** wrap your prediction with `<answer>` tags.
"""
)

predstate_task_cot_desc = (
    predstate_task_desc
    + """
Explain your reasoning step-by-step **before** answering. Wrap your reasoning in `<reason>` tags.
Note that you **MUST** wrap your reasoning steps with `<reason>` tags and the prediction with `<answer>` tags.
"""
)

# Semantic Rule Prediction (PredRule) Task
predrule_task_desc_sos = """## TASK:
For each question below, you will be given:
1. A program
2. The program state (`𝜎`) (variable values) before executing the program
3. The control stack (`χ`) before executing the program

Assume that all necessary variables have been declared and have the values as
indicated in the provided program state.

You must:
- Correctly identify and apply the small-step operational semantic rules required to evaluate the program to completion
- List them in the correct order of application

A program is executed completely when its evaluation reaches one of the terminal
configurations 〈ε,𝜎,χ〉,〈{HALT},𝜎,χ〉,〈{ERROR},𝜎,χ〉.

Here is one example:
** Program:**
```
{WHILE} (n {LTEQ_OP} 0)
{{
    {HALT};
}};
```

**Program state(𝜎) before execution:**
{{'n': 100, 'sum': 0}}

**Control stack(χ) before execution:**
 `ε`


This is the sequence of steps:
1. First, we transform the `{WHILE}` into `{LOOP}` using **Rule 67**.
2. Reduce the loop predicate using **Rule 68**.
3. The loop predicate is a {LTEQ_OP} operator which triggers **Rule 32** to first reduce the left-hand side `n` to a literal using **Rule 1**.
4. The right-hand side is already a literal and since `100` is not less-than or equal to `0`. We use **Rule 35** to evaluate this operation to `false`.
5. Since the loop predicate is `false`, we use **Rule 69** to terminate the loop.
6. Since there are no more statements left, we have reached the terminal configuration 〈ε,𝜎,χ〉 and the program evaluation terminates.

Therefore, the final answer is:
<ans>
  <answer id="1">
    <rule>67</rule>
    <rule>68</rule>
    <rule>32</rule>
    <rule>1</rule>
    <rule>35</rule>
    <rule>69</rule>
  </answer>
</ans>


## Questions:
{questions}

## Response Format:
Respond with an XML block structured as follows:

<ans>
  <answer id="1">
    <rule>1</rule>
    <rule>2</rule>
    ...
  </answer>
  <answer id="2">
    <rule>1</rule>
    <rule>2</rule>
    ...
  </answer>
  ...
</ans>

### Notes:
- Each `<answer id="N">` element corresponds to the N-th question.
- Inside each `<answer>` block, list each semantic rule in the correct order using `<rule>` tags.

## Important Notes:
- The **order** of rules matters and should reflect the evaluation sequence.
- A single rule may be needed to be applied multiple times during evaluation.
- You must include **all** semantic rules required for complete execution.
- Base your analysis solely on the provided semantics, not on general programming knowledge.
"""

predrule_task_desc_k = """## TASK:
For each question below, you will be given:
1. A program
2. The program state (`𝜎`) (variable values) before executing the program
3. The control stack (`χ`) before executing the program

Assume that all necessary variables have been declared and have the values as
indicated in the provided program state.

You must:
- Correctly identify and apply the K-semantic rules required to evaluate the program to completion
- List them in the correct order of application

Here is one example:
** Program:**
```
{WHILE} (n {LTEQ_OP} 0)
{{
    {HALT};
}};
```

**Program state(𝜎) before execution:**
{{'n': 100, 'sum': 0}}

**Control stack(χ) before execution:**
 `ε`


This is the sequence of steps:
1. First, we transform the `{WHILE}` into `{WHILE}1` while also inserting a `breakMarker` after `{WHILE}1` using **Rule 24**.
2. Next we transform the `{WHILE}1` into an `{IF}-{ELSE}` with the `{WHILE}1` as the body of the `{IF}` using **Rule 25**.
3. We then reduce the loop predicate to a boolean by first reducing left-hand-side which is a variable using **Rule 1** and then applying the `{LTEQ_OP}` using **Rule 13**.
4. Since the loop predicate evaluates to `false`, we apply the `{IF}` not taken rule **Rule 23** to take the `{ELSE}` branch which is empty.
5. Finally, we evaluate the `breakMarker` statement using **Rule 27** to conclude the program execution.

Therefore, the final answer is:
<ans>
  <answer id="1">
    <rule>24</rule>
    <rule>25</rule>
    <rule>1</rule>
    <rule>13</rule>
    <rule>23</rule>
    <rule>27</rule>
  </answer>
</ans>


## Questions:
{questions}

## Response Format:
Respond with an XML block structured as follows:

<ans>
  <answer id="1">
    <rule>1</rule>
    <rule>2</rule>
    ...
  </answer>
  <answer id="2">
    <rule>1</rule>
    <rule>2</rule>
    ...
  </answer>
  ...
</ans>

### Notes:
- Each `<answer id="N">` element corresponds to the N-th question.
- Inside each `<answer>` block, list each semantic rule in the correct order using `<rule>` tags.

## Important Notes:
- The **order** of rules matters and should reflect the evaluation sequence.
- Only rules that have names indicated in `[]` adjacent to it must be reported in the answer.
- A single rule may be needed to be applied multiple times during evaluation.
- You must include **all** semantic rules required for complete execution.
- Base your analysis solely on the provided semantics, not on general programming knowledge.
"""

predrule_task_cot_desc_sos = (
    predrule_task_desc_sos
    + """
Explain your reasoning step-by-step **before** answering. Wrap your reasoning in `<reason>` tags.
"""
)

predrule_task_da_desc_sos = (
    predrule_task_desc_sos
    + """
Only output the `<ans>` XML block. Do not include any other content.
"""
)

predrule_task_cot_desc_k = (
    predrule_task_desc_k
    + """
Explain your reasoning step-by-step **before** answering. Wrap your reasoning in `<reason>` tags.
"""
)

predrule_task_da_desc_k = (
    predrule_task_desc_k
    + """
Only output the `<ans>` XML block. Do not include any other content.
"""
)

# Execution Trace Prediction (PredTrace) Task
predtrace_task_desc_sos = """## TASK:
Given a program and its semantics, predict the execution trace. Your goal is to simulate execution, step by step of executing the program using the given small-step operational semantics rules. Do not skip any rules that are needed to evaluate the program. You will output your answer in the following format.

## Response Format:
Respond with an XML block structured as follows:

<answer>
  <step>
    <rule>1</rule>
    <program_state>
        <n>0</n>
        <sum>0</sum>
    </program_state>
  </step>
  <step>
    <rule>2</rule>
    <program_state>
      <n>100</n>
      <sum>0</sum>
    </program_state>
  </step>
  ...
</answer>

## Here is an example:

Here is the {language} program:
```
int i;
int j;
i {ASSIGN_OP} 0;
{WHILE} (i {LT_OP} 2)
{{
    {HALT};
}};
```

## Expected output:

<answer>
  <step>
    <rule>3</rule>
    <program_state>
        <i>0</i>
    </program_state>
  </step
  <step>
    <rule>3</rule>
    <program_state>
        <i>0</i>
        <j>0</j>
    </program_state>
  </step>
  <step>
    <rule>5</rule>
    <program_state>
        <i>0</i>
        <j>0</j>
    </program_state>
  </step>
  <step>
    <rule>67</rule>
    <program_state>
        <i>0</i>
        <j>0</j>
    </program_state>
  </step>
  <step>
    <rule>68</rule>
    <program_state>
        <i>0</i>
        <j>0</j>
    </program_state>
  </step>
  <step>
    <rule>28</rule>
    <program_state>
        <i>0</i>
        <j>0</j>
    </program_state>
  </step>
  <step>
    <rule>1</rule>
    <program_state>
        <i>0</i>
        <j>0</j>
    </program_state>
  </step>
  <step>
    <rule>30</rule>
    <program_state>
        <i>0</i>
        <j>0</j>
    </program_state>
  </step>
  <step>
    <rule>70</rule>
    <program_state>
        <i>0</i>
        <j>0</j>
    </program_state>
  </step>
  <step>
    <rule>78</rule>
    <program_state>
        <i>0</i>
        <j>0</j>
    </program_state>
  </step>
</answer>


## Notes:
- Each `<step>` must correspond to **exactly one small-step operational semantics rule** that is needed to evaluate a statement in the given program.
- The `<rule>` must indicate a rule used in the evaluation of a statement.
- The `<program_state>` must represent the **entire program state immediately after** the execution of that rule.
- The program state must list **all variables currently in scope**, using the variable names as XML tags and their current values as tag content.
- Include variables even if they did not change.
- Do not skip any step or merge multiple steps into one.
- Do not skip any rules (including those used to reduce expressions and variables) that are needed to evaluate the program.
- The program execution is complete when on of the terminal configurations 〈ε,𝜎,χ〉,〈{HALT},𝜎,χ〉,〈{ERROR},𝜎,χ〉 is reached
"""

predtrace_task_desc_k = """## TASK:
Given a program and its semantics, predict the execution trace. Your goal is to simulate execution, step by step of executing the program using the given K-semantics rules. Do not skip any rules that are needed to evaluate the program. You will output your answer in the following format.

## Response Format:
Respond with an XML block structured as follows:

<answer>
  <step>
    <rule>1</rule>
    <program_state>
        <n>0</n>
        <sum>0</sum>
    </program_state>
  </step>
  <step>
    <rule>2</rule>
    <program_state>
      <n>100</n>
      <sum>0</sum>
    </program_state>
  </step>
  ...
</answer>

## Here is an example:

Here is the {language} program:
```
int i;
int j;
i {ASSIGN_OP} 0;
{WHILE} (i {LT_OP} 2)
{{
    {HALT};
}};
```

## Expected output:

<answer>
  <step>
    <rule>36</rule>
    <program_state>
        <i>0</i>
    </program_state>
  </step
  <step>
    <rule>36</rule>
    <program_state>
        <i>0</i>
        <j>0</j>
    </program_state>
  </step>
  <step>
    <rule>21</rule>
    <program_state>
        <i>0</i>
        <j>0</j>
    </program_state>
  </step>
  <step>
    <rule>24</rule>
    <program_state>
        <i>0</i>
        <j>0</j>
    </program_state>
  </step>
  <step>
    <rule>25</rule>
    <program_state>
        <i>0</i>
        <j>0</j>
    </program_state>
  </step>
  <step>
    <rule>1</rule>
    <program_state>
        <i>0</i>
        <j>0</j>
    </program_state>
  </step>
  <step>
    <rule>12</rule>
    <program_state>
        <i>0</i>
        <j>0</j>
    </program_state>
  </step>
  <step>
    <rule>22</rule>
    <program_state>
        <i>0</i>
        <j>0</j>
    </program_state>
  </step>
  <step>
    <rule>26</rule>
    <program_state>
        <i>0</i>
        <j>0</j>
    </program_state>
  </step>
</answer>


## Notes:
- Each `<step>` must correspond to **exactly one K-semantics re-write rule** that is needed to evaluate a statement in the given program.
- Only rules that have names indicated in `[]` adjacent to it must be reported in the answer.
- The `<rule>` must indicate a rule used in the evaluation of a statement.
- The `<program_state>` must represent the **entire program state immediately after** the execution of that rule.
- The program state must list **all variables currently in scope**, using the variable names as XML tags and their current values as tag content.
- Include variables even if they did not change.
- Do not skip any step or merge multiple steps into one.
- Do not skip any rules (including those used to reduce expressions and variables) that are needed to evaluate the program.
"""

predtrace_task_cot_desc_sos = (
    predtrace_task_desc_sos
    + """
Explain your reasoning step-by-step **before** answering. Wrap your reasoning in `<reason>` tags.
Note that you **MUST** wrap your reasoning steps with `<reason>` tags, the prediction with `<answer>` tags.
"""
)

predtrace_task_da_desc_sos = (
    predtrace_task_desc_sos
    + """
Only output the `<answer>` XML block. Do not include explanations, comments, or any other text.
"""
)

predtrace_task_cot_desc_k = (
    predtrace_task_desc_k
    + """
Explain your reasoning step-by-step **before** answering. Wrap your reasoning in `<reason>` tags.
Note that you **MUST** wrap your reasoning steps with `<reason>` tags, the prediction with `<answer>` tags.
"""
)

predtrace_task_da_desc_k = (
    predtrace_task_desc_k
    + """
Only output the `<answer>` XML block. Do not include explanations, comments, or any other text.
"""
)

# ============================================================================
# Prompt Templates
# ============================================================================

BASE_PROMPT_TEMPLATE_SOS_SEMANTICS = """You are an interpreter for a language called {language}. I will describe the syntax for {language} in EBNF and its semantics using small-step operational semantics. You will use this to execute a {language} program. You will only use the rules described in the semantics I provide. Assume all the rules in the semantics I give are correct. A program has finished execution when one of the terminal configurations 〈ε,𝜎,χ〉,〈{HALT},𝜎,χ〉,〈{ERROR},𝜎,χ〉 is reached.

Here is the syntax of {language} in EBNF
```
{syntax}
```

Here is the small-step operational semantics of {language}
```
{semantics}
```
"""

BASE_PROMPT_TEMPLATE_K_SEMANTICS = """You are an interpreter for a language called {language}. I will describe the syntax and the semantics of the language using the K-framework. You will use this to execute a {language} program. You will only use the rules described in the semantics I provide. Assume all the rules in the semantics I give are correct.

Here is the K-framework formalization of {language}
```
{semantics}
```
"""

BASE_PROMPT_TEMPLATE_NO_SEMANTICS = """You are an interpreter for my language called {language}."""

INCLUDE_PROGRAM = """
Here is the {language} program
```
{program}
```
"""


PREDRULE_QUESTIONS = """
### Question {index}:
    ** Program:**
    ```
    {statement}
    ```
**Program state(𝜎) before execution:**
{program_state}

**Control stack(χ) before execution:**
{control_stack}

"""


# PredState Prompts
predstate_nk_prompt_da   = BASE_PROMPT_TEMPLATE_NO_SEMANTICS + INCLUDE_PROGRAM + predstate_task_da_desc
predstate_nk_prompt_cot  = BASE_PROMPT_TEMPLATE_NO_SEMANTICS + INCLUDE_PROGRAM + predstate_task_cot_desc
predstate_sos_prompt_da  =  BASE_PROMPT_TEMPLATE_SOS_SEMANTICS + INCLUDE_PROGRAM + predstate_task_da_desc
predstate_sos_prompt_cot =  BASE_PROMPT_TEMPLATE_SOS_SEMANTICS + INCLUDE_PROGRAM + predstate_task_cot_desc
predstate_k_prompt_da    =  BASE_PROMPT_TEMPLATE_K_SEMANTICS + INCLUDE_PROGRAM + predstate_task_da_desc
predstate_k_prompt_cot   =  BASE_PROMPT_TEMPLATE_K_SEMANTICS + INCLUDE_PROGRAM + predstate_task_cot_desc

# PredRule Prompts
predrule_sos_prompt_da  =  BASE_PROMPT_TEMPLATE_SOS_SEMANTICS + predrule_task_da_desc_sos
predrule_sos_prompt_cot =  BASE_PROMPT_TEMPLATE_SOS_SEMANTICS + predrule_task_cot_desc_sos
predrule_k_prompt_da    =  BASE_PROMPT_TEMPLATE_K_SEMANTICS + predrule_task_da_desc_k
predrule_k_prompt_cot   =  BASE_PROMPT_TEMPLATE_K_SEMANTICS + predrule_task_cot_desc_k

# PredTrace Prompts
predtrace_sos_prompt_da  =  BASE_PROMPT_TEMPLATE_SOS_SEMANTICS + INCLUDE_PROGRAM + predtrace_task_da_desc_sos
predtrace_sos_prompt_cot =  BASE_PROMPT_TEMPLATE_SOS_SEMANTICS + INCLUDE_PROGRAM + predtrace_task_cot_desc_sos
predtrace_k_prompt_da    =  BASE_PROMPT_TEMPLATE_K_SEMANTICS + INCLUDE_PROGRAM + predtrace_task_da_desc_k
predtrace_k_prompt_cot   =  BASE_PROMPT_TEMPLATE_K_SEMANTICS + INCLUDE_PROGRAM + predtrace_task_cot_desc_k
