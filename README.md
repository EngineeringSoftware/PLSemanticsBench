

<div align="center">
  <p>The 43rd International Conference on Machine Learning (ICML 2026), Seoul, South Korea</p>
  <h1>LLMs Lean on Priors, Not Programming Language Semantics</h1>

  <p style="font-size: 20px;">
    by
    <a href="https://www.adityathimmaiah.com">Aditya Thimmaiah</a><sup>1</sup>,
    <a href="https://jiyangzhang.github.io/">Jiyang Zhang</a><sup>1</sup>,
    <a href="https://scholar.google.com/citations?user=HtNfeKYAAAAJ&hl=en">Jayanth Srinivasa</a><sup>2</sup>,
    <a href="https://www.jessyli.com">Junyi Jessy Li</a><sup>1</sup>,
    <a href="https://users.ece.utexas.edu/~gligoric/">Milos Gligoric</a><sup>1</sup>
  </p>

  <p>
    <sup>1</sup>The University of Texas at Austin &nbsp;&nbsp;&nbsp;
    <sup>2</sup>Cisco Research
  </p>
</div>

<p align="center"><a href="https://engineeringsoftware.github.io/PLSemanticsBench/"><img alt="Project Page" src="https://img.shields.io/badge/Project_Page-PLSemanticsBench-blueviolet"></a> <a href="https://arxiv.org/pdf/2510.03415v3"><img alt="arXiv" src="https://img.shields.io/badge/arXiv-2510.03415v3-b31b1b.svg"></a> <a href="https://github.com/EngineeringSoftware/PLSemanticsBench"><img alt="Code" src="https://img.shields.io/badge/Code-GitHub-black"></a> <a href="https://huggingface.co/datasets/EngineeringSoftware/PLSemanticsBench"><img alt="Dataset" src="https://img.shields.io/badge/🤗-Dataset-yellow"></a></p>

<div align="center">
  <img
src="https://raw.githubusercontent.com/EngineeringSoftware/PLSemanticsBench/main/docs/icons/logo.png"
alt="PLSemanticsBench logo"
width="80">
</div>


## Table of Contents
- [About](#about)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Detailed Usage](#detailed-usage)
- [Benchmark](#benchmark)
- [Citation](#citation)

## About
PLSemanticsBench is the first counterfactual programming language (PL) semantics dataset for evaluating rule-conditioned reasoning in LLMs.
It contains the semantics formalization of `C*`, a featherweight C programming language, in two approaches: small-step 
operational semantics and the K-framework semantics. Execution of `C*` programs under counterfactual and standard semantics is then used as a 
lens for evaluating rule-conditioned reasoning in LLMs via three tasks:

| Task | Description |
|------|-------------|
| ✨ **PredState**| Predict the final program state |
| ✨ **PredRule** | Predict the ordered sequence of semantic rules needed to evaluate a program|
| ✨ **PredTrace**| Predict the step-by-step execution of a program |

It also includes the auxiliary tasks below, to rule out formal notation understanding as an influencing
factor:  

| Task | Description |
|------|-------------|
| ✨ **NL2Rule**| Select the correct formal semantic rule (out of 5) given its natural language description |
| ✨ **Rule2NL** | Select the correct natural language description (out of 5) given the formal semantic rule|

## Installation

### System Requirements
- [Conda](https://docs.conda.io/projects/conda/en/stable/user-guide/install/index.html) package management system
- Python 3.11 or higher
- OpenAI API key (for running experiments with OpenAI models)


### Step-by-Step Installation
1. Create and activate the conda environment:
```bash
conda env create -f env.yaml
conda activate plsemanticsbench
```

2. Set up your OpenAI API key (only for OpenAI models):
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Quick Start

We provide a bash script `quick` that:
 1. Sets up the `plsemanticsbench` conda environment.
 2. Pulls the `DeepSeek-R1 1.5B` model.
 3. Evaluates the `DeepSeek-R1 1.5B` model on the `PredState` task with `no-semantics` and `chain-of-thought` prompting on the `Human-Written` dataset.
 4. Prints the `accuracy` and `malformed-count` to screen.
 5. Creates `metrics-predstate-deepseek-r1:1.5b.json` that contains the evaluation result.
 
```bash
bash quick
```

## Detailed Usage

### Basic Example
Here's a minimal example to get started:

```python
from plsemanticsbench import GPTRunner
from plsemanticsbench import ExperimentArgs, LLMEvaluator
from plsemanticsbench import (
    PROMPT_STRATEGY,
    Task,
    Formalization,
    Semantics_Type,
    Language,
    PLDataset
)

# Model name
model_name = "o3-mini"

# Experiment args: Run the PredState task on the IMP language with
# standard semantics formalized using SOS and with direct prompting
exp_args = ExperimentArgs(
    dataset=PLDataset.Human_Written,
    task=Task.PredState,
    language=Language.IMP,
    formalization=Formalization.SOS,
    semantics_type=Semantics_Type.Standard,
    model_name=model_name,
    prompt_strategy=PROMPT_STRATEGY.DA,
    num_datapoints_to_run=2, # Run just 2 datapoints (omit to run entire dataset)
)
                        
# Run inference using the OpenAI API
gpt_runner = GPTRunner(args=exp_args)

# Generation (generate LLM prediction on the predstate task)
predictions = gpt_runner.do_experiment() # path to dump results can be provided

# Evaluation (evaluate LLM prediction against ground-truth)
llm_eval = LLMEvaluator(task=exp_args.task, semantics_type=exp_args.semantics_type)
evaluation_result = llm_eval.evaluate_from_list(results=predictions, model_name=model_name)
print(evaluation_result)
```

### Expected Output

```python
{
    'accuracy': 1,
    'malformed-count': 0,
}
```

### Extending Providers

You must implement [BaseRunner](https://github.com/EngineeringSoftware/PLSemanticsBench/blob/main/src/plsemanticsbench/core/exps/base_experiment.py)(`_query` method) to evaluate your models. We provide two example implementations for OpenAI models ([GPTRunner](https://github.com/EngineeringSoftware/PLSemanticsBench/blob/main/src/plsemanticsbench/core/exps/gpt_experiment.py)) and Ollama models ([OllamaRunner](https://github.com/EngineeringSoftware/PLSemanticsBench/blob/main/src/plsemanticsbench/core/exps/ollama_experiment.py)).

## Dataset

### Access
You can load the dataset using the `datasets` library. Here is an example:
```python
from datasets import load_dataset

# Load PredState task with standard semantics under K formalization for the LLM Translated dataset
predstate_K_standard_llm_translated = load_dataset("EngineeringSoftware/PLSemanticsBench", name="predstate/K-Standard-llm-translated")

# Load PredRule task with nonstandard semantics under S formalization for the Human Written dataset
predrule_S_nonstandard_human_written = load_dataset("EngineeringSoftware/PLSemanticsBench", name="predrule/S-NonStandard-human-written")

# Load PredState task with standard semantics but without explicitly providing the formal semantics rules, for the Fuzzer Generated dataset
predstate_none_fuzzer_generated = load_dataset("EngineeringSoftware/PLSemanticsBench", name="predstate/None-fuzzer-generated")
```

### Splits

<table>
  <tr>
    <th>Task</th>
    <th>Split</th>
    <th>Description</th>
  </tr>
  <tr>
    <td rowspan="5">✨ <strong>PredState</strong><br>(Final State Prediction)</td>
    <td> predstate/None-{dataset-name} </td>
    <td> No semantics </td>
  </tr>
  <tr>
    <td> predstate/K-Standard-{dataset-name} </td>
    <td>Standard semantics with K formalization</td>
  </tr>
  <tr>
    <td> predstate/K-NonStandard-{dataset-name} </td>
    <td>Nonstandard semantics with K formalization</td>
  </tr>
  <tr>
    <td> predstate/S-Standard-{dataset-name} </td>
    <td>Standard semantics with S formalization</td>
  </tr>
  <tr>
    <td> predstate/S-NonStandard-{dataset-name} </td>
    <td>Nonstandard semantics with S formalization</td>
  </tr>
  <tr>
    <td rowspan="4">✨ <strong>PredRule</strong><br>(Semantic Rule Prediction)</td>
    <td> predrule/K-Standard-human-written </td>
    <td>Standard semantics with K formalization</td>
  </tr>
  <tr>
    <td> predrule/K-NonStandard-human-written </td>
    <td>Nonstandard semantics with K formalization</td>
  </tr>
  <tr>
    <td> predrule/S-Standard-human-written </td>
    <td>Standard semantics with S formalization</td>
  </tr>
  <tr>
    <td> predrule/S-NonStandard-human-written </td>
    <td>Nonstandard semantics with S formalization</td>
  </tr>
  <tr>
    <td rowspan="4">✨ <strong>PredTrace</strong><br>(Execution Trace Prediction)</td>
    <td> predtrace/K-Standard-human-written </td>
    <td>Standard semantics with K formalization</td>
  </tr>
  <tr>
    <td> predtrace/K-NonStandard-human-written </td>
    <td>Nonstandard semantics with K formalization</td>
  </tr>
  <tr>
    <td> predtrace/S-Standard-human-written </td>
    <td>Standard semantics with S formalization</td>
  </tr>
  <tr>
    <td> predtrace/S-NonStandard-human-written </td>
    <td>Nonstandard semantics with S formalization</td>
  </tr>
</table>


### Example Data Point

An example of a data point from the `predstate/None-human-written` split:
```json
{
  "program": "int ans; ans = 1; ...",
  "syntax": "<program> :: ...",
  "semantics": "ℤ := Set of integers ...",
  "mutated-program": "int ans; ans = 1; ...",
  "mutation-pattern": "KeyWordSwap",
  "exec-trace": [
    {
      "linenumber": 1,
      "rule": ["Rule 38", "Rule 39"],
      "state": {"ans": 1}
    }
  ],
  "ground-truth": "<answer>...</answer>"
}
```

## Citation
```bibtex
@inproceedings{ThimmaiahETAL25PLSemanticsBench,
  title     = {LLMs Lean on Priors, Not Programming Language Semantics},
  author    = {Aditya Thimmaiah, Jiyang Zhang, Jayanth Srinivasa, Junyi Jessy Li, Milos Gligoric},
  year      = {2026},
  booktitle = {ICML}, 
}
```
