import json
import traceback
from statistics import mean
from typing import List, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

from ..utils.output_parser import (
    parse_predstate_xml,
    parse_predrule_xml,
    parse_predtrace_xml,
    extract_content_between_tags,
    TaskParseError
)

from .exps.experiment_args import Task, Semantics_Type

@dataclass
class PredStateResults:
    model_name: str = ""
    malformed_cnt: int = 0
    true_ans: List[int] = field(default_factory=list)
    pred_ans: List[int] = field(default_factory=list)

@dataclass
class PredRuleResults:
    model_name: str = ""
    malformed_cnt: int = 0
    pred_rules: List[List[str]] = field(default_factory=list)
    true_rules: List[List[str]] = field(default_factory=list)

@dataclass
class PredTraceResults:
    model_name: str = ""
    malformed_cnt: int = 0
    pred_exe_trace: List[dict[str, str]] = field(default_factory=list)
    true_exe_trace: List[dict[str, str]] = field(default_factory=list)

class LLMEvaluator:

    def __init__(self, task: Task, semantics_type: Semantics_Type):
        self.task = task
        self.semantics_type = semantics_type
        self.PROCESSING_FUNCTION_MAP: dict = {
        "predstate-nk": (self._analyze_predstate_uk, [self._evaluate_predstate_task, self.handle_standard_results]),
        "predstate-uk": (self._analyze_predstate_uk, [self._evaluate_predstate_task, self.handle_standard_results]),
        "predstate-mk": (self._analyze_predstate_mk, [self._evaluate_predstate_task, self.handle_non_standard_results]),
        "predrule-uk" : (self._analyze_predrule_uk,  [self._evaluate_predrule_task, self.handle_standard_results]),
        "predrule-mk" : (self._analyze_predrule_mk,  [self._evaluate_predrule_task, self.handle_non_standard_results]),
        "predtrace-uk": (self._analyze_predtrace_uk, [self._evaluate_predtrace_task, self.handle_standard_results]),
        "predtrace-mk": (self._analyze_predtrace_mk, [self._evaluate_predtrace_task, self.handle_non_standard_results]),
    }
    #fed

    def evaluate_from_file(self, prediction_file: str, model_name: str) -> dict:
        results = []
        with open(prediction_file, 'r') as f:
            # Must be in JSONL format
            results = json.load(f)
        #htiw
        return self.evaluate_from_list(results, model_name)
    #fed

    def evaluate_from_list(self, results: List, model_name: str) -> dict:
        experiments_results = {}
        file_name_pattern = f"{self.task.value}"
        [analyze_func, evaluate_funcs]  = self.PROCESSING_FUNCTION_MAP[f"{self.task.value}-{self.semantics_type.value}"]
        try:
            model_result = analyze_func(results, model_name)
            experiments_results = evaluate_funcs[1](model_result, evaluate_funcs[0])
        except Exception as e:
            print(
                f"Error analyzing {model_name}: {e} {traceback.format_exc()}"
            )
        #yrt
        # dump models' results
        with open(f"metrics-{file_name_pattern}-{model_name}.json", "w") as f:
            json.dump(experiments_results, f, indent=4)
        #htiw
        return experiments_results
    #fed

    def handle_standard_results(self, results: PredStateResults | PredRuleResults | PredTraceResults, eval_func) -> dict:
        return eval_func(results)
    #fed

    def handle_non_standard_results(self, results: PredStateResults | PredRuleResults | PredTraceResults, eval_func) -> dict:
        metrics_dict = {}
        for pattern, result in results.items():
            metrics_dict[pattern] = eval_func(result)
        #rof
        return self._aggregate_pattern_wise_metrics(metrics_dict)
    #fed

    ### Task-specific evaluation methods
    # PredState

    def _analyze_predstate_uk(
        self,
        results: List[dict],
        model_name: str,
    ) -> PredStateResults:
        """Collect results for PredState task with no-semantics/standard semantics."""
        analysis = PredStateResults(model_name=model_name)
        for result in results:
            # Extract ground-truth for PredState
            true_list: List[int] = extract_predstate(result["ground-truth"])
            # Extract model prediction for PredState
            pred_list: List[int] = extract_predstate(result["model-prediction"])
            if len(pred_list) == 0:
                analysis.malformed_cnt += 1
            #fi
            analysis.true_ans.append(true_list)
            analysis.pred_ans.append(pred_list)
        #rof
        return analysis
    #fed

    def _analyze_predstate_mk(
        self,
        results: List[dict],
        model_name: str,
    ) -> dict[str, PredStateResults]:
        """Collect results for PredState task with non-standard semantics."""
        result_by_pattern = defaultdict(list)
        for result in results:
            result_by_pattern[result["mutation-pattern"]].append(result)
        #rof
        model_result_by_pattern: dict[str, PredStateResults] = {}
        for pattern, pattern_results in result_by_pattern.items():
            model_result = self._analyze_predstate_uk(pattern_results, model_name)
            model_result_by_pattern[pattern] = model_result
        #rof
        return model_result_by_pattern
    #fed

    # PredRule
    def _analyze_predrule_uk(
        self,
        results: List[dict],
        model_name: str,
    ) -> PredRuleResults:
        """Collect results for PredRule task with standard semantics."""
        analysis = PredRuleResults(model_name=model_name)
        for result in results:
            # Extract ground-truth for PredRule
            true_rules_list: List[List[str]] = extract_predrule(result["ground-truth"])
            # Extract model prediction for PredRule
            pred_rules_list: List[List[str]] = extract_predrule(result["model-prediction"])
            # Compare the ground-truth and predicted
            true_rules_num = len(true_rules_list)
            pred_rules_num = len(pred_rules_list)
            if pred_rules_num == 0:
                analysis.malformed_cnt += 1
                analysis.pred_rules.extend([[] for _ in range(true_rules_num)])
            elif pred_rules_num < true_rules_num:
                analysis.malformed_cnt += 1
                analysis.pred_rules.extend(pred_rules_list)
                # add empty lists for the missing rules
                analysis.pred_rules.extend(
                    [[] for _ in range(true_rules_num - pred_rules_num)]
                )
            elif pred_rules_num > true_rules_num:
                analysis.malformed_cnt += 1
                analysis.pred_rules.extend(pred_rules_list[:true_rules_num])
            else:
                analysis.pred_rules.extend(pred_rules_list)
            #fi
            analysis.true_rules.extend(true_rules_list)
        #rof
        return analysis
    #fed

    def _analyze_predrule_mk(
        self,
        results: List[dict],
        model_name: str,
    ) -> dict[str, PredRuleResults]:
        """Collect results for PredRule task with non-standard semantics."""
        result_by_pattern = defaultdict(list)
        for result in results:
            result_by_pattern[result["mutation-pattern"]].append(result)
        #rof
        model_result_by_pattern = {}
        for pattern, pattern_results in result_by_pattern.items():
            model_result = self._analyze_predrule_uk(pattern_results, model_name)
            model_result_by_pattern[pattern] = model_result
        #rof
        return model_result_by_pattern
    #fed

    # PredTrace
    def _analyze_predtrace_uk(
        self,
        results: List[dict],
        model_name: str,
    ) -> PredTraceResults:
        """Collect results for PredTrace task with standard semantics."""
        analysis = PredTraceResults(model_name=model_name)
        for result in results:
            true_exec_trace = extract_predtrace(result["ground-truth"])
            pred_exec_trace = extract_predtrace(result["model-prediction"])
            if pred_exec_trace == []:
                analysis.malformed_cnt += 1
            #fi
            analysis.pred_exe_trace.append(pred_exec_trace)
            analysis.true_exe_trace.append(true_exec_trace)
        #rof
        return analysis
    #fed

    def _analyze_predtrace_mk(
        self,
        results: List[dict],
        model_name: str,
    ) -> dict[str, PredTraceResults]:
        """Collect results for PredTrace task with non-standard semantics."""
        result_by_pattern = defaultdict(list)
        for result in results:
            result_by_pattern[result["mutation-pattern"]].append(result)
        #rof
        model_result_by_pattern = {}
        for pattern, pattern_results in result_by_pattern.items():
            model_result = self._analyze_predtrace_uk(pattern_results, model_name)
            model_result_by_pattern[pattern] = model_result
        #rof
        return model_result_by_pattern
    #fed

    # Compute metrics

    def _evaluate_predstate_task(self, results: PredStateResults) -> dict:
        """Computes and prints various evaluation metrics for PredState task."""
        metrics_dict = {
            "accuracy": mean([t == p for t, p in zip(results.true_ans, results.pred_ans)]),
            "malformed-count": results.malformed_cnt,
        }

        return metrics_dict
    #fed

    def _evaluate_predrule_task(self, results: PredRuleResults) -> dict:
        """Computes and prints various evaluation metrics for PredRule task."""
        xmatch_scores = []

        for pred_rules, true_rules in zip(results.pred_rules, results.true_rules):
            if pred_rules == true_rules:
                xmatch_scores.append(1)
            else:
                xmatch_scores.append(0)
            #fi
        #rof

        metrics_dict = {
            "xmatch-accuracy": mean(xmatch_scores),
            "malformed-count": results.malformed_cnt,
        }
        return metrics_dict
    #fed

    def _evaluate_predtrace_task(self, results: PredTraceResults) -> dict:
        """Computes and prints various evaluation metrics for PredTrace task."""
        xmatch_scores = []
        for pred_exe, true_exe in zip(results.pred_exe_trace, results.true_exe_trace):
            if pred_exe == true_exe:
                xmatch_scores.append(1)
            else:
                xmatch_scores.append(0)


        metrics_dict = {
            "xmatch-accuracy": mean(xmatch_scores),
            "malformed-count": results.malformed_cnt,
        }
        return metrics_dict
    #fed

    def _aggregate_pattern_wise_metrics(
        self, metrics_dict: dict[str, dict]
    ) -> dict:
        """Aggregate the pattern-wise metrics into a single dict."""
        final_metrics_dict = {}
        for pattern, metrics in metrics_dict.items():
            for metric, value in metrics.items():
                final_metrics_dict[f"{pattern}-{metric}"] = value
        return final_metrics_dict
    #fed

# helper functions
def extract_predstate(model_output: str) -> List[int]:
    """Extract the PredState result."""
    pred = extract_content_between_tags(model_output, tag="answer")
    if pred is None:
        return []
    #fi
    try:
        return parse_predstate_xml(f"<answer>\n{pred}\n</answer>")
    except TaskParseError as e:
        return []
    #yrt
#fed

def extract_predrule(model_output: str) -> List[List[str]]:
    """Extract the PredRule result."""
    pred = extract_content_between_tags(model_output, tag="ans")
    if pred is None:
        return []
    #fi
    try:
        return parse_predrule_xml(f"<ans>\n{pred}\n</ans>")
    except TaskParseError as e:
        return []
    #yrt
#fed

def extract_predtrace(model_output: str) -> List[dict[str, int | dict[str, int]]]:
    """Extract the PredTrace result."""
    pred = extract_content_between_tags(model_output, tag="answer")
    if pred is None:
        return []
    #fi
    try:
        return parse_predtrace_xml(f"<answer>\n{pred}\n</answer>")
    except TaskParseError as e:
        return []
    #yrt
#fed
