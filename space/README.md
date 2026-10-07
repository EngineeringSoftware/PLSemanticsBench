---
title: PLSemanticsBench
emoji: 🧭
colorFrom: blue
colorTo: yellow
sdk: gradio
python_version: 3.12.12
app_file: app.py
suggested_hardware: zero-a10g
license: mit
---

# PLSemanticsBench interactive demo

This Space powers the “Try it yourself” panel on the
[PLSemanticsBench project page](https://engineeringsoftware.github.io/PLSemanticsBench/).
It accepts a standard C* program, applies the selected benchmark intervention,
loads the corresponding formal semantics from the
[PLSemanticsBench dataset](https://huggingface.co/datasets/EngineeringSoftware/PLSemanticsBench),
and runs `Qwen/Qwen2.5-7B-Instruct` on ZeroGPU.

The named Gradio API endpoint is `/predict`.
