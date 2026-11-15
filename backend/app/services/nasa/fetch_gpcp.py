"""Optional cross-check: GPCP V3.3 monthly box means for the study regions. Owner: Developer A (task A8, "should").

Not implemented. When done it stores rows in box_observations with box
"gpcp_box_3x3" (a different product, never joined to the IMERG series) and
trends.py adds a GPCP row to the sensitivity table.
"""
from __future__ import annotations


def fetch(*_args, **_kwargs) -> None:
    raise NotImplementedError("fetch_gpcp: optional task A8, see docs/TEAM.md")
