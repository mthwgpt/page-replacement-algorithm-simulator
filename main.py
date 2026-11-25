"""
Page Replacement Algorithm Simulator  (FIFO, LRU, Optimal)
Topic 3 - Operating Systems Project

Input  : page-reference string + number of page frames
Process: read references in order, simulate frame contents, identify HIT/FAULT,
         apply the replacement rule when frames are full, count hits and faults
Output : frame-by-frame trace per algorithm, HIT/FAULT per reference, final frames,
         total hits/faults, hit/fault ratio and percentage

Run:  python main.py      (requires only the Python standard library)

Files:
  main.py        - entry point
  config.py      - constants (algorithm list, limits)
  algorithms.py  - FIFO / LRU / Optimal simulation logic
  utils.py       - input validation, formatting, text report
  app.py         - Tkinter UI
"""

from app import App

if __name__ == "__main__":
    App().mainloop()
