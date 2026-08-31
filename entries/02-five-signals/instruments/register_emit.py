"""Per-event evidence for The Null Register, Entry 02.

The five studies publish summary statistics: a mean, a confidence interval, a
placebo p. A reader is asked to take on faith that 9,470 events averaged
-0.13%. That is exactly the shape of claim this register exists to refuse, so
every study now writes the rows underneath its summary and a stranger
recomputes the published figure from them, offline, without our code.

Emission is NOT optional and NOT flag-gated. A study that can produce a summary
without producing the rows behind it can drift from its own evidence, which is
the failure mode the register was built around. Writing the rows in the same
function call that writes the summary is what makes that impossible.

Rows land in strategies/_data/register/<question>_events.jsonl, one JSON object
per line, in the order the study scored them.

Added 2026-08-31.
"""
import json
import os

_D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "strategies", "_data")
REGISTER = os.path.join(_D, "register")


def emit(question, rows, tally=None):
    """Write one line per scored event, plus a trailing manifest line.

    `rows` is the study's own event list, untouched — the same objects whose
    values produced the summary. `tally` is the survivorship/exclusion dict, so
    the counts a reader is asked to accept ship beside the rows they describe.
    Returns the path written, for the study to print.
    """
    os.makedirs(REGISTER, exist_ok=True)
    path = os.path.join(REGISTER, f"{question.lower()}_events.jsonl")
    with open(path, "w") as fh:
        for r in rows:
            fh.write(json.dumps({"q": question, **r}, sort_keys=True) + "\n")
        fh.write(json.dumps({"q": question, "_manifest": True,
                             "n_rows": len(rows),
                             "exclusions": tally or {}}, sort_keys=True) + "\n")
    return path
