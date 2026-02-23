# -*- coding: utf-8 -*-
"""
utils/hitl_extractor.py

Human-in-the-Loop extraction logic. Distinct from automated filtering
because it relies on USER STATE rather than data state.

This module handles the three manual extraction methods:
  1. Peak Checklist Selection  — expert selects from algorithm-detected peaks
  2. Custom Time Checkpoints   — expert forces extraction from specific months
  3. Visual Lasso              — expert drags zones on epidemic curve chart

All methods always include the absolute First and Last sequences (locked).

Build target (Phase 3):
  - HITLExtractor.generate_peak_checklist()
  - HITLExtractor.extract_by_checklist_selection()
  - HITLExtractor.extract_by_checkpoints()
  - HITLExtractor.extract_by_lasso()
  - HITLExtractor._get_sequences_for_period()

State keys managed by this module (stored in st.session_state):
  - selected_peaks    : list of selected peak period strings
  - lasso_zones       : list of (start_date, end_date) tuples
  - checkpoint_targets: list of 'YYYY-MM' month strings

These must persist when user switches pages and returns.
"""

import pandas as pd


class HITLExtractor:
    """Human-in-the-loop peak and checkpoint extraction.

    Phase 3: Implement all methods.
    """

    def generate_peak_checklist(self, df: pd.DataFrame) -> list[dict]:
        """Build checklist items from detected peaks for the UI.

        Calls EpiWaveDetector internally. Returns list of dicts:
            {
                'id': 'first',
                'label': 'Absolute First (Jan 2024)',
                'type': 'locked',        # locked | major_peak | minor_peak | potential_spillover
                'selected': True,
                'sequences': 1
            }

        First and Last items always have type='locked' and selected=True.
        Major peaks (count > 50) auto-selected. Minor peaks user-decides.
        Off-season clusters default to unselected — require expert decision.

        Phase 3: Implement here.
        """
        # --- STUB ---
        return []

    def extract_by_checklist_selection(
        self, df: pd.DataFrame, selected_items: list[dict]
    ) -> pd.DataFrame:
        """Extract sequences based on expert checkbox selections.

        Always includes locked First and Last. Adds one representative
        per selected peak period. Returns drop_duplicates() result.

        Phase 3: Implement here.
        """
        # --- STUB ---
        return df.head(0)

    def extract_by_checkpoints(
        self,
        df: pd.DataFrame,
        first: bool = True,
        last: bool = True,
        checkpoints: list[str] = None,
    ) -> pd.DataFrame:
        """Extract sequences from specific checkpoint months.

        Args:
            checkpoints: List of 'YYYY-MM' strings.
                         For each, extracts the first sequence of that month.

        Always includes global First and Last (locked).
        Shows st.info on found months, st.warning on empty months.

        Phase 3: Implement here.
        """
        # --- STUB ---
        return df.head(0)

    def extract_by_lasso(
        self, df: pd.DataFrame, selected_ranges: list[tuple] = None
    ) -> pd.DataFrame:
        """Extract sequences from visually-selected date ranges.

        Args:
            selected_ranges: List of (start_date, end_date) tuples.
                Filters df where collection_date falls within ANY tuple (OR logic).
                Applies weekly density sampling within each range.

        Phase 3: Implement here.
        """
        # --- STUB ---
        return df.head(0)

    def _get_sequences_for_period(
        self, df: pd.DataFrame, period
    ) -> pd.DataFrame:
        """Filter df to sequences within a given pandas Period.

        Phase 3: Implement here.
        """
        # --- STUB ---
        return df.head(0)
