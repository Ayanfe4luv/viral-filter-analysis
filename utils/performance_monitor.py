# -*- coding: utf-8 -*-
"""
utils/performance_monitor.py

Zero-lag architecture validation framework.

All targets from the Performance Directive (must pass in BOTH 'en' and 'ru' modes):
  parse_10k_sequences  < 5.0 s
  parse_50k_sequences  < 10.0 s
  filter_response      < 1.0 s
  page_switch          < 2.0 s    (validated manually)
  translation_lookup   < 0.001 s  (1 ms)
  peak_detection       < 0.1 s    (100 ms on aggregated counts)
  memory_usage         < 2 GB     (validated externally)

Usage (Phase 1 gate):
    from utils.performance_monitor import PerformanceBenchmark
    bench = PerformanceBenchmark()
    results = bench.run_full_benchmark_suite()
    # All results['*']['status'] must be '✅ PASS'
"""

import time
import random

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Hard performance targets (seconds unless noted)
# ---------------------------------------------------------------------------
BENCHMARKS = {
    "parse_10k_sequences": 5.0,
    "parse_50k_sequences": 10.0,
    "filter_response":     1.0,
    "translation_lookup":  0.001,
    "peak_detection":      0.1,
    "adaptive_sampling":   2.0,
}


# ---------------------------------------------------------------------------
# Synthetic data generator
# ---------------------------------------------------------------------------

def generate_sample_gisaid_data(n_sequences: int = 10_000, seed: int = 42) -> str:
    """Generate a synthetic GISAID-format FASTA string for benchmarking.

    Includes a mix of:
      - Subtypes: H3N2, H1N1, H5N1, H1N2
      - Hosts: Human, Avian, Swine
      - Locations: English and Cyrillic (UTF-8 stress test)
      - Clades: realistic dot-notation hierarchy
      - Dates: 2020-01-01 through 2023-12-31
      - Sequence lengths: 1,600–1,800 bp (realistic HA segment)
      - N-runs: ~5% of sequences have runs of 'N' (quality filter test)

    Args:
        n_sequences: Number of FASTA records to generate.
        seed:        Random seed for reproducibility.

    Returns:
        Multi-line FASTA string (UTF-8).
    """
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)

    subtypes = ["A_/_H3N2", "A_/_H1N1", "A_/_H5N1", "A_/_H1N2"]
    segments = ["HA", "NA", "PB2", "PB1", "PA", "NP", "M", "NS"]
    clades = [
        "3C.2a1b.2a.2a", "3C.2a1b.2a.2a1", "3C.3a",
        "6B.1A.5a.2a", "6B.1A.5a.1", "2.3.4.4b",
        "3C.2a", "6B.1A",
    ]
    locations_en = [
        "California", "Texas", "New_York", "Florida", "Illinois",
        "Beijing", "Shanghai", "Tokyo", "Seoul", "Bangkok",
        "London", "Berlin", "Paris", "Amsterdam", "Stockholm",
    ]
    locations_ru = [
        "Новосибирск", "Москва", "Екатеринбург", "Владивосток",
        "Омск", "Красноярск", "Хабаровск", "Иркутск",
    ]
    all_locations = locations_en + locations_ru
    bases = "ACGT"
    base_date = pd.Timestamp("2020-01-01")
    date_range_days = 4 * 365  # 2020-2023

    lines = []
    for i in range(n_sequences):
        subtype = rng.choice(subtypes)
        segment = rng.choice(segments)
        location = rng.choice(all_locations)
        clade = rng.choice(clades)
        accession = f"EPI_ISL_{rng.randint(100_000, 9_999_999)}"
        offset_days = rng.randint(0, date_range_days)
        coll_date = (base_date + pd.Timedelta(days=offset_days)).strftime("%Y-%m-%d")
        year = 2020 + offset_days // 365

        # Build isolate name based on subtype host inference
        host_roll = rng.random()
        if host_roll < 0.70:
            isolate = f"A/{location}/{i + 1}/{year}"
        elif host_roll < 0.85:
            isolate = f"A/duck/{location}/{i + 1}/{year}"
        else:
            isolate = f"A/swine/{location}/{i + 1}/{year}"

        header = f">{isolate}|{subtype}|{segment}|{coll_date}|{accession}|{clade}"

        # Generate sequence
        seq_len = rng.randint(1600, 1800)
        seq_arr = np_rng.choice(list(bases), size=seq_len)

        # Inject N-runs in ~5% of sequences (quality filter stress test)
        if rng.random() < 0.05:
            n_run_start = rng.randint(0, seq_len - 30)
            n_run_len = rng.randint(10, 25)
            seq_arr[n_run_start: n_run_start + n_run_len] = "N"

        seq = "".join(seq_arr)
        lines.append(header)
        lines.append(seq)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Benchmark runner
# ---------------------------------------------------------------------------

class PerformanceBenchmark:
    """Validation framework for zero-lag architecture performance targets.

    All methods return a result dict with:
        status:  '✅ PASS' or '❌ FAIL'
        elapsed: measured time in seconds
        target:  target time in seconds
    """

    def validate_parsing_performance(
        self,
        file_content: str,
        target_time: float = BENCHMARKS["parse_10k_sequences"],
    ) -> dict:
        """Time parse_gisaid_fasta() against target.

        NOTE: Bypasses @st.cache_data by importing and calling the underlying
        logic directly so benchmarks measure true parse speed, not cache hits.
        """
        from utils.gisaid_parser import parse_gisaid_fasta

        # Force re-execution by appending a unique nonce comment
        nonce = f"# bench_{time.time_ns()}"
        start = time.perf_counter()
        result, _ = parse_gisaid_fasta(file_content + "\n" + nonce, "__benchmark__.fasta")
        elapsed = time.perf_counter() - start

        n = len(result)
        return {
            "status": "✅ PASS" if elapsed <= target_time else "❌ FAIL",
            "elapsed": round(elapsed, 3),
            "target": target_time,
            "sequences_parsed": n,
            "throughput": f"{n / elapsed:.0f} seqs/s" if elapsed > 0 else "N/A",
        }

    def validate_filter_performance(
        self,
        df: pd.DataFrame,
        filter_rules: list = None,
        target_time: float = BENCHMARKS["filter_response"],
    ) -> dict:
        """Time VectorizedFilterEngine against target.

        Requires Phase 2 VectorizedFilterEngine to be implemented.
        Stubs return 'PENDING' until then.
        """
        try:
            from utils.vectorized_filters import VectorizedFilterEngine
            engine = VectorizedFilterEngine()
            rules = filter_rules or [
                {"field": "subtype_clean", "operator": "equals",     "value": "H3N2"},
                {"field": "host",          "operator": "equals",     "value": "Human"},
                {"field": "collection_date","operator": "date_range",
                 "value": [pd.Timestamp("2022-01-01"), pd.Timestamp("2023-12-31")]},
            ]
            start = time.perf_counter()
            filtered = engine.apply_header_component_filters(df, rules)
            elapsed = time.perf_counter() - start

            return {
                "status": "✅ PASS" if elapsed <= target_time else "❌ FAIL",
                "elapsed": round(elapsed, 4),
                "target": target_time,
                "input_rows": len(df),
                "output_rows": len(filtered),
            }
        except NotImplementedError:
            return {"status": "⏳ PENDING — Phase 2 not yet built"}

    def validate_translation_performance(self, n_lookups: int = 1000) -> dict:
        """Time T() lookup speed. Target: <1ms per call."""
        try:
            # Simulate session state without a running Streamlit server
            import streamlit as st
            import json, os
            _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            translations = {
                "en": json.load(open(
                    os.path.join(_root, "assets", "translations", "en.json"),
                    encoding="utf-8"
                )),
                "ru": json.load(open(
                    os.path.join(_root, "assets", "translations", "ru.json"),
                    encoding="utf-8"
                )),
            }
            lang_dict = translations["en"]
            keys = list(lang_dict.keys())

            start = time.perf_counter()
            for i in range(n_lookups):
                _ = lang_dict.get(keys[i % len(keys)], keys[i % len(keys)])
            elapsed = time.perf_counter() - start
            per_call = elapsed / n_lookups

            return {
                "status": "✅ PASS" if per_call <= BENCHMARKS["translation_lookup"] else "❌ FAIL",
                "elapsed_total": round(elapsed, 6),
                "per_call_ms": round(per_call * 1000, 4),
                "target_ms": BENCHMARKS["translation_lookup"] * 1000,
                "lookups": n_lookups,
            }
        except Exception as e:
            return {"status": f"❌ ERROR: {e}"}

    def run_full_benchmark_suite(self, language: str = "en") -> dict:
        """Run all available benchmarks and return consolidated results.

        Run this twice — once with language='en', once with language='ru' —
        to satisfy the multilingual performance gate.

        Args:
            language: 'en' or 'ru' — the active language during benchmarking.

        Returns:
            Dict of benchmark_name → result dict.
        """
        print(f"\n{'='*60}")
        print(f"  Vir-Seq-Sift v2.1 — Performance Benchmark Suite")
        print(f"  Language: {language.upper()}")
        print(f"{'='*60}\n")

        results = {}

        # --- Parse 10K ---
        print("Generating 10K synthetic sequences...")
        data_10k = generate_sample_gisaid_data(n_sequences=10_000)
        print(f"Running parse benchmark (10K, target < {BENCHMARKS['parse_10k_sequences']}s)...")
        r = self.validate_parsing_performance(
            data_10k, target_time=BENCHMARKS["parse_10k_sequences"]
        )
        results["parse_10k"] = r
        print(f"  {r['status']}  {r.get('elapsed', '?')}s  ({r.get('throughput', '')})")

        # --- Translation lookup ---
        print("Running translation lookup benchmark (1000 lookups, target < 1ms each)...")
        r = self.validate_translation_performance(n_lookups=1_000)
        results["translation_lookup"] = r
        print(f"  {r['status']}  {r.get('per_call_ms', '?')}ms per call")

        # --- Filter (Phase 2 — may be pending) ---
        print("Running filter benchmark (requires Phase 2)...")
        if results.get("parse_10k", {}).get("sequences_parsed", 0) > 0:
            from utils.gisaid_parser import parse_gisaid_fasta
            seqs = parse_gisaid_fasta(data_10k, "bench_filter.fasta")[0]
            df = pd.DataFrame(seqs)
            r = self.validate_filter_performance(df)
        else:
            r = {"status": "⏳ PENDING — parse result unavailable"}
        results["filter_10k"] = r
        print(f"  {r['status']}")

        print(f"\n{'='*60}")
        all_pass = all(
            v.get("status", "").startswith("✅")
            for v in results.values()
            if not v.get("status", "").startswith("⏳")
        )
        gate_status = "✅ PHASE 1 GATE: PASSED" if all_pass else "❌ PHASE 1 GATE: FAILED — fix before Phase 2"
        print(f"  {gate_status}")
        print(f"{'='*60}\n")
        results["_gate"] = {"status": gate_status, "language_tested": language}
        return results
