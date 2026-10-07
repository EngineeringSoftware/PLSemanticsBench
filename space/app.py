"""ZeroGPU Gradio app for the PLSemanticsBench interactive demo."""

from __future__ import annotations

import re
import time

import spaces
import gradio as gr
import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

from cstar import (
    DATASET_ID,
    INTERVENTIONS,
    SemanticsSpec,
    build_predstate_prompt,
)

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
DEFAULT_PROGRAM = """int a;
int b;
int ans;
a = 10;
b = 3;
ans = (a + b);"""


def _load_semantics() -> dict[tuple[str, str], SemanticsSpec]:
    specs: dict[tuple[str, str], SemanticsSpec] = {}
    for formalization in ("S", "K"):
        standard_split_name = f"{formalization}_Standard_Human_Written"
        standard_split = load_dataset(
            "parquet",
            data_files=(
                f"https://huggingface.co/datasets/{DATASET_ID}/resolve/main/"
                f"predstate/{standard_split_name}-00000-of-00001.parquet"
            ),
            split="train",
        )
        standard = standard_split[0]
        specs[(formalization, "Standard")] = SemanticsSpec(
            syntax=standard["syntax"],
            semantics=standard["semantics"],
        )

        nonstandard_split_name = f"{formalization}_NonStandard_Human_Written"
        nonstandard_split = load_dataset(
            "parquet",
            data_files=(
                f"https://huggingface.co/datasets/{DATASET_ID}/resolve/main/"
                f"predstate/{nonstandard_split_name}-00000-of-00001.parquet"
            ),
            split="train",
        )
        for intervention in ("KeywordSwap", "KeywordObf"):
            record = next(
                (
                    row
                    for row in nonstandard_split
                    if row["mutation-pattern"] == intervention
                ),
                None,
            )
            if record is None:
                raise RuntimeError(
                    f"{intervention} is missing from {nonstandard_split_name}."
                )
            specs[(formalization, intervention)] = SemanticsSpec(
                syntax=record["syntax"],
                semantics=record["semantics"],
            )
    return specs


SEMANTICS_SPECS = _load_semantics()
TOKENIZER = AutoTokenizer.from_pretrained(MODEL_ID)
MODEL = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype=torch.bfloat16,
).to("cuda")
MODEL.eval()


def _extract_answer(response: str) -> str:
    matches = re.findall(r"<answer>.*?</answer>", response, flags=re.DOTALL)
    return matches[-1].strip() if matches else response.strip()


@spaces.GPU(duration=30)
def predict(
    program: str,
    intervention: str,
    formalization: str,
) -> tuple[str, str, str, str]:
    """Run one benchmark-style PredState request on ZeroGPU."""
    started = time.perf_counter()
    prompt, transformed_program = build_predstate_prompt(
        program=program,
        intervention=intervention,
        formalization=formalization,
        specs=SEMANTICS_SPECS,
    )
    messages = [{"role": "user", "content": prompt}]
    model_inputs = TOKENIZER.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_tensors="pt",
        return_dict=True,
    ).to("cuda")
    input_ids = model_inputs["input_ids"]

    with torch.inference_mode():
        generated = MODEL.generate(
            **model_inputs,
            max_new_tokens=512,
            do_sample=False,
            pad_token_id=TOKENIZER.eos_token_id,
        )

    response = TOKENIZER.decode(
        generated[0, input_ids.shape[-1] :],
        skip_special_tokens=True,
    ).strip()
    answer = _extract_answer(response)
    elapsed = time.perf_counter() - started
    run_details = (
        f"{MODEL_ID} · {intervention} · {formalization} · {elapsed:.1f}s"
    )
    return answer, response, transformed_program, run_details


with gr.Blocks(title="PLSemanticsBench · Try C*") as demo:
    gr.Markdown(
        """
# Try C* under counterfactual semantics

Enter a standard C* program. The app applies the selected PLSemanticsBench
intervention, supplies the corresponding formal semantics to the model, and
asks it to predict the final state.
"""
    )
    with gr.Row():
        intervention_input = gr.Radio(
            choices=list(INTERVENTIONS),
            value="Standard",
            label="Semantic intervention",
        )
        formalization_input = gr.Dropdown(
            choices=["Small-step (S)", "K semantics"],
            value="Small-step (S)",
            label="Formalization",
        )
    program_input = gr.Code(
        value=DEFAULT_PROGRAM,
        language="c",
        label="Standard C* program",
        lines=12,
    )
    run_button = gr.Button("Run model", variant="primary")
    answer_output = gr.Code(label="Predicted final state", language="html")
    with gr.Accordion("Program after intervention", open=True):
        transformed_output = gr.Code(language="c")
    with gr.Accordion("Raw model output", open=False):
        raw_output = gr.Textbox(lines=10)
    details_output = gr.Textbox(label="Run details", interactive=False)

    run_button.click(
        fn=predict,
        inputs=[program_input, intervention_input, formalization_input],
        outputs=[
            answer_output,
            raw_output,
            transformed_output,
            details_output,
        ],
        api_name="predict",
    )

demo.queue(default_concurrency_limit=1).launch()
