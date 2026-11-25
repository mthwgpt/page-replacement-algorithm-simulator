"""Core page-replacement logic: FIFO, LRU, Optimal (no UI code here)."""


def simulate(algo, refs, n_frames):
    """Simulate one page-replacement algorithm.

    Returns a dict with: steps, hits, faults, final_frames, total.
    Each step is a dict: page, frames (snapshot), hit (bool), replaced (page or None).
    """
    frames = [None] * n_frames      # None = empty frame
    last_used = {}                  # LRU: page -> index of most recent use
    fifo_ptr = 0                    # FIFO: next frame to be replaced (oldest page)
    hits = faults = 0
    steps = []

    for i, page in enumerate(refs):
        replaced = None
        if page in frames:                          # ---- HIT ----
            hit = True
            hits += 1
        else:                                       # ---- FAULT ----
            hit = False
            faults += 1
            if None in frames:                      # free frame available
                slot = frames.index(None)
            elif algo == "FIFO":                    # evict the oldest loaded page
                slot = fifo_ptr
            elif algo == "LRU":                     # evict least recently used page
                slot = min(range(n_frames), key=lambda s: last_used[frames[s]])
            else:                                   # Optimal: evict page used farthest in future
                def next_use(s):
                    try:
                        return refs.index(frames[s], i + 1)
                    except ValueError:
                        return float("inf")         # never used again
                slot = max(range(n_frames), key=next_use)
            replaced = frames[slot]
            frames[slot] = page
            if algo == "FIFO":
                fifo_ptr = (slot + 1) % n_frames
        last_used[page] = i
        steps.append({"page": page, "frames": list(frames), "hit": hit, "replaced": replaced})

    return {
        "algo": algo,
        "steps": steps,
        "hits": hits,
        "faults": faults,
        "final_frames": list(frames),
        "total": len(refs),
    }
