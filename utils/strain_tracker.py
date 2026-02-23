# -*- coding: utf-8 -*-
"""
utils/strain_tracker.py

Longitudinal strain lifecycle analysis.

STATUS: SPECIFICATION PENDING — stub only.
Before implementing, define:
  - What constitutes a "strain" identity (sequence_hash? clade? subtype+clade?)
  - What "lifecycle" means: prevalence across seasons? cross-host transmission?
  - Does this use sequence_hash for identity tracking across sessions?
  - Does it interact with strain_hashes in session_state?
  - Output format: DataFrame, dict, or visualization-ready structure?

Spec should be finalized before Phase 4 begins (see roadmap Step 0c).

Build target (Phase 4 — after spec):
  - StrainTracker.track_strain_prevalence()
  - StrainTracker.detect_inter_annual_persistence()
  - StrainTracker.identify_overwintering_candidates()
"""

import pandas as pd


class StrainTracker:
    """Longitudinal strain lifecycle analysis.

    Phase 4: Implement after specification is finalized (Step 0c of roadmap).
    """

    def track_strain_prevalence(self, df: pd.DataFrame) -> pd.DataFrame:
        """Track strain prevalence across time periods.

        Phase 4: Implement after spec is finalized.
        """
        # --- STUB: Awaiting specification ---
        raise NotImplementedError(
            "StrainTracker requires specification before implementation. "
            "See roadmap Step 0c."
        )
