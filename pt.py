"""
Page Replacement Algorithm Simulator  (FIFO, LRU, Optimal)
Topic 3 - Operating Systems Project

Input  : page-reference string + number of page frames
Process: read references in order, simulate frame contents, identify HIT/FAULT,
         apply the replacement rule when frames are full, count hits and faults
Output : frame-by-frame trace per algorithm, HIT/FAULT per reference, final frames,
         total hits/faults, hit/fault ratio and percentage

Run:  python page_replacement_simulator.py      (requires only the Python standard library)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

ALGORITHMS = ["FIFO", "LRU", "Optimal"]
MAX_FRAMES = 10
MAX_REFS = 60


# ----------------------------------------------------------------------------
# CORE LOGIC (no UI code here)
# ----------------------------------------------------------------------------
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


# ----------------------------------------------------------------------------
# USER INTERFACE
# ----------------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Page Replacement Simulator - FIFO | LRU | Optimal")
        self.geometry("1000x680")
        self.minsize(820, 560)
        self.results = {}
        self.n_frames = 0
        self.refs = []
        self._build_style()
        self._build_input_panel()
        self._build_output_area()
        self.ref_var.set("7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1")
        self.frames_var.set("3")

    # ---------- styling ----------
    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 15, "bold"))
        style.configure("Sub.TLabel", font=("Segoe UI", 9), foreground="#555")
        style.configure("Treeview", rowheight=24, font=("Consolas", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Run.TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("Stat.TLabel", font=("Segoe UI", 10))

    # ---------- input ----------
    def _build_input_panel(self):
        top = ttk.Frame(self, padding=(14, 10, 14, 4))
        top.pack(fill="x")
        ttk.Label(top, text="Page Replacement Simulator", style="Title.TLabel").grid(row=0, column=0, columnspan=4, sticky="w")
        ttk.Label(top, text="FIFO  •  LRU  •  Optimal", style="Sub.TLabel").grid(row=1, column=0, columnspan=4, sticky="w", pady=(0, 8))

        ttk.Label(top, text="Reference string:").grid(row=2, column=0, sticky="w")
        self.ref_var = tk.StringVar()
        ref_entry = ttk.Entry(top, textvariable=self.ref_var, font=("Consolas", 11))
        ref_entry.grid(row=2, column=1, columnspan=3, sticky="ew", padx=6, pady=3)
        ref_entry.bind("<Return>", lambda e: self.run())

        ttk.Label(top, text="Number of frames:").grid(row=3, column=0, sticky="w")
        self.frames_var = tk.StringVar()
        ttk.Spinbox(top, from_=1, to=MAX_FRAMES, width=6, textvariable=self.frames_var).grid(row=3, column=1, sticky="w", padx=6, pady=3)

        ttk.Label(top, text="(separate pages with spaces or commas)", style="Sub.TLabel").grid(row=3, column=2, columnspan=2, sticky="w")
        top.columnconfigure(1, weight=1)

        btns = ttk.Frame(top)
        btns.grid(row=4, column=0, columnspan=4, sticky="w", pady=(8, 2))
        ttk.Button(btns, text="▶  Run Simulation", style="Run.TButton", command=self.run).pack(side="left")
        ttk.Button(btns, text="Sample", command=self.load_sample).pack(side="left", padx=6)
        ttk.Button(btns, text="Random", command=self.random_input).pack(side="left")
        ttk.Button(btns, text="Clear", command=self.clear).pack(side="left", padx=6)
        ttk.Button(btns, text="Export to .txt", command=self.export).pack(side="left")

    # ---------- output ----------
    def _build_output_area(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=(6, 12))
        self.tabs = {}
        for name in ALGORITHMS:
            self._make_algo_tab(name)
        self._make_summary_tab()

    def _make_algo_tab(self, name):
        frame = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(frame, text=f"  {name}  ")
        tree_holder = ttk.Frame(frame)
        tree_holder.pack(fill="both", expand=True)
        tree = ttk.Treeview(tree_holder, show="headings")
        ysb = ttk.Scrollbar(tree_holder, orient="vertical", command=tree.yview)
        xsb = ttk.Scrollbar(tree_holder, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        ysb.grid(row=0, column=1, sticky="ns")
        xsb.grid(row=1, column=0, sticky="ew")
        tree_holder.rowconfigure(0, weight=1)
        tree_holder.columnconfigure(0, weight=1)
        tree.tag_configure("hit", background="#d9f2dd")
        tree.tag_configure("fault", background="#fbdcdc")

        stats = ttk.Label(frame, text="Run the simulation to see results.", style="Stat.TLabel", justify="left")
        stats.pack(anchor="w", pady=(8, 0))
        self.tabs[name] = {"tree": tree, "stats": stats}

    def _make_summary_tab(self):
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="  Comparison  ")
        cols = ("algo", "hits", "faults", "hit_pct", "fault_pct", "ratio")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=5)
        heads = {"algo": "Algorithm", "hits": "Hits", "faults": "Faults",
                 "hit_pct": "Hit %", "fault_pct": "Fault %", "ratio": "Hit : Fault"}
        for c in cols:
            tree.heading(c, text=heads[c])
            tree.column(c, anchor="center", width=130)
        tree.pack(fill="x")
        tree.tag_configure("best", background="#d9f2dd")
        self.summary_tree = tree
        self.summary_note = ttk.Label(frame, text="", style="Stat.TLabel", justify="left", wraplength=900)
        self.summary_note.pack(anchor="w", pady=10)

    # ---------- actions ----------
    def run(self):
        try:
            refs, n = parse_input(self.ref_var.get(), self.frames_var.get())
        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))
            return
        self.refs, self.n_frames = refs, n
        self.results = {a: simulate(a, refs, n) for a in ALGORITHMS}
        for a in ALGORITHMS:
            self._show_algo(a)
        self._show_summary()

    def _show_algo(self, name):
        res = self.results[name]
        tab = self.tabs[name]
        tree = tab["tree"]
        tree.delete(*tree.get_children())
        cols = ["step", "page"] + [f"f{i}" for i in range(self.n_frames)] + ["result", "replaced"]
        tree["columns"] = cols
        tree.heading("step", text="Step")
        tree.heading("page", text="Page")
        tree.column("step", width=55, anchor="center", stretch=False)
        tree.column("page", width=60, anchor="center", stretch=False)
        for i in range(self.n_frames):
            tree.heading(f"f{i}", text=f"Frame {i + 1}")
            tree.column(f"f{i}", width=75, anchor="center", stretch=False)
        tree.heading("result", text="HIT / FAULT")
        tree.heading("replaced", text="Replaced")
        tree.column("result", width=100, anchor="center", stretch=False)
        tree.column("replaced", width=90, anchor="center", stretch=False)

        for k, s in enumerate(res["steps"], 1):
            row = [k, s["page"]] + [fmt(f) for f in s["frames"]]
            row += ["HIT" if s["hit"] else "FAULT", fmt(s["replaced"]) if not s["hit"] else ""]
            tree.insert("", "end", values=row, tags=("hit" if s["hit"] else "fault",))

        total = res["total"]
        tab["stats"].config(text=(
            f"Final frames: [ {' | '.join(fmt(f) for f in res['final_frames'])} ]\n"
            f"Total references: {total}    Hits: {res['hits']} ({pct(res['hits'], total):.2f}%)    "
            f"Faults: {res['faults']} ({pct(res['faults'], total):.2f}%)    "
            f"Hit:Fault ratio = {res['hits']}:{res['faults']}"
        ))

    def _show_summary(self):
        self.summary_tree.delete(*self.summary_tree.get_children())
        best = min(r["faults"] for r in self.results.values())
        for a in ALGORITHMS:
            r = self.results[a]
            tag = ("best",) if r["faults"] == best else ()
            self.summary_tree.insert("", "end", tags=tag, values=(
                a, r["hits"], r["faults"],
                f"{pct(r['hits'], r['total']):.2f}%", f"{pct(r['faults'], r['total']):.2f}%",
                f"{r['hits']}:{r['faults']}"))
        winners = [a for a in ALGORITHMS if self.results[a]["faults"] == best]
        self.summary_note.config(text=(
            f"Reference string ({len(self.refs)} pages): {' '.join(map(str, self.refs))}\n"
            f"Frames: {self.n_frames}\n"
            f"Fewest page faults: {', '.join(winners)} ({best} faults).  "
            f"Optimal is the theoretical lower bound, so no algorithm can do better than it."
        ))

    def load_sample(self):
        self.ref_var.set("7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1")
        self.frames_var.set("3")
        self.run()

    def random_input(self):
        import random
        refs = [random.randint(0, 9) for _ in range(random.randint(15, 25))]
        self.ref_var.set(" ".join(map(str, refs)))
        self.frames_var.set(str(random.randint(3, 4)))
        self.run()

    def clear(self):
        self.ref_var.set("")
        self.frames_var.set("3")
        self.results = {}
        for a in ALGORITHMS:
            self.tabs[a]["tree"].delete(*self.tabs[a]["tree"].get_children())
            self.tabs[a]["stats"].config(text="Run the simulation to see results.")
        self.summary_tree.delete(*self.summary_tree.get_children())
        self.summary_note.config(text="")

    def export(self):
        if not self.results:
            messagebox.showinfo("Nothing to export", "Run a simulation first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text file", "*.txt")],
                                            initialfile="page_replacement_results.txt")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"Reference string: {' '.join(map(str, self.refs))}\nFrames: {self.n_frames}\n\n")
            for a in ALGORITHMS:
                f.write(result_text(self.results[a], self.n_frames) + "\n")
        messagebox.showinfo("Exported", f"Results saved to:\n{path}")


if __name__ == "__main__":
    App().mainloop()