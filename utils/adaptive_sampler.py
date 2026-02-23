# -*- coding: utf-8 -*-
"""
utils/adaptive_sampler.py

Core biological intelligence engine. Solves Temporal Sampling Bias by
scaling sample resolution to the biological lifespan of the strain dataset.

Lifespan categories:
  Micro    (<90 days)   → Weekly sentinel sampling
  Seasonal (90-270 days) → Monthly sentinel sampling
  Endemic  (>270 days)  → Quarterly or wave-crest sampling

Phase 4 (with safeguards):
  calculate_genetic_leap() — Hamming divergence trigger.
  Mandatory safeguards: pre-cluster to <10K seqs, 30s timeout, numpy Hamming.
"""

import time

import numpy as np
import pandas as pd


class AdaptiveBiologicalSampler:
    """Proportional sampling engine for epidemiological sequence datasets."""

    # Lifespan thresholds (days)
    MICRO_MAX    = 90
    SEASONAL_MAX = 270

    def calculate_lifespan_category(self, df: pd.DataFrame) -> str:
        """Classify dataset by strain temporal lifespan.

        Returns: 'Micro', 'Seasonal', or 'Endemic'

        Requires 'collection_date' column as datetime-compatible values.
        """
        if df.empty or "collection_date" not in df.columns:
            return "Seasonal"

        dates = pd.to_datetime(df["collection_date"], errors="coerce").dropna()
        if dates.empty:
            return "Seasonal"

        span_days = (dates.max() - dates.min()).days

        if span_days < self.MICRO_MAX:
            return "Micro"
        if span_days <= self.SEASONAL_MAX:
            return "Seasonal"
        return "Endemic"

    def apply_proportionality_rule(
        self, df: pd.DataFrame, category: str = None
    ) -> pd.DataFrame:
        """Dispatch to the correct sampling resolution for the given category.

        If category is None, auto-detects via calculate_lifespan_category().
        """
        if df.empty:
            return df

        if category is None:
            category = self.calculate_lifespan_category(df)

        if category == "Micro":
            return self._weekly_sentinel_sampling(df)
        if category == "Seasonal":
            return self._monthly_sentinel_sampling(df)
        # Endemic
        return self._quarterly_or_wave_sampling(df)

    def _weekly_sentinel_sampling(self, df: pd.DataFrame) -> pd.DataFrame:
        """High-resolution sampling for short outbreaks (<90 days).

        Keeps the first unique sequence per (sequence_hash, ISO-week) pair.
        If sequence_hash is absent, falls back to first per week.
        """
        if df.empty or "collection_date" not in df.columns:
            return df

        df = df.copy()
        df["_week"] = (
            pd.to_datetime(df["collection_date"], errors="coerce")
            .dt.to_period("W")
        )

        group_cols = (
            ["sequence_hash", "_week"]
            if "sequence_hash" in df.columns
            else ["_week"]
        )

        result = (
            df.dropna(subset=["_week"])
              .sort_values("collection_date")
              .groupby(group_cols, sort=False, observed=True)
              .first()
              .reset_index()
              .drop(columns=["_week"])
        )
        return result

    def _monthly_sentinel_sampling(self, df: pd.DataFrame) -> pd.DataFrame:
        """Monthly first-of-period sampling for seasonal datasets (90-270 days).

        Keeps the first unique sequence per (sequence_hash, month) pair.
        """
        if df.empty or "collection_date" not in df.columns:
            return df

        df = df.copy()
        df["_month"] = (
            pd.to_datetime(df["collection_date"], errors="coerce")
            .dt.to_period("M")
        )

        group_cols = (
            ["sequence_hash", "_month"]
            if "sequence_hash" in df.columns
            else ["_month"]
        )

        result = (
            df.dropna(subset=["_month"])
              .sort_values("collection_date")
              .groupby(group_cols, sort=False, observed=True)
              .first()
              .reset_index()
              .drop(columns=["_month"])
        )
        return result

    def _quarterly_or_wave_sampling(self, df: pd.DataFrame) -> pd.DataFrame:
        """Quarterly or wave-crest sampling for endemic datasets (>270 days).

        Tries EpiWaveDetector first; falls back to quarterly grouping if wave
        detection returns fewer than 2 peaks (too flat a signal).
        """
        if df.empty:
            return df

        try:
            from utils.peak_detector import EpiWaveDetector
            detector = EpiWaveDetector()
            wave_analysis = detector.detect_epi_waves(df)

            if wave_analysis["wave_count"] >= 2:
                return detector.extract_wave_representatives(df, wave_analysis)
        except Exception:
            pass

        # Quarterly fallback
        if "collection_date" not in df.columns:
            return df

        df = df.copy()
        df["_quarter"] = (
            pd.to_datetime(df["collection_date"], errors="coerce")
            .dt.to_period("Q")
        )

        group_cols = (
            ["sequence_hash", "_quarter"]
            if "sequence_hash" in df.columns
            else ["_quarter"]
        )

        result = (
            df.dropna(subset=["_quarter"])
              .sort_values("collection_date")
              .groupby(group_cols, sort=False, observed=True)
              .first()
              .reset_index()
              .drop(columns=["_quarter"])
        )
        return result

    def _fallback_chronological_sampling(
        self, df: pd.DataFrame, target_n: int = 500
    ) -> pd.DataFrame:
        """Chronological fallback used when Genomic Divergence Trigger times out.

        Evenly distributes `target_n` sequences across the full time range.
        """
        if df.empty or len(df) <= target_n:
            return df

        df_sorted = df.sort_values("collection_date").reset_index(drop=True)
        step = len(df_sorted) / target_n
        indices = [int(i * step) for i in range(target_n)]
        return df_sorted.iloc[indices].copy()

    def _pre_cluster_sequences(
        self, df: pd.DataFrame, identity_threshold: float = 0.99
    ) -> pd.DataFrame:
        """Reduce dataset to <10K representatives before Hamming comparison.

        Phase 4 safeguard: deduplicate by sequence_hash first, then random
        sample if still > 10K.
        """
        if df.empty:
            return df

        out = df.copy()

        # Step 1: deduplicate by hash
        if "sequence_hash" in out.columns:
            out = out.drop_duplicates(subset=["sequence_hash"])

        # Step 2: cap at 10K via random sample
        if len(out) > 10_000:
            out = out.sample(n=10_000, random_state=42)

        return out.reset_index(drop=True)
