import { Client } from "https://cdn.jsdelivr.net/npm/@gradio/client@2.7.1/dist/index.min.js";

const DEFAULT_PROGRAM = `int a;
int b;
int ans;
a = 10;
b = 3;
ans = (a + b);`;

const INTERVENTIONS = {
  Standard: {
    label: "Standard semantics",
    description: "Familiar symbols retain their conventional meanings."
  },
  KeywordSwap: {
    label: "KeywordSwap · conflicting symbols",
    description: "Operator meanings are exchanged: + ↔ −, × ↔ ÷, < ↔ >, == ↔ !=, and && ↔ ||."
  },
  KeywordObf: {
    label: "KeywordObf · novel symbols",
    description: "Operators and control-flow keywords are replaced with unfamiliar symbols while preserving their behavior."
  }
};

const demo = document.querySelector("#try-it");
const programInput = document.querySelector("#cstar-program");
const formalizationInput = document.querySelector("#try-formalization");
const runButton = document.querySelector("#run-cstar");
const resetButton = document.querySelector("#reset-cstar-program");
const status = document.querySelector("#try-status");
const result = document.querySelector("#try-result");
const transformedProgram = document.querySelector("#transformed-program");
const modelAnswer = document.querySelector("#model-answer");
const rawModelOutput = document.querySelector("#raw-model-output");
const runDetails = document.querySelector("#run-details");
const interventionLabel = document.querySelector("#intervention-label");
const interventionDescription = document.querySelector("#intervention-description");
const tabs = [...document.querySelectorAll(".semantics-tab[data-intervention]")];

let selectedIntervention = "Standard";
let clientPromise;

function selectIntervention(intervention) {
  selectedIntervention = intervention;
  const copy = INTERVENTIONS[intervention];
  interventionLabel.textContent = copy.label;
  interventionDescription.textContent = copy.description;
  tabs.forEach((tab) => {
    const active = tab.dataset.intervention === intervention;
    tab.classList.toggle("active", active);
    tab.setAttribute("aria-selected", String(active));
  });
}

function setRunning(running) {
  runButton.disabled = running;
  runButton.classList.toggle("loading", running);
  runButton.firstChild.textContent = running ? "Running " : "Run model ";
}

function queueMessage(message) {
  const stage = message.stage || message.status;
  if (stage === "pending" || stage === "queued") {
    const position = Number.isInteger(message.position) ? ` · position ${message.position + 1}` : "";
    return `Waiting for ZeroGPU${position}…`;
  }
  if (stage === "generating" || stage === "processing") {
    return "GPU allocated · applying the formal semantics…";
  }
  return "Preparing the ZeroGPU request…";
}

async function getClient() {
  if (!clientPromise) {
    clientPromise = Client.connect(demo.dataset.spaceId);
  }
  return clientPromise;
}

async function runPrediction() {
  const program = programInput.value.trim();
  if (!program) {
    status.textContent = "Enter a C★ program first.";
    programInput.focus();
    return;
  }

  setRunning(true);
  result.hidden = true;
  status.textContent = "Connecting to the Hugging Face Space…";

  try {
    const client = await getClient();
    const job = client.submit("/predict", [
      program,
      selectedIntervention,
      formalizationInput.value
    ]);

    for await (const message of job) {
      if (message.type === "status") {
        status.textContent = queueMessage(message);
      } else if (message.type === "data") {
        const [answer, raw, transformed, details] = message.data;
        modelAnswer.textContent = answer;
        rawModelOutput.textContent = raw;
        transformedProgram.textContent = transformed;
        runDetails.textContent = details;
        result.hidden = false;
        status.textContent = "Prediction complete.";
      }
    }
  } catch (error) {
    clientPromise = undefined;
    const detail = error instanceof Error ? error.message : String(error);
    status.textContent = `The demo could not run: ${detail}`;
  } finally {
    setRunning(false);
  }
}

tabs.forEach((tab) => {
  tab.addEventListener("click", () => selectIntervention(tab.dataset.intervention));
});

runButton?.addEventListener("click", runPrediction);
resetButton?.addEventListener("click", () => {
  programInput.value = DEFAULT_PROGRAM;
  selectIntervention("Standard");
  result.hidden = true;
  status.textContent = "Example restored.";
  programInput.focus();
});

programInput?.addEventListener("keydown", (event) => {
  if (event.key === "Tab") {
    event.preventDefault();
    const start = programInput.selectionStart;
    const end = programInput.selectionEnd;
    programInput.setRangeText("    ", start, end, "end");
  }
});

selectIntervention("Standard");
