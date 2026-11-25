"""Helper functions: input validation, formatting, and text-report export."""

from config import MAX_FRAMES, MAX_REFS


def parse_input(ref_text, frame_text):
    """Validate and parse user input. Raises ValueError with a friendly message."""
    tokens = ref_text.replace(",", " ").split()
    if not tokens:
        raise ValueError("Please enter a page-reference string (e.g. 7 0 1 2 0 3 0 4).")
    if len(tokens) > MAX_REFS:
        raise ValueError(f"Reference string is too long (max {MAX_REFS} pages).")
    for t in tokens:
        if not t.isdigit():
            raise ValueError(f"Invalid page '{t}'. Pages must be non-negative integers.")
    refs = [int(t) for t in tokens]

    try:
        n = int(frame_text)
    except ValueError:
        raise ValueError("Number of frames must be a whole number.")
    if not 1 <= n <= MAX_FRAMES:
        raise ValueError(f"Number of frames must be between 1 and {MAX_FRAMES}.")
    return refs, n


def fmt(page):
    return "-" if page is None else str(page)


def pct(part, total):
    return (part / total * 100) if total else 0.0


def result_text(res, n_frames):
    """Plain-text report for one algorithm (used for export)."""
    lines = [f"=== {res['algo']} ({n_frames} frames) ==="]
    header = f"{'Step':<5}{'Page':<6}" + "".join(f"{'F' + str(i + 1):<5}" for i in range(n_frames)) + "Result"
    lines.append(header)
    lines.append("-" * len(header))
    for k, s in enumerate(res["steps"], 1):
        row = f"{k:<5}{s['page']:<6}" + "".join(f"{fmt(f):<5}" for f in s["frames"])
        row += "HIT" if s["hit"] else f"FAULT (replaced {fmt(s['replaced'])})" if s["replaced"] is not None else "FAULT"
        lines.append(row)
    lines.append("")
    lines.append("Final frames : " + " | ".join(fmt(f) for f in res["final_frames"]))
    lines.append(f"Total refs   : {res['total']}")
    lines.append(f"Hits         : {res['hits']}  ({pct(res['hits'], res['total']):.2f}%)")
    lines.append(f"Faults       : {res['faults']}  ({pct(res['faults'], res['total']):.2f}%)")
    lines.append(f"Hit:Fault    : {res['hits']}:{res['faults']}")
    lines.append("")
    return "\n".join(lines)
