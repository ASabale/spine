from __future__ import annotations

class SpineError(Exception):
    exit_code = 1

class UsageError(SpineError):
    exit_code = 2

class InvalidTransition(SpineError):
    exit_code = 3

class ClaimConflict(SpineError):
    exit_code = 4

class EvaluationInvalid(SpineError):
    exit_code = 5

class ReviewInvalid(SpineError):
    exit_code = 5

class ContractError(SpineError):
    exit_code = 5


class AmbiguousArtifact(SpineError):
    """More than one artifact matches. Callers must not pick a winner."""

    exit_code = 5

    def __init__(self, spec: str, matches: list[str]):
        self.spec = spec
        self.matches = list(matches)
        listed = ", ".join(self.matches)
        super().__init__(f"ambiguous artifact {spec}: {listed}")

class HumanInterventionRequired(SpineError):
    exit_code = 6

class ExternalError(SpineError):
    exit_code = 7

class InconsistentState(SpineError):
    exit_code = 8

def exit_code_for(exc: BaseException) -> int:
    if isinstance(exc, SpineError):
        return exc.exit_code
    if isinstance(exc, (ValueError, FileNotFoundError)):
        return 1
    return 1