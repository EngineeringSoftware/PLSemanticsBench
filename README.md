# PLSemanticsBench

[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Dataset-blue)](https://huggingface.co/datasets/EngineeringSoftware/PLSemanticsBench)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


## Table of Contents
- [About](#about)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Benchmark](#benchmark)
- [Citation](#citation)

## About
PLSemanticsBench is the first benchmark for evaluating LLMs as programming language interpreters. We introduce three tasks to evaluate this:

| Task | Description |
|------|-------------|
| ✨ **PredState**| Predicts the final program state |
| ✨ **PredRule** | Predicts the ordered sequence of semantic rules needed to evaluate a program|
| ✨ **PredTrace**| Predicts the step-by-step execution of a program |

PLSemanticsBench is hosted on HuggingFace: [PLSemanticsBench](https://huggingface.co/datasets/EngineeringSoftware/PLSemanticsBench). 

## Installation

### System Requirements
- Python 3.11 or higher
- OpenAI API key (for running experiments)


### Step-by-Step Installation
1. Create and activate the conda environment:
```bash
conda env create -f env.yaml
conda activate plsemanticsbench
```

2. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```


## Quick Start

### Basic Example
Here's a minimal example to get started:

```python
from plsemanticsbench import GPTRunner, GPT_MODEL_ENUM
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
model_name = "gpt-5-mini"

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
gpt_runner = GPTRunner(
    gpt_model=GPT_MODEL_ENUM.O3_MINI,
    args=exp_args,
)

# If prediction file is provided, the predictions will be saved to the file
predictions = gpt_runner.do_experiment()
llm_eval = LLMEvaluator(exp_args)
evaluation_result = llm_eval.evaluate_from_list(results=predictions, model_name=model_name)
print(evaluation_result)
```

### Expected Output

The evaluation results will look like:
```python
{
    'accuracy': 1,
    'malformed-count': 0,
}
```

## Benchmark
Our benchmark is hosted on HuggingFace: [PLSemanticsBench](https://huggingface.co/datasets/EngineeringSoftware/PLSemanticsBench). 

### Benchmark Access
You can load the dataset using the `datasets` library. Here is an example:
```python
from datasets import load_dataset

# Load PredState task with standard semantics (uk) and K-semantics formalization (K) and with the Human Written (human-written) dataset
predstate_IMP_K_uk_human_written = load_dataset("EngineeringSoftware/PLSemanticsBench", name="predstate-IMP-K-uk-human-written")

# Load PredRule task with nonstandard semantics (mk) ans SOS formalization (SOS) and with the LLM Translated (llm-translated) dataset
predrule_IMP_SOS_mk_llm_translated = load_dataset("EngineeringSoftware/PLSemanticsBench", name="predrule-IMP-SOS-mk-llm-translated")

# Load PredState task with no-semantics (nk) and with the Fuzzer Generated (fuzzer-generated) dataset
predstate_IMP_nk_fuzzer_generated = load_dataset("EngineeringSoftware/PLSemanticsBench", name="predstate-IMP-nk-fuzzer-generated")
```

### Dataset Split

<table>
  <tr>
    <th>Task</th>
    <th>Split</th>
    <th>Description</th>
  </tr>
  <tr>
    <td rowspan="5">✨ <strong>PredState</strong><br>(Final State Prediction)</td>
    <td> predstate-IMP-nk-{dataset-name} </td>
    <td> No semantics </td>
  </tr>
  <tr>
    <td> predstate-IMP-K-uk-{dataset-name} </td>
    <td>Standard semantics with K-semantics formalization</td>
  </tr>
  <tr>
    <td> predstate-IMP-K-mk-{dataset-name} </td>
    <td>Nonstandard semantics with K-semantics formalization</td>
  </tr>
  <tr>
    <td> predstate-IMP-SOS-uk-{dataset-name} </td>
    <td>Standard semantics with SOS formalization</td>
  </tr>
  <tr>
    <td> predstate-IMP-SOS-mk-{dataset-name} </td>
    <td>Nonstandard semantics with SOS formalization</td>
  </tr>
  <tr>
    <td rowspan="4">✨ <strong>PredRule</strong><br>(Semantic Rule Prediction)</td>
    <td> predrule-IMP-K-uk-human-written </td>
    <td>Standard semantics with K-semantics formalization</td>
  </tr>
  <tr>
    <td> predrule-IMP-K-mk-human-written </td>
    <td>Nonstandard semantics with K-semantics formalization</td>
  </tr>
  <tr>
    <td> predrule-IMP-SOS-uk-human-written </td>
    <td>Standard semantics with SOS formalization</td>
  </tr>
  <tr>
    <td> predrule-IMP-SOS-mk-human-written </td>
    <td>Nonstandard semantics with SOS formalization</td>
  </tr>
  <tr>
    <td rowspan="4">✨ <strong>PredTrace</strong><br>(Execution Trace Prediction)</td>
    <td> predtrace-IMP-K-uk-human-written </td>
    <td>Standard semantics with K-semantics formalization</td>
  </tr>
  <tr>
    <td> predtrace-IMP-K-mk-human-written </td>
    <td>Nonstandard semantics with K-semantics formalization</td>
  </tr>
  <tr>
    <td> predtrace-IMP-SOS-uk-human-written </td>
    <td>Standard semantics with SOS formalization</td>
  </tr>
  <tr>
    <td> predtrace-IMP-SOS-mk-human-written </td>
    <td>Nonstandard semantics with SOS formalization</td>
  </tr>
</table>


### Data Example

One example of the dataset is as follows:
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
@article{ThimmaiahETAL25PLSemanticsBench,
  title={PLSemanticsBench: Large Language Models As Programming Language Interpreters},
  author={Aditya Thimmaiah, Jiyang Zhang, Jayanth Srinivasa, Junyi Jessy Li, Milos Gligoric},
  year={2025},
  archivePrefix={arXiv},
  url={https://arxiv.org/abs/2510.03415}, 
}
```


## License
This project is licensed under the CC0-1.0 License - see the [LICENSE](LICENSE) file for details.
