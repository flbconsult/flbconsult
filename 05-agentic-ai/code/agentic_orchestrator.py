#!/usr/bin/env python3
"""
Agentic Orchestrator — Module 05
==================================
Production-grade multi-agent reference architecture with:
  - Hierarchical orchestration (planner + specialist subagents)
  - Blast radius guardrails (max steps, token budget, irreversibility gate)
  - Human-in-the-loop approval for irreversible actions
  - Full trace logging (compatible with agent_audit_logger.py)

Patterns: ReAct (Yao et al. 2023), Plan-and-Execute hybrid

Usage:
    python agentic_orchestrator.py --demo
    python agentic_orchestrator.py --task "Research Q1 2026 cloud pricing for AWS, Azure, GCP"
    python agentic_orchestrator.py --demo --no-hitl  # skip human approval prompts

Production note: replace StubLLM with your preferred provider:
    from langchain_anthropic import ChatAnthropic
    from openai import OpenAI
"""

import argparse
import json
import random
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# Data models
# ─────────────────────────────────────────────────────────────────────────────

class ActionType(Enum):
    READ = "read"           # read-only, zero blast radius
    REVERSIBLE = "reversible"   # can be undone
    IRREVERSIBLE = "irreversible"  # cannot be undone — requires HITL approval


@dataclass
class Tool:
    name: str
    description: str
    action_type: ActionType
    parameters: Dict[str, str]
    handler: Callable


@dataclass
class ThoughtActionObservation:
    """Single ReAct step."""
    step: int
    thought: str
    action: str
    action_input: Dict[str, Any]
    observation: str
    approved_by_hitl: Optional[bool] = None
    tokens_used: int = 0


@dataclass
class AgentTrace:
    agent_id: str
    agent_role: str
    task: str
    steps: List[ThoughtActionObservation] = field(default_factory=list)
    final_output: str = ""
    status: str = "pending"  # pending | completed | halted | error
    total_tokens: int = 0
    total_steps: int = 0


@dataclass
class OrchestratorResult:
    task_id: str
    task: str
    status: str
    final_answer: str
    agent_traces: List[AgentTrace]
    total_tokens: int
    total_steps: int
    hitl_approvals: int
    hitl_rejections: int


# ─────────────────────────────────────────────────────────────────────────────
# Guardrails
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Guardrails:
    max_steps: int = 10
    max_tokens: int = 50_000
    max_tool_calls_per_tool: int = 5
    require_hitl_for_irreversible: bool = True
    hitl_timeout_seconds: int = 30

    def check(self, trace: AgentTrace) -> Tuple[bool, str]:
        if trace.total_steps >= self.max_steps:
            return False, f"Max steps reached ({self.max_steps})"
        if trace.total_tokens >= self.max_tokens:
            return False, f"Token budget exceeded ({self.max_tokens})"
        return True, "OK"


# ─────────────────────────────────────────────────────────────────────────────
# Stub LLM (replace with real provider in production)
# ─────────────────────────────────────────────────────────────────────────────

class StubLLM:
    """Deterministic stub for demonstration. Replace with real LLM client."""

    def __init__(self, role: str):
        self.role = role
        self._step = 0

    def generate(self, context: str, available_tools: List[str]) -> Dict:
        """Returns a ReAct step: thought + action + action_input."""
        self._step += 1
        random.seed(hash(context[:50]) + self._step)

        # Simulate agent reasoning based on step
        if self._step == 1:
            tool = available_tools[0] if available_tools else "finish"
            thought = f"I need to start by gathering information. I'll use {tool} first."
            return {"thought": thought, "action": tool,
                    "action_input": {"query": context[:60]}, "tokens": 450}

        elif self._step == 2:
            tool = available_tools[1] if len(available_tools) > 1 else available_tools[0]
            thought = "I have initial information. Let me enrich it with additional data."
            return {"thought": thought, "action": tool,
                    "action_input": {"query": "additional context"}, "tokens": 380}

        elif self._step <= 4:
            thought = f"Step {self._step}: Processing gathered information and synthesising."
            return {"thought": thought, "action": "analyze_data",
                    "action_input": {"data": "gathered"}, "tokens": 290}

        else:
            thought = "I have sufficient information to provide a comprehensive answer."
            return {"thought": thought, "action": "finish",
                    "action_input": {"output": f"[Synthesised answer for: {context[:80]}...]"},
                    "tokens": 520}

    def plan(self, task: str, subagent_roles: List[str]) -> List[Dict]:
        """Plan-and-Execute: decompose task into subtasks for subagents."""
        return [
            {"subtask": f"Research phase: gather relevant data for '{task[:50]}'",
             "agent": subagent_roles[0] if subagent_roles else "researcher",
             "depends_on": []},
            {"subtask": f"Analysis phase: analyse and structure findings",
             "agent": subagent_roles[1] if len(subagent_roles) > 1 else "analyst",
             "depends_on": ["Research phase"]},
            {"subtask": "Synthesis phase: produce final output",
             "agent": subagent_roles[-1] if subagent_roles else "synthesiser",
             "depends_on": ["Analysis phase"]},
        ]


# ─────────────────────────────────────────────────────────────────────────────
# Tool registry (demo tools)
# ─────────────────────────────────────────────────────────────────────────────

def _web_search(query: str, **kwargs) -> str:
    """Stub: simulate web search results."""
    return f"[Web search results for '{query}': Found 5 relevant sources. Top result: ...]"

def _database_query(query: str, **kwargs) -> str:
    """Stub: simulate read-only database query."""
    return f"[DB query results for '{query}': 23 records matching criteria returned.]"

def _analyze_data(data: str, **kwargs) -> str:
    """Stub: simulate data analysis."""
    return f"[Analysis complete: 3 key patterns identified in data. Confidence: 87%.]"

def _draft_email(to: str, subject: str, body: str, **kwargs) -> str:
    """Stub: create email draft (reversible)."""
    return f"[Draft created: To={to}, Subject='{subject}'. Saved to drafts folder. Not sent.]"

def _send_email(to: str, subject: str, body: str, **kwargs) -> str:
    """Stub: send email (IRREVERSIBLE — requires HITL)."""
    return f"[Email SENT to {to}: Subject='{subject}'. This action cannot be undone.]"

def _update_record(record_id: str, field: str, value: str, **kwargs) -> str:
    """Stub: update database record (IRREVERSIBLE — requires HITL)."""
    return f"[Record {record_id} updated: {field} = {value}. Previous value archived.]"

def _finish(output: str, **kwargs) -> str:
    return output


DEMO_TOOLS = [
    Tool("web_search", "Search the web for information", ActionType.READ,
         {"query": "string"}, _web_search),
    Tool("database_query", "Query internal databases (read-only)", ActionType.READ,
         {"query": "string"}, _database_query),
    Tool("analyze_data", "Analyse and structure data", ActionType.READ,
         {"data": "string"}, _analyze_data),
    Tool("draft_email", "Create an email draft (NOT sent)", ActionType.REVERSIBLE,
         {"to": "string", "subject": "string", "body": "string"}, _draft_email),
    Tool("send_email", "Send an email (IRREVERSIBLE)", ActionType.IRREVERSIBLE,
         {"to": "string", "subject": "string", "body": "string"}, _send_email),
    Tool("update_record", "Update a database record (IRREVERSIBLE)", ActionType.IRREVERSIBLE,
         {"record_id": "string", "field": "string", "value": "string"}, _update_record),
    Tool("finish", "Return final answer", ActionType.READ,
         {"output": "string"}, _finish),
]


# ─────────────────────────────────────────────────────────────────────────────
# Subagent
# ─────────────────────────────────────────────────────────────────────────────

class Subagent:

    def __init__(self, role: str, tools: List[Tool], guardrails: Guardrails,
                 require_hitl: bool = True):
        self.role = role
        self.agent_id = f"{role}-{uuid.uuid4().hex[:6]}"
        self.tools = {t.name: t for t in tools}
        self.guardrails = guardrails
        self.require_hitl = require_hitl
        self.llm = StubLLM(role)

    def run(self, task: str) -> AgentTrace:
        trace = AgentTrace(
            agent_id=self.agent_id,
            agent_role=self.role,
            task=task,
            status="in_progress"
        )

        context = f"Role: {self.role}\nTask: {task}\n"
        tool_names = list(self.tools.keys())

        while True:
            ok, reason = self.guardrails.check(trace)
            if not ok:
                trace.status = "halted"
                trace.final_output = f"[HALTED: {reason}]"
                print(f"    ⚠️  Agent {self.role} halted: {reason}")
                break

            step_data = self.llm.generate(context, tool_names)
            action_name = step_data.get("action", "finish")
            action_input = step_data.get("action_input", {})

            # Execute or gate action
            tool = self.tools.get(action_name)
            approved = None
            observation = ""

            if tool is None:
                observation = f"[Error: tool '{action_name}' not found]"
            elif (tool.action_type == ActionType.IRREVERSIBLE and
                  self.require_hitl):
                approved = self._request_hitl_approval(action_name, action_input)
                if approved:
                    observation = tool.handler(**action_input)
                else:
                    observation = f"[Action '{action_name}' REJECTED by human reviewer. Task halted.]"
                    tao = ThoughtActionObservation(
                        step=trace.total_steps + 1,
                        thought=step_data["thought"],
                        action=action_name,
                        action_input=action_input,
                        observation=observation,
                        approved_by_hitl=False,
                        tokens_used=step_data.get("tokens", 0),
                    )
                    trace.steps.append(tao)
                    trace.total_steps += 1
                    trace.total_tokens += step_data.get("tokens", 0)
                    trace.status = "halted"
                    trace.final_output = "[Task halted after HITL rejection]"
                    break
            else:
                observation = tool.handler(**action_input)

            tao = ThoughtActionObservation(
                step=trace.total_steps + 1,
                thought=step_data["thought"],
                action=action_name,
                action_input=action_input,
                observation=observation,
                approved_by_hitl=approved,
                tokens_used=step_data.get("tokens", 0),
            )
            trace.steps.append(tao)
            trace.total_steps += 1
            trace.total_tokens += step_data.get("tokens", 0)

            if action_name == "finish":
                trace.status = "completed"
                trace.final_output = action_input.get("output", observation)
                break

            context += f"\nObservation {trace.total_steps}: {observation}"

        return trace

    def _request_hitl_approval(self, action: str, inputs: Dict,
                                auto_approve: bool = False) -> bool:
        if auto_approve:
            print(f"    [HITL] Auto-approving irreversible action: {action}")
            return True

        print(f"\n    {'─'*50}")
        print(f"    ⚠️  HUMAN APPROVAL REQUIRED (irreversible action)")
        print(f"    Agent: {self.role}")
        print(f"    Action: {action}")
        print(f"    Parameters: {json.dumps(inputs, indent=6)}")
        print(f"    This action CANNOT be undone.")
        ans = input("    Approve? [y/N]: ").strip().lower()
        print(f"    {'─'*50}")
        return ans == "y"


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator
# ─────────────────────────────────────────────────────────────────────────────

class Orchestrator:

    def __init__(self, guardrails: Optional[Guardrails] = None,
                 require_hitl: bool = True):
        self.guardrails = guardrails or Guardrails()
        self.require_hitl = require_hitl
        self.planner_llm = StubLLM("planner")

        # Define specialist subagents
        read_tools = [t for t in DEMO_TOOLS if t.action_type == ActionType.READ]
        all_tools = DEMO_TOOLS

        self.subagents = {
            "researcher": Subagent("researcher", read_tools, self.guardrails, require_hitl),
            "analyst": Subagent("analyst", read_tools, self.guardrails, require_hitl),
            "writer": Subagent("writer", all_tools, self.guardrails, require_hitl),
        }

    def run(self, task: str) -> OrchestratorResult:
        task_id = uuid.uuid4().hex[:8]
        print(f"\n  {'═'*60}")
        print(f"  ORCHESTRATOR — Task {task_id}")
        print(f"  {task}")
        print(f"  Guardrails: max_steps={self.guardrails.max_steps}, "
              f"max_tokens={self.guardrails.max_tokens:,}")
        print(f"  {'═'*60}")

        # Plan phase
        print("\n  ── Phase 1: Planning ────────────────────────────────────────")
        subtasks = self.planner_llm.plan(task, list(self.subagents.keys()))
        for i, st in enumerate(subtasks, 1):
            print(f"  {i}. [{st['agent']}] {st['subtask']}")

        # Execute phase
        print("\n  ── Phase 2: Execution ───────────────────────────────────────")
        all_traces = []
        hitl_approvals = 0
        hitl_rejections = 0
        total_tokens = 0
        total_steps = 0
        last_output = ""

        for st in subtasks:
            agent_name = st["agent"]
            agent = self.subagents.get(agent_name)
            if not agent:
                continue

            print(f"\n  → Running {agent_name}: {st['subtask'][:60]}...")
            enriched_task = f"{st['subtask']}\nContext from previous steps: {last_output[:200]}"
            trace = agent.run(enriched_task)
            all_traces.append(trace)

            for step in trace.steps:
                print(f"    Step {step.step}: [{step.action}] {step.thought[:60]}...")
                if step.approved_by_hitl is True:
                    hitl_approvals += 1
                elif step.approved_by_hitl is False:
                    hitl_rejections += 1

            total_tokens += trace.total_tokens
            total_steps += trace.total_steps
            last_output = trace.final_output
            print(f"  ✓ {agent_name} completed: {trace.final_output[:80]}...")

            if trace.status == "halted" and hitl_rejections > 0:
                print("\n  ✗ Orchestration halted due to HITL rejection.")
                break

        # Synthesis
        final_answer = f"[Orchestrated result for: {task[:60]}]\n\n{last_output}"

        result = OrchestratorResult(
            task_id=task_id,
            task=task,
            status="completed" if hitl_rejections == 0 else "halted",
            final_answer=final_answer,
            agent_traces=all_traces,
            total_tokens=total_tokens,
            total_steps=total_steps,
            hitl_approvals=hitl_approvals,
            hitl_rejections=hitl_rejections,
        )

        print(f"\n  ── Result ────────────────────────────────────────────────────")
        print(f"  Status:  {result.status.upper()}")
        print(f"  Tokens:  {result.total_tokens:,} / {self.guardrails.max_tokens:,} budget")
        print(f"  Steps:   {result.total_steps}")
        print(f"  HITL:    {result.hitl_approvals} approved, {result.hitl_rejections} rejected")
        print(f"  {'═'*60}")
        return result


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Multi-Agent Orchestrator with Guardrails",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agentic_orchestrator.py --demo
  python agentic_orchestrator.py --demo --no-hitl
  python agentic_orchestrator.py --task "Analyse Q1 cloud costs and draft executive summary"
        """
    )
    parser.add_argument("--demo", action="store_true",
                        help="Run demo task with HITL prompts")
    parser.add_argument("--no-hitl", action="store_true",
                        help="Skip HITL prompts (auto-approve)")
    parser.add_argument("--task", help="Custom task to execute")
    parser.add_argument("--max-steps", type=int, default=10)
    parser.add_argument("--max-tokens", type=int, default=50000)
    args = parser.parse_args()

    guardrails = Guardrails(
        max_steps=args.max_steps,
        max_tokens=args.max_tokens,
        require_hitl_for_irreversible=not args.no_hitl,
    )

    require_hitl = not args.no_hitl

    if args.demo or args.task:
        task = args.task or (
            "Research the three main EU AI Act compliance gaps for HR AI systems "
            "in 2026, produce a summary report, and draft an email to the legal team."
        )
        orchestrator = Orchestrator(guardrails=guardrails, require_hitl=require_hitl)
        orchestrator.run(task)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
