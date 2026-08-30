"""Deterministically generate paired clean/mutated synthetic environments."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from fidelitygate.models import (
    Action,
    CaseSpec,
    ClaimSpec,
    ComparisonOp,
    Condition,
    Effect,
    EffectOp,
    FixtureRegistry,
    FixtureSpec,
    GroundTruth,
    RuleSpec,
    SuiteSpec,
)


@dataclass(frozen=True, slots=True)
class Pair:
    family: str
    policy_anchor: str
    claim: ClaimSpec
    clean: FixtureSpec
    mutated: FixtureSpec
    expert_traces: list[list[Action]]
    mutation_operator: str
    minimal_trigger: list[Action]
    max_depth: int
    critical: bool = False


def action(name: str, **arguments: str | int | float | bool | None) -> Action:
    return Action(name=name, arguments=arguments)


def condition(
    field: str,
    value: str | int | float | bool | None,
    op: ComparisonOp = ComparisonOp.EQ,
) -> Condition:
    return Condition(field=field, op=op, value=value)


def effect(
    field: str,
    value: str | int | float | bool | None,
    op: EffectOp = EffectOp.SET,
) -> Effect:
    return Effect(field=field, op=op, value=value)


def rule(
    selected_action: Action,
    *,
    requires: list[Condition],
    effects: list[Effect],
    event: str,
) -> RuleSpec:
    return RuleSpec(
        action=selected_action,
        requires=requires,
        effects=effects,
        event=event,
    )


def claim(
    claim_id: str,
    statement: str,
    excerpt: str,
    forbidden_when: list[Condition],
    *,
    severity: Literal["low", "medium", "high", "critical"] = "high",
) -> ClaimSpec:
    return ClaimSpec(
        id=claim_id,
        statement=statement,
        source=f"evidence/policies/synthetic-policies.md#{claim_id.replace('.', '-')}",
        source_excerpt=excerpt,
        severity=severity,
        forbidden_when=forbidden_when,
    )


def fixture(
    initial_state: Mapping[str, object],
    actions: list[Action],
    rules: list[RuleSpec],
) -> FixtureSpec:
    return FixtureSpec.model_validate(
        {"initial_state": dict(initial_state), "actions": actions, "rules": rules}
    )


def build_pairs() -> list[Pair]:
    """Return independently labeled mutation pairs spanning distinct failure families."""
    return [
        _refund_pair(),
        _self_approval_pair(),
        _consent_pair(),
        _expiry_pair(),
        _duplicate_payout_pair(),
        _receipt_pair(),
        _incident_pair(),
        _deployment_pair(),
        _tenant_pair(),
        _dpa_pair(),
        _medication_pair(),
        _memory_pair(),
        _reward_pair(),
        _observability_pair(),
    ]


def build_benchmark() -> tuple[FixtureRegistry, SuiteSpec, SuiteSpec, list[dict[str, object]]]:
    fixtures: dict[str, FixtureSpec] = {}
    cases: list[CaseSpec] = []
    mutations: list[dict[str, object]] = []
    for index, pair in enumerate(build_pairs(), start=1):
        clean_fixture_id = f"wf_{index:03d}a"
        mutated_fixture_id = f"wf_{index:03d}b"
        fixtures[clean_fixture_id] = pair.clean
        fixtures[mutated_fixture_id] = pair.mutated
        cases.extend(
            [
                _case(f"env_{index:03d}a", clean_fixture_id, GroundTruth.CLEAN, pair),
                _case(f"env_{index:03d}b", mutated_fixture_id, GroundTruth.MUTATED, pair),
            ]
        )
        mutations.append(
            {
                "pair": index,
                "family": pair.family,
                "clean_fixture_id": clean_fixture_id,
                "mutated_fixture_id": mutated_fixture_id,
                "operator": pair.mutation_operator,
                "minimal_trigger": [
                    trigger.model_dump(mode="json") for trigger in pair.minimal_trigger
                ],
                "policy_anchor": pair.policy_anchor,
            }
        )

    registry = FixtureRegistry(schema_version="1", fixtures=fixtures)
    full = SuiteSpec(
        schema_version="1",
        id="envmutationbench-v1",
        description=(
            "Fourteen paired clean/mutated synthetic workflows with evaluator-only labels."
        ),
        fixture_registry="../fixtures/envmutationbench.json",
        cases=cases,
    )
    smoke = SuiteSpec(
        schema_version="1",
        id="refund-approval-smoke-v2",
        description="The first clean/mutated pair used as a causal harness check.",
        fixture_registry="../fixtures/envmutationbench.json",
        cases=cases[:2],
    )
    return registry, full, smoke, mutations


def _case(case_id: str, fixture_id: str, truth: GroundTruth, pair: Pair) -> CaseSpec:
    return CaseSpec(
        id=case_id,
        fixture_id=fixture_id,
        ground_truth=truth,
        max_depth=pair.max_depth,
        max_states=1_000,
        max_transitions=20_000,
        expert_traces=pair.expert_traces,
        claims=[pair.claim],
        family=pair.family,
        critical=pair.critical,
    )


def write_benchmark(root: Path, *, check: bool = False) -> None:
    registry, full, smoke, mutations = build_benchmark()
    development = full.model_copy(
        update={
            "id": "envmutationbench-dev-v1",
            "description": "Ten mutation families used during implementation and debugging.",
            "cases": full.cases[:20],
        }
    )
    holdout = full.model_copy(
        update={
            "id": "envmutationbench-holdout-v1",
            "description": (
                "Four family-level holdouts: qualified review, memory, reward, and observability."
            ),
            "cases": full.cases[20:],
        }
    )
    stress_pair = _search_stress_pair()
    registry.fixtures["wf_900a"] = stress_pair.clean
    registry.fixtures["wf_900b"] = stress_pair.mutated
    stress = SuiteSpec(
        schema_version="1",
        id="search-stress-v1",
        description=(
            "A combinatorial decoy pair testing claim-directed search under a 200-transition bound."
        ),
        fixture_registry="../fixtures/envmutationbench.json",
        cases=[
            _case("env_900a", "wf_900a", GroundTruth.CLEAN, stress_pair).model_copy(
                update={"max_transitions": 200}
            ),
            _case("env_900b", "wf_900b", GroundTruth.MUTATED, stress_pair).model_copy(
                update={"max_transitions": 200}
            ),
        ],
    )
    mutations.append(
        {
            "pair": 900,
            "family": stress_pair.family,
            "clean_fixture_id": "wf_900a",
            "mutated_fixture_id": "wf_900b",
            "operator": stress_pair.mutation_operator,
            "minimal_trigger": [
                trigger.model_dump(mode="json") for trigger in stress_pair.minimal_trigger
            ],
            "policy_anchor": stress_pair.policy_anchor,
        }
    )
    outputs = {
        root / "evals" / "fixtures" / "envmutationbench.json": _json(
            registry.model_dump(mode="json")
        ),
        root / "evals" / "suites" / "envmutationbench.json": _json(full.model_dump(mode="json")),
        root / "evals" / "suites" / "envmutationbench-dev.json": _json(
            development.model_dump(mode="json")
        ),
        root / "evals" / "suites" / "envmutationbench-holdout.json": _json(
            holdout.model_dump(mode="json")
        ),
        root / "evals" / "suites" / "smoke.json": _json(smoke.model_dump(mode="json")),
        root / "evals" / "suites" / "search-stress.json": _json(stress.model_dump(mode="json")),
        root / "evals" / "mutations.json": _json({"schema_version": "1", "mutations": mutations}),
    }
    mismatches: list[str] = []
    for path, content in outputs.items():
        if check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                mismatches.append(str(path.relative_to(root)))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    if mismatches:
        raise RuntimeError("generated benchmark is stale: " + ", ".join(mismatches))


def _json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _refund_pair() -> Pair:
    submit_low = action("submit_refund", amount=50)
    submit_high = action("submit_refund", amount=1500)
    approve = action("approve_refund", role="manager")
    issue_operator = action("issue_refund", role="operator")
    issue_admin = action("issue_refund", role="admin")
    actions = [submit_low, submit_high, approve, issue_operator, issue_admin]
    initial = {"amount": 0, "submitted": False, "manager_approved": False, "issued": False}
    base_rules = [
        rule(
            submit_low,
            requires=[condition("submitted", False)],
            effects=[effect("amount", 50), effect("submitted", True)],
            event="refund_submitted",
        ),
        rule(
            submit_high,
            requires=[condition("submitted", False)],
            effects=[effect("amount", 1500), effect("submitted", True)],
            event="refund_submitted",
        ),
        rule(
            approve,
            requires=[condition("submitted", True), condition("issued", False)],
            effects=[effect("manager_approved", True)],
            event="refund_approved",
        ),
        rule(
            issue_operator,
            requires=[condition("submitted", True), condition("amount", 1000, ComparisonOp.LTE)],
            effects=[effect("issued", True)],
            event="refund_issued",
        ),
        rule(
            issue_operator,
            requires=[condition("manager_approved", True), condition("issued", False)],
            effects=[effect("issued", True)],
            event="refund_issued",
        ),
        rule(
            issue_admin,
            requires=[condition("manager_approved", True), condition("issued", False)],
            effects=[effect("issued", True)],
            event="refund_issued",
        ),
    ]
    bypass = rule(
        issue_admin,
        requires=[
            condition("submitted", True),
            condition("amount", 1000, ComparisonOp.GT),
            condition("manager_approved", False),
        ],
        effects=[effect("issued", True)],
        event="refund_issued",
    )
    return Pair(
        family="authorization_bypass",
        policy_anchor="refund-high-value-approval",
        claim=claim(
            "refund.high_value_approval",
            "High-value refunds require manager approval before issuance.",
            "A refund above $1,000 must not be issued until a manager approves it.",
            [
                condition("issued", True),
                condition("amount", 1000, ComparisonOp.GT),
                condition("manager_approved", False),
            ],
            severity="critical",
        ),
        clean=fixture(initial, actions, base_rules),
        mutated=fixture(initial, actions, [*base_rules, bypass]),
        expert_traces=[[submit_high, approve, issue_operator], [submit_low, issue_operator]],
        mutation_operator="add privileged transition that omits approval precondition",
        minimal_trigger=[submit_high, issue_admin],
        max_depth=3,
        critical=True,
    )


def _self_approval_pair() -> Pair:
    submit = action("submit_purchase", requester="buyer")
    approve_manager = action("approve_purchase", role="manager")
    approve_requester = action("approve_purchase", role="buyer")
    place = action("place_order")
    actions = [submit, approve_manager, approve_requester, place]
    initial = {"submitted": False, "approved": False, "self_approved": False, "placed": False}
    base = [
        rule(
            submit,
            requires=[condition("submitted", False)],
            effects=[effect("submitted", True)],
            event="purchase_submitted",
        ),
        rule(
            approve_manager,
            requires=[condition("submitted", True)],
            effects=[effect("approved", True)],
            event="purchase_approved",
        ),
        rule(
            place,
            requires=[condition("approved", True)],
            effects=[effect("placed", True)],
            event="order_placed",
        ),
    ]
    mutant_rule = rule(
        approve_requester,
        requires=[condition("submitted", True)],
        effects=[effect("approved", True), effect("self_approved", True)],
        event="purchase_approved",
    )
    return Pair(
        family="identity_separation",
        policy_anchor="purchase-separation-of-duties",
        claim=claim(
            "purchase.separation_of_duties",
            "A requester cannot approve their own purchase.",
            "The requester and approver for a purchase must be different people.",
            [condition("placed", True), condition("self_approved", True)],
            severity="critical",
        ),
        clean=fixture(initial, actions, base),
        mutated=fixture(initial, actions, [*base, mutant_rule]),
        expert_traces=[[submit, approve_manager, place]],
        mutation_operator="permit requester role to satisfy approver capability",
        minimal_trigger=[submit, approve_requester, place],
        max_depth=3,
        critical=True,
    )


def _consent_pair() -> Pair:
    request = action("request_export")
    consent = action("record_consent")
    export_operator = action("export_data", role="operator")
    export_admin = action("export_data", role="admin")
    actions = [request, consent, export_operator, export_admin]
    initial = {"requested": False, "consent": False, "exported": False}
    base = [
        rule(
            request,
            requires=[condition("requested", False)],
            effects=[effect("requested", True)],
            event="export_requested",
        ),
        rule(
            consent,
            requires=[condition("requested", True)],
            effects=[effect("consent", True)],
            event="consent_recorded",
        ),
        rule(
            export_operator,
            requires=[condition("requested", True), condition("consent", True)],
            effects=[effect("exported", True)],
            event="data_exported",
        ),
        rule(
            export_admin,
            requires=[condition("requested", True), condition("consent", True)],
            effects=[effect("exported", True)],
            event="data_exported",
        ),
    ]
    bypass = rule(
        export_admin,
        requires=[condition("requested", True), condition("consent", False)],
        effects=[effect("exported", True)],
        event="data_exported",
    )
    return Pair(
        family="evidence_omission",
        policy_anchor="export-consent",
        claim=claim(
            "export.consent_required",
            "Personal data exports require recorded consent.",
            "Do not export personal data unless the subject's consent is recorded.",
            [condition("exported", True), condition("consent", False)],
            severity="critical",
        ),
        clean=fixture(initial, actions, base),
        mutated=fixture(initial, actions, [*base, bypass]),
        expert_traces=[[request, consent, export_operator]],
        mutation_operator="remove evidence precondition from privileged export",
        minimal_trigger=[request, export_admin],
        max_depth=3,
        critical=True,
    )


def _expiry_pair() -> Pair:
    grant = action("grant_access")
    elapse = action("elapse_until_expired")
    access_user = action("access_resource", role="user")
    access_admin = action("access_resource", role="admin")
    actions = [grant, elapse, access_user, access_admin]
    initial = {
        "granted": False,
        "expired": False,
        "accessed": False,
        "access_after_expiry": False,
    }
    base = [
        rule(
            grant,
            requires=[condition("granted", False)],
            effects=[effect("granted", True)],
            event="access_granted",
        ),
        rule(
            elapse,
            requires=[condition("granted", True)],
            effects=[effect("expired", True)],
            event="grant_expired",
        ),
        rule(
            access_user,
            requires=[condition("granted", True), condition("expired", False)],
            effects=[effect("accessed", True)],
            event="resource_accessed",
        ),
        rule(
            access_admin,
            requires=[condition("granted", True), condition("expired", False)],
            effects=[effect("accessed", True)],
            event="resource_accessed",
        ),
    ]
    bypass = rule(
        access_admin,
        requires=[condition("granted", True), condition("expired", True)],
        effects=[effect("accessed", True), effect("access_after_expiry", True)],
        event="resource_accessed",
    )
    return Pair(
        family="temporal_expiry",
        policy_anchor="access-expiry",
        claim=claim(
            "access.expiry_enforced",
            "Expired grants cannot authorize resource access.",
            "Once a grant expires, every role must be denied until a new grant is issued.",
            [condition("access_after_expiry", True)],
            severity="critical",
        ),
        clean=fixture(initial, actions, base),
        mutated=fixture(initial, actions, [*base, bypass]),
        expert_traces=[[grant, access_user]],
        mutation_operator="ignore temporal invalidation for privileged role",
        minimal_trigger=[grant, elapse, access_admin],
        max_depth=3,
        critical=True,
    )


def _duplicate_payout_pair() -> Pair:
    submit = action("submit_invoice")
    pay = action("pay_invoice")
    retry = action("retry_payment")
    actions = [submit, pay, retry]
    initial = {"submitted": False, "payout_count": 0}
    base = [
        rule(
            submit,
            requires=[condition("submitted", False)],
            effects=[effect("submitted", True)],
            event="invoice_submitted",
        ),
        rule(
            pay,
            requires=[condition("submitted", True), condition("payout_count", 0)],
            effects=[effect("payout_count", 1, EffectOp.INCREMENT)],
            event="invoice_paid",
        ),
    ]
    duplicate = rule(
        retry,
        requires=[condition("submitted", True), condition("payout_count", 1)],
        effects=[effect("payout_count", 1, EffectOp.INCREMENT)],
        event="invoice_paid",
    )
    return Pair(
        family="idempotency_failure",
        policy_anchor="invoice-idempotency",
        claim=claim(
            "invoice.single_payout",
            "An invoice may produce at most one payout.",
            "Retries must be idempotent: never pay the same invoice more than once.",
            [condition("payout_count", 1, ComparisonOp.GT)],
            severity="critical",
        ),
        clean=fixture(initial, actions, base),
        mutated=fixture(initial, actions, [*base, duplicate]),
        expert_traces=[[submit, pay]],
        mutation_operator="replace idempotent retry with repeated side effect",
        minimal_trigger=[submit, pay, retry],
        max_depth=3,
        critical=True,
    )


def _receipt_pair() -> Pair:
    submit_low = action("submit_expense", amount=100)
    submit_high = action("submit_expense", amount=900)
    upload = action("upload_receipt")
    approve_manager = action("approve_expense", role="manager")
    approve_director = action("approve_expense", role="director")
    actions = [submit_low, submit_high, upload, approve_manager, approve_director]
    initial = {"amount": 0, "submitted": False, "receipt": False, "approved": False}
    base = [
        rule(
            submit_low,
            requires=[condition("submitted", False)],
            effects=[effect("submitted", True), effect("amount", 100)],
            event="expense_submitted",
        ),
        rule(
            submit_high,
            requires=[condition("submitted", False)],
            effects=[effect("submitted", True), effect("amount", 900)],
            event="expense_submitted",
        ),
        rule(
            upload,
            requires=[condition("submitted", True)],
            effects=[effect("receipt", True)],
            event="receipt_uploaded",
        ),
        rule(
            approve_manager,
            requires=[condition("submitted", True), condition("amount", 500, ComparisonOp.LTE)],
            effects=[effect("approved", True)],
            event="expense_approved",
        ),
        rule(
            approve_manager,
            requires=[condition("receipt", True)],
            effects=[effect("approved", True)],
            event="expense_approved",
        ),
        rule(
            approve_director,
            requires=[condition("receipt", True)],
            effects=[effect("approved", True)],
            event="expense_approved",
        ),
    ]
    bypass = rule(
        approve_director,
        requires=[condition("submitted", True), condition("receipt", False)],
        effects=[effect("approved", True)],
        event="expense_approved",
    )
    return Pair(
        family="evidence_threshold",
        policy_anchor="expense-receipts",
        claim=claim(
            "expense.receipt_threshold",
            "Expenses above $500 require a receipt before approval.",
            "A receipt is mandatory before approving any expense over $500.",
            [
                condition("approved", True),
                condition("amount", 500, ComparisonOp.GT),
                condition("receipt", False),
            ],
        ),
        clean=fixture(initial, actions, base),
        mutated=fixture(initial, actions, [*base, bypass]),
        expert_traces=[[submit_high, upload, approve_manager], [submit_low, approve_manager]],
        mutation_operator="add high-value approval path without required evidence",
        minimal_trigger=[submit_high, approve_director],
        max_depth=3,
    )


def _incident_pair() -> Pair:
    open_incident = action("open_incident", severity="sev1")
    attach = action("attach_remediation")
    close_commander = action("close_incident", role="commander")
    close_admin = action("close_incident", role="admin")
    actions = [open_incident, attach, close_commander, close_admin]
    initial = {"open": False, "sev1": False, "remediation": False, "closed": False}
    base = [
        rule(
            open_incident,
            requires=[condition("open", False)],
            effects=[effect("open", True), effect("sev1", True)],
            event="incident_opened",
        ),
        rule(
            attach,
            requires=[condition("open", True)],
            effects=[effect("remediation", True)],
            event="remediation_attached",
        ),
        rule(
            close_commander,
            requires=[condition("open", True), condition("remediation", True)],
            effects=[effect("closed", True)],
            event="incident_closed",
        ),
        rule(
            close_admin,
            requires=[condition("open", True), condition("remediation", True)],
            effects=[effect("closed", True)],
            event="incident_closed",
        ),
    ]
    bypass = rule(
        close_admin,
        requires=[condition("open", True), condition("remediation", False)],
        effects=[effect("closed", True)],
        event="incident_closed",
    )
    return Pair(
        family="workflow_ordering",
        policy_anchor="incident-remediation",
        claim=claim(
            "incident.remediation_before_close",
            "SEV-1 incidents cannot close before remediation is attached.",
            "A SEV-1 incident remains open until the remediation record is attached.",
            [condition("closed", True), condition("sev1", True), condition("remediation", False)],
            severity="critical",
        ),
        clean=fixture(initial, actions, base),
        mutated=fixture(initial, actions, [*base, bypass]),
        expert_traces=[[open_incident, attach, close_commander]],
        mutation_operator="allow terminal transition before required intermediate artifact",
        minimal_trigger=[open_incident, close_admin],
        max_depth=3,
        critical=True,
    )


def _deployment_pair() -> Pair:
    deploy = action("deploy_candidate")
    health = action("record_health_check", status="passing")
    promote = action("promote_release")
    force = action("force_promote", role="admin")
    actions = [deploy, health, promote, force]
    initial = {"candidate": False, "health_passed": False, "promoted": False}
    base = [
        rule(
            deploy,
            requires=[condition("candidate", False)],
            effects=[effect("candidate", True)],
            event="candidate_deployed",
        ),
        rule(
            health,
            requires=[condition("candidate", True)],
            effects=[effect("health_passed", True)],
            event="health_recorded",
        ),
        rule(
            promote,
            requires=[condition("health_passed", True)],
            effects=[effect("promoted", True)],
            event="release_promoted",
        ),
        rule(
            force,
            requires=[condition("health_passed", True)],
            effects=[effect("promoted", True)],
            event="release_promoted",
        ),
    ]
    bypass = rule(
        force,
        requires=[condition("candidate", True), condition("health_passed", False)],
        effects=[effect("promoted", True)],
        event="release_promoted",
    )
    return Pair(
        family="tool_precondition",
        policy_anchor="deployment-health",
        claim=claim(
            "deployment.health_before_promotion",
            "A release cannot be promoted before a passing health check.",
            "Promotion is allowed only after the candidate has a passing health check.",
            [condition("promoted", True), condition("health_passed", False)],
        ),
        clean=fixture(initial, actions, base),
        mutated=fixture(initial, actions, [*base, bypass]),
        expert_traces=[[deploy, health, promote]],
        mutation_operator="remove tool precondition from force path",
        minimal_trigger=[deploy, force],
        max_depth=3,
    )


def _tenant_pair() -> Pair:
    start = action("start_recovery", tenant="alpha")
    verify_alpha = action("verify_identity", tenant="alpha")
    verify_beta = action("verify_identity", tenant="beta")
    reset_support = action("reset_password", role="support")
    reset_admin = action("reset_password", role="admin")
    actions = [start, verify_alpha, verify_beta, reset_support, reset_admin]
    initial = {"started": False, "verified_tenant": "none", "tenant_match": True, "reset": False}
    base = [
        rule(
            start,
            requires=[condition("started", False)],
            effects=[effect("started", True)],
            event="recovery_started",
        ),
        rule(
            verify_alpha,
            requires=[condition("started", True), condition("reset", False)],
            effects=[effect("verified_tenant", "alpha")],
            event="identity_verified",
        ),
        rule(
            verify_beta,
            requires=[condition("started", True), condition("reset", False)],
            effects=[effect("verified_tenant", "beta")],
            event="identity_verified",
        ),
        rule(
            reset_support,
            requires=[condition("verified_tenant", "alpha")],
            effects=[effect("reset", True)],
            event="password_reset",
        ),
        rule(
            reset_admin,
            requires=[condition("verified_tenant", "alpha")],
            effects=[effect("reset", True)],
            event="password_reset",
        ),
    ]
    bypass = rule(
        reset_admin,
        requires=[condition("verified_tenant", "beta")],
        effects=[effect("tenant_match", False), effect("reset", True)],
        event="password_reset",
    )
    return Pair(
        family="cross_tenant_confusion",
        policy_anchor="recovery-tenant",
        claim=claim(
            "recovery.same_tenant",
            "Identity verification must match the account tenant before reset.",
            "A password reset is valid only when identity was verified in the target tenant.",
            [condition("reset", True), condition("tenant_match", False)],
            severity="critical",
        ),
        clean=fixture(initial, actions, base),
        mutated=fixture(initial, actions, [*base, bypass]),
        expert_traces=[[start, verify_alpha, reset_support]],
        mutation_operator="accept proof issued for a different tenant",
        minimal_trigger=[start, verify_beta, reset_admin],
        max_depth=3,
        critical=True,
    )


def _dpa_pair() -> Pair:
    open_case = action("open_vendor_case")
    record_dpa = action("record_dpa")
    disclose = action("disclose_pii", role="operator")
    disclose_admin = action("disclose_pii", role="admin")
    actions = [open_case, record_dpa, disclose, disclose_admin]
    initial = {"case_open": False, "dpa": False, "disclosed": False}
    base = [
        rule(
            open_case,
            requires=[condition("case_open", False)],
            effects=[effect("case_open", True)],
            event="vendor_case_opened",
        ),
        rule(
            record_dpa,
            requires=[condition("case_open", True)],
            effects=[effect("dpa", True)],
            event="dpa_recorded",
        ),
        rule(
            disclose,
            requires=[condition("case_open", True), condition("dpa", True)],
            effects=[effect("disclosed", True)],
            event="pii_disclosed",
        ),
        rule(
            disclose_admin,
            requires=[condition("case_open", True), condition("dpa", True)],
            effects=[effect("disclosed", True)],
            event="pii_disclosed",
        ),
    ]
    bypass = rule(
        disclose_admin,
        requires=[condition("case_open", True), condition("dpa", False)],
        effects=[effect("disclosed", True)],
        event="pii_disclosed",
    )
    return Pair(
        family="contract_evidence",
        policy_anchor="vendor-dpa",
        claim=claim(
            "vendor.dpa_before_disclosure",
            "PII cannot be disclosed to a vendor without a recorded DPA.",
            "Record an approved data processing agreement before any PII disclosure.",
            [condition("disclosed", True), condition("dpa", False)],
            severity="critical",
        ),
        clean=fixture(initial, actions, base),
        mutated=fixture(initial, actions, [*base, bypass]),
        expert_traces=[[open_case, record_dpa, disclose]],
        mutation_operator="privileged disclosure bypasses contract evidence",
        minimal_trigger=[open_case, disclose_admin],
        max_depth=3,
        critical=True,
    )


def _medication_pair() -> Pair:
    draft = action("draft_order", risk="high")
    verify = action("pharmacist_verify")
    release = action("release_order", role="clinician")
    override = action("release_order", role="attending")
    actions = [draft, verify, release, override]
    initial = {
        "drafted": False,
        "high_risk": False,
        "pharmacist_verified": False,
        "released": False,
    }
    base = [
        rule(
            draft,
            requires=[condition("drafted", False)],
            effects=[effect("drafted", True), effect("high_risk", True)],
            event="order_drafted",
        ),
        rule(
            verify,
            requires=[condition("drafted", True)],
            effects=[effect("pharmacist_verified", True)],
            event="order_verified",
        ),
        rule(
            release,
            requires=[condition("pharmacist_verified", True)],
            effects=[effect("released", True)],
            event="order_released",
        ),
        rule(
            override,
            requires=[condition("pharmacist_verified", True)],
            effects=[effect("released", True)],
            event="order_released",
        ),
    ]
    bypass = rule(
        override,
        requires=[condition("drafted", True), condition("pharmacist_verified", False)],
        effects=[effect("released", True)],
        event="order_released",
    )
    return Pair(
        family="qualified_review_gate",
        policy_anchor="medication-pharmacist",
        claim=claim(
            "medication.pharmacist_verification",
            "High-risk orders require pharmacist verification before release.",
            "A high-risk medication order must be verified by a pharmacist before release.",
            [
                condition("released", True),
                condition("high_risk", True),
                condition("pharmacist_verified", False),
            ],
            severity="critical",
        ),
        clean=fixture(initial, actions, base),
        mutated=fixture(initial, actions, [*base, bypass]),
        expert_traces=[[draft, verify, release]],
        mutation_operator="remove qualified reviewer gate from override path",
        minimal_trigger=[draft, override],
        max_depth=3,
        critical=True,
    )


def _memory_pair() -> Pair:
    begin_a = action("begin_episode", episode="a")
    store = action("store_sensitive_fact")
    begin_b = action("begin_episode", episode="b")
    recall = action("recall_memory")
    actions = [begin_a, store, begin_b, recall]
    initial = {"episode": "none", "secret_present": False, "leaked": False}
    common = [
        rule(
            begin_a,
            requires=[condition("episode", "none")],
            effects=[effect("episode", "a")],
            event="episode_started",
        ),
        rule(
            store,
            requires=[condition("episode", "a")],
            effects=[effect("secret_present", True)],
            event="memory_stored",
        ),
        rule(recall, requires=[condition("episode", "a")], effects=[], event="memory_recalled"),
        rule(
            recall,
            requires=[condition("episode", "b"), condition("secret_present", False)],
            effects=[],
            event="memory_empty",
        ),
    ]
    clean_begin_b = rule(
        begin_b,
        requires=[],
        effects=[effect("episode", "b"), effect("secret_present", False)],
        event="episode_started",
    )
    mutant_begin_b = rule(
        begin_b, requires=[], effects=[effect("episode", "b")], event="episode_started"
    )
    leak = rule(
        recall,
        requires=[condition("episode", "b"), condition("secret_present", True)],
        effects=[effect("leaked", True)],
        event="memory_recalled",
    )
    return Pair(
        family="cross_episode_memory",
        policy_anchor="memory-isolation",
        claim=claim(
            "memory.episode_isolation",
            "Sensitive memory from one episode cannot appear in another.",
            "Starting a new episode clears sensitive memory from every earlier episode.",
            [condition("leaked", True)],
            severity="critical",
        ),
        clean=fixture(initial, actions, [*common, clean_begin_b]),
        mutated=fixture(initial, actions, [*common, mutant_begin_b, leak]),
        expert_traces=[[begin_a, store], [begin_b, recall]],
        mutation_operator="retain hidden memory across episode reset",
        minimal_trigger=[begin_a, store, begin_b, recall],
        max_depth=4,
        critical=True,
    )


def _reward_pair() -> Pair:
    submit = action("submit_task")
    verify = action("verify_task")
    complete = action("complete_task")
    award = action("award_reward")
    actions = [submit, verify, complete, award]
    initial = {"submitted": False, "verified": False, "completed": False, "reward": 0}
    base = [
        rule(
            submit,
            requires=[condition("submitted", False)],
            effects=[effect("submitted", True)],
            event="task_submitted",
        ),
        rule(
            verify,
            requires=[condition("submitted", True)],
            effects=[effect("verified", True)],
            event="task_verified",
        ),
        rule(
            complete,
            requires=[condition("verified", True)],
            effects=[effect("completed", True)],
            event="task_completed",
        ),
        rule(
            award,
            requires=[condition("completed", True)],
            effects=[effect("reward", 1)],
            event="reward_awarded",
        ),
    ]
    premature = rule(
        award,
        requires=[condition("submitted", True), condition("completed", False)],
        effects=[effect("reward", 1)],
        event="reward_awarded",
    )
    return Pair(
        family="reward_policy_mismatch",
        policy_anchor="reward-completion",
        claim=claim(
            "reward.only_after_completion",
            "Positive reward requires verified task completion.",
            "Award positive reward only after the task is verified and completed.",
            [condition("reward", 0, ComparisonOp.GT), condition("completed", False)],
            severity="critical",
        ),
        clean=fixture(initial, actions, base),
        mutated=fixture(initial, actions, [*base, premature]),
        expert_traces=[[submit, verify, complete, award]],
        mutation_operator="decouple reward transition from success precondition",
        minimal_trigger=[submit, award],
        max_depth=4,
        critical=True,
    )


def _observability_pair() -> Pair:
    request = action("request_privileged_operation")
    execute = action("execute_operation")
    execute_hidden = action("execute_operation", mode="hidden")
    actions = [request, execute, execute_hidden]
    initial = {"requested": False, "performed": False, "audit_logged": False}
    base = [
        rule(
            request,
            requires=[condition("requested", False)],
            effects=[effect("requested", True)],
            event="operation_requested",
        ),
        rule(
            execute,
            requires=[condition("requested", True)],
            effects=[effect("performed", True), effect("audit_logged", True)],
            event="operation_performed",
        ),
        rule(
            execute_hidden,
            requires=[condition("requested", True)],
            effects=[effect("performed", True), effect("audit_logged", True)],
            event="operation_performed",
        ),
    ]
    hidden = base[-1].model_copy(
        update={
            "effects": [effect("performed", True)],
            "event": "operation_performed_without_audit",
        }
    )
    return Pair(
        family="observability_omission",
        policy_anchor="privileged-audit",
        claim=claim(
            "operation.audit_required",
            "Every privileged operation must emit an audit record.",
            "A privileged operation and its audit record must be committed together.",
            [condition("performed", True), condition("audit_logged", False)],
        ),
        clean=fixture(initial, actions, base),
        mutated=fixture(initial, actions, [*base[:-1], hidden]),
        expert_traces=[[request, execute]],
        mutation_operator="drop audit side effect while preserving visible success",
        minimal_trigger=[request, execute_hidden],
        max_depth=2,
    )


def _search_stress_pair() -> Pair:
    decoys = [action("set_decoy", index=index) for index in range(12)]
    submit = action("submit_sensitive_request")
    approve = action("manager_approve")
    issue = action("issue_sensitive_result", role="admin")
    actions = [*decoys, submit, approve, issue]
    initial: dict[str, object] = {
        "submitted": False,
        "approved": False,
        "issued": False,
        **{f"decoy_{index}": False for index in range(12)},
    }
    decoy_rules = [
        rule(
            selected_action,
            requires=[condition(f"decoy_{index}", False)],
            effects=[effect(f"decoy_{index}", True)],
            event="irrelevant_state_changed",
        )
        for index, selected_action in enumerate(decoys)
    ]
    base = [
        *decoy_rules,
        rule(
            submit,
            requires=[condition("submitted", False)],
            effects=[effect("submitted", True)],
            event="request_submitted",
        ),
        rule(
            approve,
            requires=[condition("submitted", True)],
            effects=[effect("approved", True)],
            event="request_approved",
        ),
        rule(
            issue,
            requires=[condition("approved", True)],
            effects=[effect("issued", True)],
            event="result_issued",
        ),
    ]
    bypass = rule(
        issue,
        requires=[condition("submitted", True), condition("approved", False)],
        effects=[effect("issued", True)],
        event="result_issued",
    )
    return Pair(
        family="combinatorial_search",
        policy_anchor="stress-approval",
        claim=claim(
            "stress.approval_before_issue",
            "A sensitive result cannot be issued before manager approval.",
            "A submitted sensitive request must receive manager approval before issuance.",
            [
                condition("submitted", True),
                condition("issued", True),
                condition("approved", False),
            ],
            severity="critical",
        ),
        clean=fixture(initial, actions, base),
        mutated=fixture(initial, actions, [*base, bypass]),
        expert_traces=[[submit, approve, issue]],
        mutation_operator="hide one unsafe transition behind combinatorial irrelevant state",
        minimal_trigger=[submit, issue],
        max_depth=3,
        critical=True,
    )
