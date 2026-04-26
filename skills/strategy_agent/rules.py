from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import yaml


class RuleOperator(Enum):
    LT = "<"
    GT = ">"
    LTE = "<="
    GTE = ">="
    EQ = "=="


@dataclass
class Rule:
    indicator: str
    operator: RuleOperator
    value: float
    reference: str | None = None
    multiplier: float = 1.0


def load_strategy_config(path: str = "config/strategy.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def parse_rules(config: dict) -> dict:
    entry_conditions = config.get("strategy", {}).get("entry", {}).get("conditions", [])
    exit_conditions = config.get("strategy", {}).get("exit", {}).get("conditions", [])

    entry_rules = [_parse_condition(c) for c in entry_conditions]
    exit_rules = [_parse_condition(c) for c in exit_conditions]

    return {"entry": entry_rules, "exit": exit_rules}


def _parse_condition(condition: dict) -> Rule:
    indicator = condition.get("indicator", "")
    operator_str = condition.get("operator", ">")
    value = condition.get("value", 0)
    reference = condition.get("reference")
    multiplier = condition.get("multiplier", 1.0)

    operator = RuleOperator(operator_str)

    return Rule(
        indicator=indicator,
        operator=operator,
        value=value,
        reference=reference,
        multiplier=multiplier,
    )


def evaluate_rule(rule: Rule, indicators: dict) -> bool:
    actual = indicators.get(rule.indicator)

    if actual is None:
        return False

    if rule.reference:
        ref_value = indicators.get(rule.reference)
        if ref_value is None or ref_value == 0:
            return False
        threshold = ref_value * rule.multiplier
    else:
        threshold = rule.value

    ops = {
        RuleOperator.LT: lambda a, t: a < t,
        RuleOperator.GT: lambda a, t: a > t,
        RuleOperator.LTE: lambda a, t: a <= t,
        RuleOperator.GTE: lambda a, t: a >= t,
        RuleOperator.EQ: lambda a, t: a == t,
    }

    return ops[rule.operator](actual, threshold)
