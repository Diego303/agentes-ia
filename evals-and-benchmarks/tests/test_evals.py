import yaml

from opsagent_evals import DATASETS
from opsagent_evals.benchmarks import THRESHOLDS, run_all
from opsagent_evals.graders import grade
from opsagent_evals.judge import agreement

RESULT = {
    "reply": "La causa probable es v2.14.0 (pool reducido). Recomiendo rollback.",
    "stop": "end_turn",
    "tainted": False,
    "pending_approval": None,
    "trajectory": [
        {"tool": "get_service_status", "decision": "allow"},
        {"tool": "list_recent_deployments", "decision": "allow"},
        {"tool": "create_incident", "decision": "deny"},
    ],
}


def test_grade_passes_matching_expectations():
    expect = {
        "tools_called": ["get_service_status"],
        "tools_not_called": ["create_incident"],  # pedida pero denegada: no se ejecutó
        "answer_any": [["v2.14.0"], ["rollback", "revertir"]],
        "stop": "end_turn",
    }
    assert grade(expect, RESULT) == []


def test_grade_reports_each_failure():
    expect = {"tools_called": ["consult_change_advisor"], "answer_any": [["SEV1"]], "tainted": True}
    failures = grade(expect, RESULT)
    assert len(failures) == 3


def test_grade_two_turn_approval_case():
    first = {**RESULT, "stop": "approval_required", "pending_approval": {"name": "create_incident"}}
    second = {**RESULT, "trajectory": [{"tool": "create_incident", "decision": "rejected"}]}
    assert (
        grade({"pending_tool": "create_incident", "tools_not_called": ["create_incident"]}, second, first)
        == []
    )


def test_agreement_kappa():
    assert agreement([True, False, True, False], [True, False, True, False]) == {
        "accuracy": 1.0,
        "kappa": 1.0,
    }
    assert agreement([True, True, False, False], [True, False, True, False])["kappa"] == 0.0


def test_datasets_are_well_formed():
    allowed = {"tools_called", "tools_not_called", "answer_any", "stop", "pending_tool", "tainted"}
    tasks = yaml.safe_load((DATASETS / "agent_tasks.yaml").read_text(encoding="utf-8"))
    assert len({t["id"] for t in tasks}) == len(tasks)
    for task in tasks:
        assert set(task["expect"]) <= allowed, task["id"]
    calibration = yaml.safe_load((DATASETS / "judge_calibration.yaml").read_text(encoding="utf-8"))
    assert {True, False} == {c["human_pass"] for c in calibration}


def test_offline_benchmarks_meet_thresholds():
    results = run_all()
    for name, threshold in THRESHOLDS.items():
        assert results[name] >= threshold, (name, results[name])
