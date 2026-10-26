"""Reference SMFR parser and comparator following SPECIFICATION.md Draft 0.1."""
from __future__ import annotations

from dataclasses import dataclass
import re

_PATTERN = re.compile(r"(?P<stage>[PBS])(?P<major>[1-9][0-9]*)(?P<feature>[A-Z])?(?:\.(?P<subversion>[1-9][0-9]*)(?P<revision>[A-Z])?)?", re.ASCII)
_STAGE_ORDER = {"P": 0, "B": 1, "S": 2}


class IncomparableVersions(ValueError):
    """Raised if release tracks are different."""


@dataclass(frozen=True)
class SMFRVersion:
    stage: str
    major: int
    feature: str | None = None
    subversion: int | None = None
    revision: str | None = None

    def __str__(self) -> str:
        return (f"{self.stage}{self.major}{self.feature or ''}"
                + (f".{self.subversion}" if self.subversion is not None else "")
                + (self.revision or ""))

    @property
    def warnings(self) -> tuple[str, ...]:
        warnings: list[str] = []
        if self.major > 99:
            warnings.append("major exceeds the recommended range 1–99")
        if self.subversion is not None and self.subversion > 99:
            warnings.append("subversion exceeds the recommended range 1–99")
        return tuple(warnings)


def parse(value: str) -> SMFRVersion:
    if not isinstance(value, str):
        raise ValueError("SMFR version must be a string")
    match = _PATTERN.fullmatch(value)
    if match is None:
        raise ValueError(f"Invalid SMFR version: {value!r}")
    groups = match.groupdict()
    return SMFRVersion(
        stage=groups["stage"],
        major=int(groups["major"]),
        feature=groups["feature"],
        subversion=int(groups["subversion"]) if groups["subversion"] else None,
        revision=groups["revision"],
    )


def validate(value: str) -> bool:
    try:
        parse(value)
    except ValueError:
        return False
    return True


def compare(left: str | SMFRVersion, right: str | SMFRVersion) -> int:
    """Return -1, 0, or 1; throw when feature tracks differ."""
    a = parse(left) if isinstance(left, str) else left
    b = parse(right) if isinstance(right, str) else right
    if a.feature != b.feature:
        raise IncomparableVersions("Different SMFR feature tracks")
    def order(v: SMFRVersion) -> tuple[int, int, int, int]:
        return (v.major, v.subversion or 0,
                ord(v.revision) - ord("A") + 1 if v.revision else 0,
                _STAGE_ORDER[v.stage])
    return (order(a) > order(b)) - (order(a) < order(b))
