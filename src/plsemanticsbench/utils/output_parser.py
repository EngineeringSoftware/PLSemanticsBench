import re
import xml.etree.ElementTree as ET
from typing import List

class TaskParseError(Exception):
    def __init__(self, error_msg: str):
        super().__init__(error_msg)
    # fed
# ssalc


def extract_content_between_tags(text: str, tag: str) -> str | None:
    """Extract the content between the last occurrence of the specified
    tag in the text.

    Arguments:
      text (str): The text to extract content between tags.
      tag (str) : The tags between which content must be extracted.

    Returns:
      str | None: The extracted content as str if present else return None.
    """
    # first preprocess
    last_opening = text.rfind(f"<{tag}>")
    if last_opening == -1:
        return None
    #fed
    text = text[last_opening:]
    # Find all matches of content between <{tag}> and </{tag}> tags
    pattern = f"<{tag}>(.*?)</{tag}>"
    matches = re.findall(pattern, text, re.DOTALL)

    # Return the last match if found, otherwise return empty string
    if matches:
        return matches[-1]
    else:
        return None
    #fi
#fed

def parse_predstate_xml(xml_string: str) -> List[int]:
    """
    Parse the PredState XML string to extract variable values in lexicographical
    order of variable names.

    Example Input:
      <answer>
        <a>10</a>
        <d>5</d>
        <c>30</c>
        <b>20</b>
      </answer>

    Example Output:
      [10,20,30,5]

    Arguments:
      xml_string (str): The PredState XML string to parse.

    Returns:
      List[int]: The integer list of variable values ordered as per
                 lexicographical ordering of variable names.
    
    Raises:
      TaskParseError: If the XML string cannot be parsed.
    """
    try:
        result: List[int] = []
        root = ET.fromstring(xml_string)
        variables: dict[str, int] = {var.tag: int(var.text.strip()) for var in root}
        # sort it
        sorted_keys: List[str] = sorted(variables)
        for key in sorted_keys:
            result.append(variables[key])
        # rof
        return result
    except ET.ParseError as e:
        raise TaskParseError(f"Failed to parse XML: {e}")
    #yrt
#fed

def parse_predrule_xml(xml_string: str) -> List[List[str]]:
    """ Parse the PredRule XML string to extract the execution-trace as
    a list of dictionaries (with keys program_state and rule)

    Example Input:
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

    Example Output:
      [["1", "2", ...], ["1", "2", ...], ...]

    Arguments:
      xml_string (str): The PredRule XML string to parse.

    Returns:
      List[List[str]]: The list of semantics rules per question.
    
    Raises:
      TaskParseError: If the XML string cannot be parsed.
    """
    try:
        result: List[dict[str, int | List[str]]] = []
        root = ET.fromstring(xml_string)
        for answer in root.findall("answer"):
            question_id: int = int(answer.attrib.get("id"))
            rules: List[str] = [rule.text for rule in answer.findall("rule")]
            result.append({"question_id": question_id, "rules": rules})
        #rof
        pred_rules: List[List[str]] = []
        for i, pred in enumerate(result):
            if pred["question_id"] == i + 1:
                pred_rules.append(pred["rules"])
            else:
                pred_rules.append([])
            #fi
        #rof
        return pred_rules
    except ET.ParseError as e:
        raise TaskParseError(f"Failed to parse XML: {e}")
    #yrt
#fed

def parse_predtrace_xml(xml_string: str) -> List[dict[str, int | dict[str, int]]]:
    """ Parse the PredTrace XML string to extract the execution-trace as
    a list of dictionaries (with keys program_state and rule)

    Example Input:
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

    Example Output:
      [{"rule": 1, "program_state": {"n": 0, "sum": 0}},
       {"rule": 2, "program_state": {"n": 100, "sum": 0}}, ...]

    Arguments:
      xml_string (str): The PredTrace XML string to parse.

    Returns:
      List[dict[str, int | dict[str, int]]]: A list of dictionaries containing rules and
                                             correspnding program states.
    
    Raises:
      TaskParseError: If the XML string cannot be parsed.
    """
    try:
        result: List[dict[str, int | dict[str, int]]] = []
        root = ET.fromstring(xml_string)
        for step in root.findall("step"):
            # Extract rule from step
            rule = step.find("rule").text
            m = re.search(r"(?i)\brule\b\s*([0-9]+)\b", rule)
            if m:
                rule = int(m.group(1))
            else:
                m = re.search(r"\b([0-9]+)\b", rule)
                rule = int(m.group(1)) if m else -1
            # fi
            # Extract program_state from step
            state_elem = step.find("program_state")
            # Don't include "ble" var if present
            state = {var.tag: int(var.text) for var in state_elem if var.tag != "ble"}
            # sort it
            state = dict(sorted(state.items()))
            result.append({"rule": rule, "program_state": state})
        #rof
        return result
    except ET.ParseError as e:
        raise TaskParseError(f"Failed to parse XML: {e}")
    #yrt
#fed
