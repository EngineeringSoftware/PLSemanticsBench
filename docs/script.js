const semantics = {
  standard: {
    label: "Standard",
    operator: "+",
    ruleDescription: "<code>+</code> evaluates as integer addition.",
    premise: "v₃ = v₁ + v₂",
    conclusion: "⟨v₁ + v₂, σ⟩ → ⟨v₃, σ⟩",
    calculate: (a, b) => a + b,
    ruleName: "E-ADD",
    commit: (v) => `commit σ[x ↦ ${v}]`
  },
  swap: {
    label: "KeywordSwap",
    operator: "+",
    ruleDescription: "<code>+</code> is explicitly redefined to evaluate as integer subtraction.",
    premise: "v₃ = v₁ − v₂",
    conclusion: "⟨v₁ + v₂, σ⟩ → ⟨v₃, σ⟩",
    calculate: (a, b) => a - b,
    ruleName: "E-SUB (swapped surface symbol)",
    commit: (v) => `commit σ[x ↦ ${v}]`
  },
  obf: {
    label: "KeywordObf",
    operator: "𐔱",
    ruleDescription: "<code>𐔱</code> is a novel symbol explicitly defined to evaluate as integer addition.",
    premise: "v₃ = v₁ + v₂",
    conclusion: "⟨v₁ 𐔱 v₂, σ⟩ → ⟨v₃, σ⟩",
    calculate: (a, b) => a + b,
    ruleName: "E-ADD (obfuscated symbol)",
    commit: (v) => `commit σ[x ↦ ${v}]`
  }
};

let currentMode = "standard";
let traceIndex = 0;

const leftInput = document.querySelector("#left-value");
const rightInput = document.querySelector("#right-value");
const operatorEl = document.querySelector("#program-operator");
const ruleDescription = document.querySelector("#rule-description");
const rulePremise = document.querySelector("#rule-premise");
const ruleConclusion = document.querySelector("#rule-conclusion");
const semanticAnswer = document.querySelector("#semantic-answer");
const priorAnswer = document.querySelector("#prior-answer");
const priorStatus = document.querySelector("#prior-status");
const trace = document.querySelector("#trace");
const stepButton = document.querySelector("#step-button");

function numericValue(input) {
  const value = Number(input.value);
  return Number.isFinite(value) ? value : 0;
}

function updateSemantics() {
  if (
    !leftInput || !rightInput || !operatorEl || !ruleDescription ||
    !rulePremise || !ruleConclusion || !semanticAnswer ||
    !priorAnswer || !priorStatus
  ) {
    return;
  }

  const mode = semantics[currentMode];
  const a = numericValue(leftInput);
  const b = numericValue(rightInput);
  const semantic = mode.calculate(a, b);
  const prior = a + b;

  operatorEl.textContent = mode.operator;
  ruleDescription.innerHTML = mode.ruleDescription;
  rulePremise.textContent = mode.premise;
  ruleConclusion.textContent = mode.conclusion;
  semanticAnswer.textContent = semantic;
  priorAnswer.textContent = prior;

  const matches = semantic === prior;
  priorStatus.textContent = matches ? "same answer" : "ignores semantics";
  priorStatus.classList.toggle("bad", !matches);
  priorStatus.classList.toggle("neutral", matches);

  if (trace) {
    trace.innerHTML = `
      <div class="trace-step active"><span>01</span><code>parse x = (${a} ${mode.operator} ${b})</code></div>
      <div class="trace-step"><span>02</span><code>select ${mode.ruleName}</code></div>
      <div class="trace-step"><span>03</span><code>${mode.commit(semantic)}</code></div>
    `;
    traceIndex = 0;
  }
}

document.querySelectorAll(".semantics-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    currentMode = tab.dataset.mode;
    document.querySelectorAll(".semantics-tab").forEach((item) => {
      const active = item === tab;
      item.classList.toggle("active", active);
      item.setAttribute("aria-selected", String(active));
    });
    updateSemantics();
  });
});

[leftInput, rightInput].forEach((input) => {
  if (input) {
    input.addEventListener("input", updateSemantics);
  }
});

if (stepButton && trace) {
  stepButton.addEventListener("click", () => {
    const steps = [...trace.querySelectorAll(".trace-step")];
    traceIndex = (traceIndex + 1) % steps.length;
    steps.forEach((step, index) => step.classList.toggle("active", index <= traceIndex));
  });
}

const tasks = {
  state: {
    hypothesis: "Hypothesis H1 · Global conditioning",
    title: "Predict the final state.",
    description: "Compose many rule applications across control and data flow to determine all variable values after termination.",
    example: `<ans>\n  <n>5</n>\n</ans>`
  },
  rule: {
    hypothesis: "Hypothesis H2 · State-free conditioning",
    title: "Select the semantic rules.",
    description: "Identify the ordered rule sequence for execution while removing intermediate state mutation as a confound.",
    example: `<ans>\n  <rule>1</rule>\n  <rule>3</rule>\n  <rule>21</rule>\n</ans>`
  },
  trace: {
    hypothesis: "Hypothesis H3 · Long-horizon conditioning",
    title: "Generate the full trace.",
    description: "Repeatedly choose rules, preserve intermediate stores, and stay grounded throughout loops and nested control flow.",
    example: `<step>\n  <rule>36</rule>\n  <state><n>0</n></state>\n</step>\n…`
  }
};

document.querySelectorAll(".task-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    const task = tasks[tab.dataset.task];
    document.querySelectorAll(".task-tab").forEach((item) => {
      const active = item === tab;
      item.classList.toggle("active", active);
      item.setAttribute("aria-selected", String(active));
    });
    document.querySelector("#task-hypothesis").textContent = task.hypothesis;
    document.querySelector("#task-title").textContent = task.title;
    document.querySelector("#task-description").textContent = task.description;
    document.querySelector("#task-example").textContent = task.example;
  });
});

const GROUP_LABELS = {
  nonreasoning: "Non-reasoning",
  cot: "Non-reasoning + Chain-of-thought",
  reasoning: "Reasoning"
};

const MODEL_ICON_RULES = [
  { match: /^Qwen|^QwQ/i, src: "icons/qwen.png", alt: "Qwen" },
  { match: /^Llama/i, src: "icons/meta-color.png", alt: "Meta" },
  { match: /^DS-/i, src: "icons/deepseek.png", alt: "DeepSeek" },
  { match: /^GPT|^o3/i, src: "icons/openai.png", alt: "OpenAI" },
  { match: /^Gemini/i, src: "icons/gemini-color.png", alt: "Google Gemini" }
];

function getModelIcon(modelName) {
  return MODEL_ICON_RULES.find(({ match }) => match.test(modelName)) ?? null;
}

const RESULTS = {
  state: {
    metric: "PredState · exact-match accuracy (%)",
    datasets: {
      human: {
        label: "Human-Written",
        rows: [
          { model: "Qwen2.5-Inst 14B", group: "nonreasoning", na: 33, k: [27, 6, 14], s: [28, 6, 8] },
          { model: "Qwen2.5-Inst 32B", group: "nonreasoning", na: 50, k: [29, 4, 12], s: [33, 4, 19] },
          { model: "Llama-3.3 70B", group: "nonreasoning", na: 32, k: [29, 4, 12], s: [25, 5, 12] },
          { model: "GPT-4o-mini", group: "nonreasoning", na: 31, k: [26, 6, 8], s: [24, 6, 8] },
          { model: "Qwen2.5-Inst 14B", group: "cot", na: 73, k: [70, 2, 48], s: [68, 4, 41] },
          { model: "Qwen2.5-Inst 32B", group: "cot", na: 81, k: [77, 8, 56], s: [69, 3, 33] },
          { model: "Llama-3.3 70B", group: "cot", na: 75, k: [75, 3, 56], s: [77, 2, 48] },
          { model: "GPT-4o-mini", group: "cot", na: 68, k: [78, 2, 38], s: [65, 3, 27] },
          { model: "DS-Qwen 14B", group: "reasoning", na: 65, k: [81, 2, 40], s: [58, 2, 29] },
          { model: "DS-Qwen 32B", group: "reasoning", na: 84, k: [93, 21, 72], s: [95, 3, 77] },
          { model: "DS-Llama 70B", group: "reasoning", na: 80, k: [88, 2, 58], s: [89, 2, 59] },
          { model: "QwQ 32B", group: "reasoning", na: 93, k: [98, 71, 82], s: [98, 7, 86] },
          { model: "o3-mini", group: "reasoning", na: 94, k: [100, 41, 84], s: [100, 63, 95] },
          { model: "GPT-5-mini", group: "reasoning", na: 100, k: [99, 79, 94], s: [100, 79, 99] },
          { model: "Gemini-2.5-pro", group: "reasoning", na: 93, k: [100, 97, 94], s: [99, 98, 100] }
        ],
        note: "The swap condition creates a direct conflict between familiar symbols and supplied meanings.",
        insight: "<strong>Semantic gap:</strong> Near-ceiling standard accuracy does not guarantee robustness. Under K semantics, o3-mini falls from 100% to 41% when meanings are swapped; under small-step semantics, QwQ 32B falls from 98% to 7%."
      },
      translated: {
        label: "LLM-Translated",
        rows: [
          { model: "QwQ 32B", group: "reasoning", na: 82, k: [83, 31, 61], s: [82, 4, 63] },
          { model: "GPT-5-mini", group: "reasoning", na: 94, k: [96, 76, 86], s: [95, 65, 90] },
          { model: "Gemini-2.5-pro", group: "reasoning", na: 91, k: [94, 85, 91], s: [94, 87, 93] }
        ],
        note: "Only the strongest PredState models are evaluated on the more complex splits. Larger programs introduce more control flow, data dependencies, and longer execution traces.",
        insight: "<strong>Complexity compounds mutation:</strong> On translated programs, KeywordSwap remains substantially harder than KeywordObf, especially under small-step semantics (QwQ 32B: 82% → 4%)."
      },
      fuzzer: {
        label: "Fuzzer-Generated",
        rows: [
          { model: "QwQ 32B", group: "reasoning", na: 16, k: [16, 0, 3], s: [15, 0, 1] },
          { model: "GPT-5-mini", group: "reasoning", na: 57, k: [51, 14, 23], s: [55, 17, 23] },
          { model: "Gemini-2.5-pro", group: "reasoning", na: 73, k: [69, 26, 49], s: [69, 39, 47] }
        ],
        note: "Fuzzer-generated programs stress structural scale: median cyclomatic complexity of 100 and up to six levels of loop nesting.",
        insight: "<strong>Structural limit:</strong> Even Gemini-2.5-pro—robust to swaps on simple programs—falls to 26% under KeywordSwap when structural complexity scales up. Frontier models show negative gains from supplied rules on this split."
      }
    }
  },
  rule: {
    metric: "PredRule · exact rule-sequence accuracy (%)",
    datasets: {
      human: {
        label: "Human-Written",
        rows: [
          { model: "Qwen2.5-Inst 14B", group: "nonreasoning", k: [49, 45, 45], s: [19, 19, 17] },
          { model: "Qwen2.5-Inst 32B", group: "nonreasoning", k: [58, 52, 46], s: [17, 24, 19] },
          { model: "Llama-3.3 70B", group: "nonreasoning", k: [45, 42, 45], s: [32, 32, 27] },
          { model: "GPT-4o-mini", group: "nonreasoning", k: [38, 34, 27], s: [27, 27, 21] },
          { model: "Qwen2.5-Inst 14B-CoT", group: "cot", k: [50, 32, 27], s: [12, 10, 6] },
          { model: "Qwen2.5-Inst 32B-CoT", group: "cot", k: [64, 47, 47], s: [29, 26, 24] },
          { model: "Llama-3.3 70B-CoT", group: "cot", k: [69, 46, 50], s: [28, 28, 17] },
          { model: "GPT-4o-mini-CoT", group: "cot", k: [57, 46, 37], s: [27, 26, 24] },
          { model: "DS-Qwen 14B", group: "reasoning", k: [57, 45, 48], s: [22, 21, 20] },
          { model: "DS-Qwen 32B", group: "reasoning", k: [79, 66, 65], s: [47, 38, 38] },
          { model: "DS-Llama 70B", group: "reasoning", k: [34, 10, 27], s: [1, 1, 1] },
          { model: "QwQ 32B", group: "reasoning", k: [92, 85, 76], s: [49, 44, 41] },
          { model: "o3-mini", group: "reasoning", k: [93, 65, 84], s: [80, 72, 67] },
          { model: "GPT-5-mini", group: "reasoning", k: [92, 83, 82], s: [80, 81, 81] },
          { model: "Gemini-2.5-pro", group: "reasoning", k: [99, 98, 90], s: [94, 96, 98] }
        ],
        note: "PredRule removes state mutation entirely: models only select and order the rules governing execution. Programs are drawn from the Human-Written split.",
        insight: "<strong>Priors dominate even locally:</strong> With long-horizon state tracking removed, most models still lose accuracy under KeywordSwap (o3-mini: 93% → 65% under K semantics). Faithful local rule conditioning under shift is rare."
      }
    }
  },
  trace: {
    metric: "PredTrace · exact full-trace accuracy (%)",
    datasets: {
      human: {
        label: "Human-Written",
        rows: [
          { model: "QwQ 32B", group: "reasoning", k: [18, 16, 15], s: [0, 0, 0] },
          { model: "o3-mini", group: "reasoning", k: [19, 3, 13], s: [5, 3, 2] },
          { model: "GPT-5-mini", group: "reasoning", k: [20, 14, 17], s: [17, 15, 17] },
          { model: "Gemini-2.5-pro", group: "reasoning", k: [25, 25, 25], s: [32, 35, 35] }
        ],
        note: "Models must emit every rule application and intermediate state. Only the 4 models (of 11) with non-zero accuracy are shown; all others collapse to 0%. Programs are drawn from the Human-Written split.",
        insight: "<strong>Long horizons are the frontier:</strong> The best full-trace accuracy is 35% (Gemini-2.5-pro under small-step semantics)—and it is the only model whose accuracy improves under semantic shift."
      }
    }
  }
};

const taskSelect = document.querySelector("#task-select");
const datasetSelect = document.querySelector("#dataset-select");
const formalizationSelect = document.querySelector("#formalization-select");
const chart = document.querySelector("#bar-chart");
const chartLegend = document.querySelector("#chart-legend");

function bar(value, className, label) {
  const low = value < 20 ? " low" : "";
  return `
    <div class="bar-track" title="${label}: ${value}%">
      <div class="bar-fill ${className}${low}" style="width:${value}%">
        <span class="bar-value">${value}</span>
      </div>
    </div>
  `;
}

function renderChart() {
  if (!taskSelect || !datasetSelect || !formalizationSelect || !chart || !chartLegend) {
    return;
  }

  const taskKey = taskSelect.value;
  const task = RESULTS[taskKey];

  // Only PredState has multiple dataset splits.
  const availableDatasets = Object.keys(task.datasets);
  [...datasetSelect.options].forEach((option) => {
    option.disabled = !availableDatasets.includes(option.value);
  });
  if (!availableDatasets.includes(datasetSelect.value)) {
    datasetSelect.value = availableDatasets[0];
  }
  datasetSelect.disabled = availableDatasets.length === 1;

  const datasetKey = datasetSelect.value;
  const formalizationKey = formalizationSelect.value;
  const dataset = task.datasets[datasetKey];
  const showNa = taskKey === "state";

  document.querySelector("#chart-metric").textContent = task.metric;
  document.querySelector("#chart-title").textContent =
    `${dataset.label} · ${formalizationKey === "k" ? "K semantics" : "Small-step semantics"}`;
  document.querySelector("#chart-note").textContent = dataset.note;
  document.querySelector("#result-insight-text").innerHTML = dataset.insight;
  chartLegend.querySelector("span:first-child").style.display = showNa ? "" : "none";
  chart.classList.toggle("with-na", showNa);

  let html = "";
  let lastGroup = null;
  const showGroups = dataset.rows.length > 4;

  dataset.rows.forEach((row) => {
    if (showGroups && row.group !== lastGroup) {
      html += `<div class="chart-group-label">${GROUP_LABELS[row.group]}</div>`;
      lastGroup = row.group;
    }
    const [std, swap, obf] = row[formalizationKey];
    const icon = getModelIcon(row.model);
    const iconHtml = icon
      ? `<img class="model-icon" src="${icon.src}" alt="${icon.alt} logo" title="${icon.alt}">`
      : "";
    html += `
      <div class="chart-row">
        <div class="chart-label" title="${row.model}">
          ${iconHtml}
          <span class="chart-label-text">${row.model}</span>
        </div>
        <div class="bars${showNa ? " four" : ""}">
          ${showNa ? bar(row.na, "na", "No semantics") : ""}
          ${bar(std, "std", "Standard")}
          ${bar(swap, "swap", "KeywordSwap")}
          ${bar(obf, "obf", "KeywordObf")}
        </div>
      </div>
    `;
  });

  chart.innerHTML = html;
}

if (taskSelect) {
  taskSelect.addEventListener("change", renderChart);
}
if (datasetSelect) {
  datasetSelect.addEventListener("change", renderChart);
}
if (formalizationSelect) {
  formalizationSelect.addEventListener("change", renderChart);
}

const heroBibtexToggle = document.querySelector("#toggle-bibtex");
const heroCitation = document.querySelector("#hero-citation");
const heroCopyBibtex = document.querySelector("#copy-hero-bibtex");
const legacyCopyBibtex = document.querySelector("#copy-bibtex");

function bindBibtexCopy(button, textNode) {
  if (!button || !textNode) {
    return;
  }
  button.addEventListener("click", async (event) => {
    const currentButton = event.currentTarget;
    const text = textNode.textContent;
    try {
      await navigator.clipboard.writeText(text);
      currentButton.textContent = "Copied";
    } catch {
      currentButton.textContent = "Select text to copy";
    }
    setTimeout(() => {
      currentButton.textContent = "Copy citation";
    }, 1800);
  });
}

if (heroBibtexToggle && heroCitation) {
  heroBibtexToggle.addEventListener("click", () => {
    const isHidden = heroCitation.hasAttribute("hidden");
    if (isHidden) {
      heroCitation.removeAttribute("hidden");
    } else {
      heroCitation.setAttribute("hidden", "");
    }
    heroBibtexToggle.setAttribute("aria-expanded", String(isHidden));
  });
}

bindBibtexCopy(heroCopyBibtex, document.querySelector("#hero-bibtex"));
bindBibtexCopy(legacyCopyBibtex, document.querySelector("#bibtex"));

updateSemantics();
renderChart();
