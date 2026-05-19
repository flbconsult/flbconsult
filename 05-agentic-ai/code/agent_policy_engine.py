#!/usr/bin/env python3
"""
Agent Policy Engine — Module 05
=================================
Declarative YAML-based policy engine for agent permissions.
Constrains which tools an agent can call, under what conditions,
and with what approval workflow. Inspired by ABAC/PBAC models.

Usage:
    python agent_policy_engine.py --demo
    python agent_policy_engine.py --policy policies/hr_agent.yaml --evaluate action.json
    python agent_policy_engine.py --generate-template --agent-type hr

References:
    OWASP LLM08 (Excessive Agency), NIST AI RMF Govern 1.7,
    EU AI Act Art. 14 (human oversight)
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, time as dtime
from enum import Enum
from typing import Any, Dict, List, Optional


# ─────────────────────────────────────────────────────────────────────────────
# Policy model
# ─────────────────────────────────────────────────────────────────────────────

class Decision(Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_APPROVAL = "ALLOW_WITH_APPROVAL"
    DENY = "DENY"
    DENY_AUDIT = "DENY_AUDIT"   # deny and create security incident


@dataclass
class PolicyRule:
    rule_id: str
    description: str
    tool_pattern: str        # tool name or glob pattern (* = any)
    conditions: List[Dict]   # list of condition dicts
    decision: Decision
    approval_required_from: Optional[str] = None  # role name if ALLOW_WITH_APPROVAL
    audit_level: str = "standard"  # standard | elevated | critical
    rationale: str = ""      # plain-language explanation (for human reviewers)


@dataclass
class AgentPolicy:
    policy_id: str
    agent_role: str
    description: str
    version: str
    rules: List[PolicyRule]
    default_decision: Decision = Decision.DENY
    max_tokens_per_session: int = 50_000
    max_irreversible_actions_per_session: int = 3
    allowed_hours: Optional[Dict] = None  # {"start": "08:00", "end": "20:00"}


@dataclass
class EvaluationContext:
    agent_role: str
    tool_name: str
    tool_action_type: str   # read | reversible | irreversible
    parameters: Dict[str, Any]
    session_tokens_used: int
    session_irreversible_count: int
    current_hour: int = field(default_factory=lambda: datetime.now().hour)
    data_classification: str = "internal"  # public | internal | confidential | restricted
    requesting_user_role: str = "operator"


@dataclass
class PolicyDecision:
    rule_id: Optional[str]
    decision: Decision
    rationale: str
    approval_required_from: Optional[str]
    audit_level: str
    conditions_evaluated: List[str]


# ─────────────────────────────────────────────────────────────────────────────
# Policy evaluator
# ─────────────────────────────────────────────────────────────────────────────

class PolicyEngine:

    def __init__(self, policy: AgentPolicy):
        self.policy = policy

    def evaluate(self, ctx: EvaluationContext) -> PolicyDecision:
        """Evaluate an agent action against the policy. First-match wins."""

        conditions_log = []

        # Budget checks (always apply, regardless of rules)
        if ctx.session_tokens_used >= self.policy.max_tokens_per_session:
            return PolicyDecision(
                rule_id="BUDGET-TOKEN",
                decision=Decision.DENY,
                rationale=f"Token budget exhausted: {ctx.session_tokens_used:,} >= {self.policy.max_tokens_per_session:,}",
                approval_required_from=None,
                audit_level="elevated",
                conditions_evaluated=["token_budget"],
            )

        if (ctx.tool_action_type == "irreversible" and
                ctx.session_irreversible_count >= self.policy.max_irreversible_actions_per_session):
            return PolicyDecision(
                rule_id="BUDGET-IRREVERSIBLE",
                decision=Decision.DENY_AUDIT,
                rationale=f"Max irreversible actions per session reached: {ctx.session_irreversible_count}",
                approval_required_from=None,
                audit_level="critical",
                conditions_evaluated=["irreversible_budget"],
            )

        # Time window check
        if self.policy.allowed_hours:
            start_h = int(self.policy.allowed_hours.get("start", "00:00").split(":")[0])
            end_h = int(self.policy.allowed_hours.get("end", "23:00").split(":")[0])
            if not (start_h <= ctx.current_hour < end_h):
                return PolicyDecision(
                    rule_id="TIME-WINDOW",
                    decision=Decision.DENY,
                    rationale=f"Action outside allowed hours ({start_h}:00–{end_h}:00). Current hour: {ctx.current_hour}",
                    approval_required_from=None,
                    audit_level="standard",
                    conditions_evaluated=["time_window"],
                )

        # Evaluate rules (first match wins)
        for rule in self.policy.rules:
            if not self._matches_tool(rule.tool_pattern, ctx.tool_name):
                continue

            match, cond_log = self._evaluate_conditions(rule.conditions, ctx)
            conditions_log.extend(cond_log)

            if match:
                return PolicyDecision(
                    rule_id=rule.rule_id,
                    decision=rule.decision,
                    rationale=rule.rationale or rule.description,
                    approval_required_from=rule.approval_required_from,
                    audit_level=rule.audit_level,
                    conditions_evaluated=conditions_log,
                )

        # Default
        return PolicyDecision(
            rule_id="DEFAULT",
            decision=self.policy.default_decision,
            rationale=f"No matching rule found. Applying default: {self.policy.default_decision.value}",
            approval_required_from=None,
            audit_level="standard",
            conditions_evaluated=conditions_log,
        )

    def _matches_tool(self, pattern: str, tool_name: str) -> bool:
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            return tool_name.startswith(pattern[:-1])
        return pattern == tool_name

    def _evaluate_conditions(self, conditions: List[Dict],
                              ctx: EvaluationContext) -> Tuple[bool, List[str]]:
        from typing import Tuple
        logs = []
        for cond in conditions:
            cond_type = cond.get("type")

            if cond_type == "action_type":
                expected = cond.get("value")
                match = ctx.tool_action_type == expected
                logs.append(f"action_type={ctx.tool_action_type} == {expected}: {match}")
                if not match:
                    return False, logs

            elif cond_type == "data_classification":
                allowed_classes = cond.get("allowed", [])
                match = ctx.data_classification in allowed_classes
                logs.append(f"data_class={ctx.data_classification} in {allowed_classes}: {match}")
                if not match:
                    return False, logs

            elif cond_type == "user_role":
                allowed_roles = cond.get("allowed", [])
                match = ctx.requesting_user_role in allowed_roles
                logs.append(f"user_role={ctx.requesting_user_role} in {allowed_roles}: {match}")
                if not match:
                    return False, logs

            elif cond_type == "parameter_check":
                param = cond.get("parameter")
                forbidden_values = cond.get("forbidden_values", [])
                param_val = str(ctx.parameters.get(param, ""))
                is_forbidden = any(fv in param_val for fv in forbidden_values)
                logs.append(f"param {param} forbidden_check: {'FORBIDDEN' if is_forbidden else 'OK'}")
                if is_forbidden:
                    return False, logs

        return True, logs


# ─────────────────────────────────────────────────────────────────────────────
# Built-in policy templates
# ─────────────────────────────────────────────────────────────────────────────

def get_hr_agent_policy() -> AgentPolicy:
    """Policy for an HR recruitment assistant agent (Annex III §4 high-risk context)."""
    return AgentPolicy(
        policy_id="HR-AGENT-POL-001",
        agent_role="hr_recruitment_assistant",
        description="Policy for LLM-based HR recruitment assistant. Annex III §4 high-risk.",
        version="1.2",
        default_decision=Decision.DENY,
        max_tokens_per_session=30_000,
        max_irreversible_actions_per_session=2,
        allowed_hours={"start": "08", "end": "19"},
        rules=[
            PolicyRule(
                rule_id="HR-001",
                description="Allow read-only tools without restriction",
                tool_pattern="*",
                conditions=[{"type": "action_type", "value": "read"}],
                decision=Decision.ALLOW,
                audit_level="standard",
                rationale="Read-only operations have zero blast radius and are always permitted.",
            ),
            PolicyRule(
                rule_id="HR-002",
                description="Draft communications require approval for external recipients",
                tool_pattern="draft_*",
                conditions=[
                    {"type": "action_type", "value": "reversible"},
                    {"type": "parameter_check", "parameter": "to",
                     "forbidden_values": ["@external.com", "@candidate"]},
                ],
                decision=Decision.DENY,
                audit_level="elevated",
                rationale="Drafts targeting external recipients must be reviewed by a human before creation.",
            ),
            PolicyRule(
                rule_id="HR-003",
                description="Internal drafts are allowed",
                tool_pattern="draft_*",
                conditions=[{"type": "action_type", "value": "reversible"}],
                decision=Decision.ALLOW,
                audit_level="standard",
                rationale="Internal drafts are reversible and allowed.",
            ),
            PolicyRule(
                rule_id="HR-004",
                description="All irreversible actions require CTO approval",
                tool_pattern="*",
                conditions=[{"type": "action_type", "value": "irreversible"}],
                decision=Decision.ALLOW_WITH_APPROVAL,
                approval_required_from="hr_manager",
                audit_level="critical",
                rationale="EU AI Act Art. 14 — irreversible actions on candidates require human oversight.",
            ),
        ],
    )


def get_finops_agent_policy() -> AgentPolicy:
    """Policy for a FinOps cloud cost optimisation agent."""
    return AgentPolicy(
        policy_id="FINOPS-AGENT-POL-001",
        agent_role="finops_optimizer",
        description="Policy for cloud cost optimisation agent. DORA-aware.",
        version="1.0",
        default_decision=Decision.DENY,
        max_tokens_per_session=50_000,
        max_irreversible_actions_per_session=1,
        rules=[
            PolicyRule(
                rule_id="FO-001",
                description="All read operations allowed",
                tool_pattern="*",
                conditions=[{"type": "action_type", "value": "read"}],
                decision=Decision.ALLOW,
                audit_level="standard",
                rationale="Read operations allowed for cost analysis.",
            ),
            PolicyRule(
                rule_id="FO-002",
                description="Infrastructure changes require CTO + FinOps approval",
                tool_pattern="*",
                conditions=[{"type": "action_type", "value": "irreversible"}],
                decision=Decision.ALLOW_WITH_APPROVAL,
                approval_required_from="cto,finops_lead",
                audit_level="critical",
                rationale="DORA operational resilience — infrastructure changes require dual approval.",
            ),
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────────────────────────────────────

def run_demo():
    print("\n" + "═" * 65)
    print("  Agent Policy Engine — DEMO MODE")
    print("  Evaluating sample actions against HR agent policy")
    print("═" * 65)

    policy = get_hr_agent_policy()
    engine = PolicyEngine(policy)

    test_cases = [
        {
            "label": "Web search for candidate background",
            "ctx": EvaluationContext(
                agent_role="hr_recruitment_assistant",
                tool_name="web_search",
                tool_action_type="read",
                parameters={"query": "candidate name LinkedIn"},
                session_tokens_used=1_200,
                session_irreversible_count=0,
                data_classification="internal",
                requesting_user_role="recruiter",
            ),
        },
        {
            "label": "Draft rejection email to internal folder",
            "ctx": EvaluationContext(
                agent_role="hr_recruitment_assistant",
                tool_name="draft_email",
                tool_action_type="reversible",
                parameters={"to": "internal_hr_folder", "subject": "Candidate rejection draft"},
                session_tokens_used=5_000,
                session_irreversible_count=0,
                data_classification="internal",
                requesting_user_role="recruiter",
            ),
        },
        {
            "label": "Send rejection email directly to candidate (irreversible)",
            "ctx": EvaluationContext(
                agent_role="hr_recruitment_assistant",
                tool_name="send_email",
                tool_action_type="irreversible",
                parameters={"to": "candidate@external.com", "subject": "Application status"},
                session_tokens_used=8_000,
                session_irreversible_count=0,
                data_classification="internal",
                requesting_user_role="recruiter",
            ),
        },
        {
            "label": "Action after token budget exceeded",
            "ctx": EvaluationContext(
                agent_role="hr_recruitment_assistant",
                tool_name="web_search",
                tool_action_type="read",
                parameters={"query": "test"},
                session_tokens_used=31_000,   # over budget
                session_irreversible_count=0,
                data_classification="internal",
                requesting_user_role="recruiter",
            ),
        },
    ]

    for tc in test_cases:
        decision = engine.evaluate(tc["ctx"])
        icon = {"ALLOW": "✅", "ALLOW_WITH_APPROVAL": "⚠️ ",
                "DENY": "❌", "DENY_AUDIT": "🚨"}.get(decision.decision.value, "?")
        print(f"\n  [{icon} {decision.decision.value}] {tc['label']}")
        print(f"    Rule: {decision.rule_id}")
        print(f"    Rationale: {decision.rationale}")
        if decision.approval_required_from:
            print(f"    Approval required from: {decision.approval_required_from}")
        print(f"    Audit level: {decision.audit_level}")

    print(f"\n{'═'*65}")
    print("  Policy summary:")
    print(f"  Policy ID:  {policy.policy_id}")
    print(f"  Agent role: {policy.agent_role}")
    print(f"  Max tokens/session: {policy.max_tokens_per_session:,}")
    print(f"  Max irreversible/session: {policy.max_irreversible_actions_per_session}")
    print(f"  Allowed hours: {policy.allowed_hours}")
    print(f"  Rules: {len(policy.rules)}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Agent Policy Engine — ABAC/PBAC for AI agents")
    parser.add_argument("--demo", action="store_true", help="Run demo evaluation")
    parser.add_argument("--generate-template", action="store_true")
    parser.add_argument("--agent-type", choices=["hr", "finops"], default="hr")
    args = parser.parse_args()

    if args.demo:
        run_demo()
        return

    if args.generate_template:
        policy = get_hr_agent_policy() if args.agent_type == "hr" else get_finops_agent_policy()
        print(f"Policy: {policy.policy_id} — {policy.description}")
        print(f"Rules ({len(policy.rules)}):")
        for r in policy.rules:
            print(f"  [{r.rule_id}] {r.description} → {r.decision.value}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
