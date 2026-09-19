from spine.errors import (
    ClaimConflict,
    ContractError,
    EvaluationInvalid,
    ExternalError,
    HumanInterventionRequired,
    InconsistentState,
    InvalidTransition,
    ReviewInvalid,
    SpineError,
    UsageError,
    exit_code_for,
)
from spine.model import ContractError as ModelContractError


def test_exit_codes():
    assert SpineError().exit_code == 1
    assert UsageError().exit_code == 2
    assert InvalidTransition("ready → done").exit_code == 3
    assert ClaimConflict("held").exit_code == 4
    assert EvaluationInvalid("evals").exit_code == 5
    assert ReviewInvalid("reviews").exit_code == 5
    assert ContractError("bad yaml").exit_code == 5
    assert HumanInterventionRequired("reviewing").exit_code == 6
    assert ExternalError("npx").exit_code == 7
    assert InconsistentState("corrupt").exit_code == 8


def test_contract_error_is_spine_error():
    assert ModelContractError is ContractError
    assert issubclass(ContractError, SpineError)


def test_exit_code_for_legacy_and_typed():
    assert exit_code_for(InvalidTransition("x")) == 3
    assert exit_code_for(ValueError("legacy")) == 1
    assert exit_code_for(FileNotFoundError("missing")) == 1
