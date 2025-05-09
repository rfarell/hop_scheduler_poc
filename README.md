# Hop‑Budget‑Aware Scheduler ‒ Proof‑of‑Concept

Lightweight Python repo that demonstrates the queue‑weight algorithm from **"Hop‑Budget‑Aware Priority Scheduling for TSM Tactical MANETs"** without any external network simulator.

* **Topology :** fixed grid or imported CSV ⇒ `networkx`
* **Scheduler :** Mirror‑descent + hop‑penalty (Alg. 1) and greedy projection (Alg. 2)  
* **Traffic :** Poisson arrivals per SAP class
* **Metrics :** packet‑delivery ratio (PDR), latency, wasted slots
* **Output :** per‑frame JSONL in `results/` and summary CSV for plotting

## Quick start

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python sim.py          # runs 16‑node grid for 500 frames
python plot.py         # creates results/summary.csv + pdr.png
```

See `python sim.py --help` for CLI options.

## Further experiments

The `compare_runs.py` script allows easy comparison of different simulation parameters:

```bash
python compare_runs.py    # Runs multiple simulations and creates comparison plots
```

This will generate:
- Per-scenario results in `results/{scenario_name}/`
- Comparison bar charts in `results/comparison.png`
- PDR vs Latency tradeoff visualization in `results/pdr_latency_tradeoff.png`
- Summary table in `results/comparison_summary.csv`

## Key findings

Through our simulations, we observed several important trends:

1. **Hop Budget Impact**: Lowering the hop budget significantly reduces latency at a moderate cost to PDR
2. **Traffic Load**: Higher arrival rates can improve PDR but at the cost of increased latency
3. **Network Size**: Larger networks tend to reduce PDR and increase latency due to longer paths

The mirror-descent scheduler with hop-penalty shows effective performance for balancing delivery ratio and latency in tactical mobile networks.

## Technical notes

- The scheduler uses a sub-gradient approach for the utility gradient at the kink point
- The mirror-descent algorithm adaptively adjusts queue weights to optimize both throughput and hop feasibility
- The simulation handles path length checking with proper exception handling to prevent index errors
- Requirements are provided for reproducibility but versions are not pinned for flexibility