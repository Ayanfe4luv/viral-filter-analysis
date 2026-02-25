# Vir-Seq-Sift v2.1 — 76 Use Cases for Beginners
## Using HA_test_copy1.fasta as Your Example Dataset

---

### About This Guide

This guide walks you through 76 concrete, step-by-step tasks you can perform in Vir-Seq-Sift v2.1 using a real dataset: **HA_test_copy1.fasta**, which contains H3N2 influenza hemagglutinin (HA) sequences collected in Novosibirsk, Russia in 2024, other data sets can be found on the site. Every sequence header follows the pattern:

```
>A/Novosibirsk/RII-7.429/2024|A_/_H3N2|HA|2024-01-17|EPI_ISL_19324838|3C.2a1b.2a.2a.3a.1
```

Fields in order: Name | Subtype | Segment | Date | EPI_ISL Accession | Clade

The app has six pages accessible via the sidebar navigation (shown below the logo and language selector):
1. **🌍 Observatory** — KPI dashboard, epidemic curve, clade distribution, virus support grid
2. **📁 Workspace** — Upload FASTA files, activate datasets, URL fetch
3. **🔬 Sequence Refinery** — Quality filters, header-component filters, HITL phylogenetic sub-sampling
4. **🧬 Molecular Timeline** — Persistence and overwintering analysis across seasons
5. **📊 Analytics** — 10+ chart types and dataset overview gauges
6. **📋 Export** — Download FASTA, CSV, ZIP bundle, accession lists, session log

Vir-Seq-Sift v2.1 supports influenza A (all subtypes including H5N1 avian), influenza B (Victoria and Yamagata lineages), and RSV (types A and B). Multi-virus and multi-host surveillance datasets are fully supported as long as each sequence uses the correct pipe-delimited header format.

---

## Category 1: Basic Loading and Exploration (Use Cases 1–8)

---

## Use Case 1: Upload Your First FASTA File

**Goal:** Get HA_test_copy1.fasta into Vir-Seq-Sift so you can begin working with it.

**Page:** Workspace

**Step-by-step:**
1. Open Vir-Seq-Sift in your browser. You will land on the Observatory page by default; click **Workspace** in the top navigation to go to the upload area.
2. Look for the radio button row near the top of the page that reads: **File Upload | URL Download**. Make sure **File Upload** is selected (it is the default).
3. Under the **Upload Files** heading you will see a drag-and-drop area labelled **Upload FASTA files**. Click it or drag your file onto it.
4. Navigate to HA_test_copy1.fasta on your computer and select it. The file browser accepts `.fasta`, `.fa`, `.fas`, `.fna`, `.txt`, and `.gz` extensions.
5. A progress bar labelled **Processing uploaded files...** will appear. Wait until it reads **Processing complete!**
6. A green success banner will appear: "Loaded 1 new files (N seqs)." A small toast popup will confirm the file is ready.
7. If the active dataset is empty, a blue info box will say: "Go to 'Manage Datasets' to activate files for analysis." That is your next step.

**Expected result:** The sidebar Quick Stats panel shows **Files Loaded: 1**. The file name HA_test_copy1.fasta appears in the Workspace file list.

**Tip for beginners:** You do not need to convert or rename your FASTA file before uploading. Vir-Seq-Sift reads the pipe-separated header format used in this dataset automatically.

---

## Use Case 2: Activate a Dataset for Analysis

**Goal:** Make the uploaded file the "active dataset" so every other page can work with it.

**Page:** Workspace

**Step-by-step:**
1. After uploading (see Use Case 1), stay on the **Workspace** page. Scroll down to the **Loaded Datasets** section.
2. You will see a multi-select box labelled **Select files to activate:** with an entry such as `HA_test_copy1.fasta (N seqs)`. Click the entry to highlight it.
3. A blue info box below the multi-select will confirm: "Selected: 1 files (N total seqs)."
4. A small preview table will appear showing the file name, total sequence count, and the top subtypes found.
5. Click the blue **Activate Selected Files** button. A spinner reads **Processing...**
6. A green success banner confirms: "Activated 1 files (N seqs)." Two navigation buttons appear: one for **Analyze & Process** and one for **Export & Reports**.

**Expected result:** The sidebar Quick Stats now shows **Active Sequences: N** and **Avg Length: ~1700 bp** (typical for full-length HA segments). The **Active Dataset** panel at the bottom of the Workspace page also lists the file name and sequence count.

**Tip for beginners:** Nothing in Vir-Seq-Sift will work on your data until you click **Activate Selected Files**. Think of activation as "loading the experiment."

---

## Use Case 3: View the Observatory KPI Dashboard

**Goal:** Get a one-screen summary of your dataset without running any analysis.

**Page:** Observatory

**Step-by-step:**
1. With the dataset activated, click **Observatory** in the top navigation.
2. The page loads a KPI dashboard automatically. Look for three metric cards near the top: **Sequence Count**, **Avg Length (bp)**, and **Completeness %**.
3. Below the KPI cards you will find an **Epidemic Curve** chart showing sequences plotted over time. For this dataset, all data points should cluster in 2024.
4. Further down, a **Clade Distribution** panel shows which phylogenetic clades are present and in what proportions.
5. Hover your mouse over any bar, slice, or data point to see exact numbers in a tooltip.

**Expected result:** The KPI cards report the total number of sequences in HA_test_copy1.fasta, an average length around 1,700 bp (full-length HA), and a high completeness percentage since these are well-annotated sequences. The epidemic curve shows activity concentrated in early-to-mid 2024.

**Tip for beginners:** The Observatory page is read-only. Nothing here changes your data. Use it as your "first look" every time you load a new file.

---

## Use Case 4: Check the Sidebar Quick Stats

**Goal:** Confirm at a glance that the correct number of sequences is loaded and active.

**Page:** Any (sidebar is always visible)

**Step-by-step:**
1. Activate HA_test_copy1.fasta as described in Use Case 2.
2. Look at the left sidebar. Under the heading **Quick Stats** you will see three metric boxes.
3. **Files Loaded** shows how many files have been uploaded in this session.
4. **Active Sequences** shows how many sequences are currently in the active dataset. This number changes every time you apply a filter.
5. **Avg Length** shows the mean nucleotide length of sequences in the active dataset, expressed in base pairs (bp).
6. Below those metrics, **Merged from** tells you how many files were combined to form the current active dataset (useful when you activate multiple files at once).

**Expected result:** You see numbers consistent with the HA_test_copy1.fasta file. Avg Length should be approximately 1,695–1,701 bp for standard H3N2 HA sequences.

**Tip for beginners:** Watch the **Active Sequences** count in the sidebar as you apply filters throughout your session. It is the fastest way to see how many sequences remain after each step.

---

## Use Case 5: Browse the Clade Distribution on Observatory

**Goal:** Find out which H3N2 clades are represented in the dataset before doing any filtering.

**Page:** Observatory

**Step-by-step:**
1. Activate the dataset and navigate to **Observatory**.
2. Scroll down past the KPI cards and epidemic curve until you reach the **Clade Distribution** panel.
3. You will see a chart (bar or pie depending on your settings) where each segment represents one phylogenetic clade detected in the headers.
4. For HA_test_copy1.fasta, you should see entries such as `3C.2a1b.2a.2a.3a.1` and potentially related sub-clades.
5. Hover over each bar or slice to read the exact sequence count and percentage.
6. Note which clade has the most sequences — this is the dominant lineage in your Novosibirsk 2024 cohort.

**Expected result:** The chart shows at least one dominant clade beginning with `3C.2a1b`, which is the currently circulating H3N2 sub-clade as of 2024. Other closely related variants may appear as minor groups.

**Tip for beginners:** Clade names in H3N2 follow a hierarchical naming convention separated by dots. A name like `3C.2a1b.2a.2a.3a.1` means: top-level clade 3C, sub-clade 2a1b, and so on. Each extra dot level is a finer subdivision.

---

## Use Case 6: Understand the FASTA Header Format

**Goal:** Learn what each field in the sequence headers means before you start filtering.

**Page:** Workspace (preview table), or any page where headers are visible

**Step-by-step:**
1. Activate the dataset and go to **Workspace**.
2. Select HA_test_copy1.fasta in the multi-select and read the **Preview: Selected Files** table that appears below.
3. The **Top Subtypes** column will show `A_/_H3N2: N` (where N is the count), confirming the subtype field is being read correctly.
4. For a deeper look at header structure, navigate to **Sequence Refinery** and look at the header-component filter controls. Each dropdown (Subtype, Host, Segment, Location, Clade, Accession) corresponds to one pipe-separated field.
5. Specifically:
   - **Field 1** (Name): e.g., `A/Novosibirsk/RII-7.429/2024`
   - **Field 2** (Subtype): e.g., `A_/_H3N2`
   - **Field 3** (Segment): e.g., `HA`
   - **Field 4** (Date): e.g., `2024-01-17`
   - **Field 5** (EPI_ISL Accession): e.g., `EPI_ISL_19324838`
   - **Field 6** (Clade): e.g., `3C.2a1b.2a.2a.3a.1`

**Expected result:** You can identify each metadata component and understand which Sequence Refinery control targets which pipe field.

**Tip for beginners:** If any field reads "Unknown" in the app, it means the header parser could not find that piece of information. This is common for older or non-standard FASTA files. The HA_test_copy1.fasta file uses a clean standard format, so all fields should parse correctly.

---

## Use Case 7: Switch Between English and Russian Interface

**Goal:** Change the app language to Russian for a Russian-speaking collaborator.

**Page:** Any (sidebar language selector)

**Step-by-step:**
1. Look at the very top of the left sidebar. You will see a language selector showing either `English` or `Русский` with flag icons.
2. Click the selector and choose **Русский** (Russian).
3. A toast message will confirm: "Switched to Русский."
4. All UI labels, buttons, and help text will now appear in Russian.
5. To switch back, click the same selector and choose **English**.

**Expected result:** The tab labels change to Russian equivalents, e.g., **Загрузка и Настройка** (Upload & Setup), **Анализ и Обработка** (Analyze & Process), etc. All your data remains intact — only labels change.

**Tip for beginners:** Your data, filters, and active sequences are not lost when you switch languages. The language setting only affects how labels are displayed. Switching back to English restores all English labels immediately.

---

## Use Case 8: Switch Between Light and Dark Theme

**Goal:** Change the visual theme to Dark mode to reduce eye strain during a long analysis session.

**Page:** Any (sidebar theme selector)

**Step-by-step:**
1. In the left sidebar, just below the language selector, find the **Theme** radio buttons with three options: **Auto**, **Light**, and **Dark**.
2. Click **Dark** (shown with a moon icon).
3. The page background, chart backgrounds, and card colors will all shift to dark tones immediately.
4. If you prefer automatic switching, choose **Auto**. In Auto mode, the app uses Light theme during daytime hours (06:00–20:00) and Dark theme at night.
5. The current time is shown as a caption: "Auto mode: Light (14:32)" when Auto is selected.

**Expected result:** Charts, tables, and cards render with dark backgrounds and light text. The sidebar caption confirms the current theme and time when in Auto mode.

**Tip for beginners:** Dark mode does not affect any computations. Charts and tables look and behave identically in both modes. Choose whichever is more comfortable for your screen and lighting conditions.

---

## Category 2: Quality Filtering (Use Cases 9–15)

---

## Use Case 9: Remove Sequences That Are Too Short

**Goal:** Discard any HA sequences shorter than 1,600 nucleotides to ensure you are working with near-full-length sequences only.

**Page:** Sequence Refinery

**Step-by-step:**
1. Activate the dataset and navigate to **Sequence Refinery**.
2. Find the **Quality Filter** section. It contains two sliders.
3. The first slider is labelled **Min Sequence Length**. By default it is set to 200.
4. Drag the slider to **1600** (or type 1600 in the number box if available).
5. Leave the **Max N-Run Length** slider at its default value of 100 for now.
6. Click the **Apply Quality Filter** button.
7. A spinner reads "Applying quality filter..." and then a success message confirms the filter ran.
8. Check the **Active Sequences** count in the sidebar. It will be equal to or less than the original count.

**Expected result:** All sequences shorter than 1,600 bp are removed. For HA_test_copy1.fasta, most sequences should pass since standard H3N2 HA is ~1,700 bp. The sidebar count should change only slightly or not at all if the file already contains full-length sequences.

**Tip for beginners:** For influenza HA, a length of 1,600 bp is a commonly used threshold for "near full-length." Sequences shorter than this often represent partial amplicons or truncated assemblies that are unreliable for phylogenetic analysis.

---

## Use Case 10: Remove Sequences with Excessive Ambiguous Nucleotides

**Goal:** Remove sequences that contain long stretches of "N" characters, which indicate positions of low sequencing quality or failed assembly.

**Page:** Sequence Refinery

**Step-by-step:**
1. Activate the dataset and navigate to **Sequence Refinery**.
2. Go to the **Quality Filter** section.
3. Find the **Max N-Run Length** slider. By default it is set to 100.
4. Drag it to **20** to enforce a stricter cutoff — any sequence with a continuous run of 20 or more "N" characters will be removed.
5. Leave **Min Sequence Length** at 200 (or your preferred value from Use Case 9).
6. Click **Apply Quality Filter**.
7. A success notification confirms the filter was applied.

**Expected result:** Sequences with runs of 20+ consecutive N characters are removed. High-quality Sanger or Illumina-assembled sequences from GISAID typically have very few or no N-runs, so most sequences in HA_test_copy1.fasta should survive this filter.

**Tip for beginners:** An "N" in a nucleotide sequence means "unknown base." A long run of N's (e.g., NNNNNNNNNNN) usually indicates a sequencing gap or a masked region. Such sequences can produce misleading results in phylogenetic trees, which is why removing them is good practice.

---

## Use Case 11: Apply Both Length and N-Run Filters Simultaneously

**Goal:** In a single filter step, enforce both a minimum length requirement and an N-run limit.

**Page:** Sequence Refinery

**Step-by-step:**
1. Navigate to **Sequence Refinery**.
2. Set **Min Sequence Length** to **1500**.
3. Set **Max N-Run Length** to **30**.
4. Click **Apply Quality Filter** once. Both thresholds are applied together in a single pass.
5. Read the green success message and the updated sidebar sequence count.
6. Navigate to **Analytics** and generate a chart of sequence lengths (use the Violin/Box chart type if available) to confirm the distribution now starts at 1,500 bp.

**Expected result:** The active dataset contains only sequences that are at least 1,500 bp long AND have no N-run exceeding 30 characters. The sidebar count will reflect any sequences removed.

**Tip for beginners:** Applying both criteria at once is more efficient than running two separate filters. The app processes both conditions in a single pass so you do not double-count any removals.

---

## Use Case 12: Remove Exact Duplicate Sequences (Basic Deduplication)

**Goal:** Identify and remove sequences that have identical nucleotide content, keeping only one representative of each.

**Page:** Sequence Refinery

**Step-by-step:**
1. Navigate to **Sequence Refinery** and find the **Deduplication** sub-section inside **Basic Operations**.
2. Click the **Deduplicate (Sequence Only)** button.
3. A spinner reads "Running basic deduplication..." followed by a success message.
4. Compare the **Active Sequences** count in the sidebar before and after. The difference is the number of duplicate sequences removed.

**Expected result:** If HA_test_copy1.fasta contains any sequences with identical nucleotide strings (even if their headers are different), only the first occurrence of each is retained. For a well-curated GISAID export, duplicates may be rare or absent.

**Tip for beginners:** Two sequences can be duplicates in terms of nucleotide content even if they have different isolate names or accession numbers. This can happen when the same sample is submitted twice to a database under different IDs. Basic deduplication catches these cases.

---

## Use Case 13: Remove Duplicates While Preserving Subtype Diversity (Advanced Deduplication)

**Goal:** Remove identical sequences but ensure that if the same nucleotide sequence appears under two different subtypes, one representative of each subtype is kept.

**Page:** Sequence Refinery

**Step-by-step:**
1. Navigate to **Sequence Refinery**, **Basic Operations** section.
2. Click **Deduplicate (Sequence + Subtype)**.
3. A spinner reads "Running advanced deduplication..." followed by a confirmation.
4. Check the updated sequence count in the sidebar.

**Expected result:** Sequences that are identical in nucleotide content AND subtype are reduced to one representative. Since HA_test_copy1.fasta contains only H3N2, this will behave identically to basic deduplication in this specific dataset. The advanced option is most useful when analyzing multi-subtype files.

**Tip for beginners:** Use Advanced Deduplication when your dataset mixes multiple subtypes (e.g., H1N1 and H3N2) and you want to avoid discarding a sequence just because its nucleotides happen to match a sequence from a different subtype.

---

## Use Case 14: Identify Outlier Sequences by Length Before Filtering

**Goal:** Visualize the distribution of sequence lengths to find outliers before deciding on a filter threshold.

**Page:** Analytics

**Step-by-step:**
1. Activate the dataset and navigate to **Analytics**.
2. Locate the chart-type selection area. Select **Violin/Box** chart type.
3. Set the field to **Segment** or leave it on default.
4. Click **Generate Chart** (or the equivalent button).
5. The violin/box plot will display the distribution of sequence lengths. Look for points plotted far outside the main body of the violin — these are outliers.
6. Note the minimum and maximum lengths shown on the y-axis.
7. Use those values to set informed thresholds in the **Min Sequence Length** slider on **Sequence Refinery**.

**Expected result:** You can see that most HA_test_copy1.fasta sequences cluster tightly around 1,695–1,701 bp with very little spread. Any sequence plotted well below 1,650 bp warrants investigation.

**Tip for beginners:** The violin plot is like a sideways histogram. A wider section of the violin means more sequences have that length. A thin "tail" pointing downward indicates a small number of unusually short sequences — the outliers you want to investigate.

---

## Use Case 15: Reset All Filters and Restore the Original Dataset

**Goal:** Undo all filtering steps and return the active dataset to its original state without re-uploading the file.

**Page:** Any (sidebar Reset button)

**Step-by-step:**
1. At any point after applying filters, look at the sidebar **Quick Actions** section.
2. Click the **Reset All Data** button (shown with a circular arrow icon).
3. A spinner appears with the message "Resetting session..."
4. After a moment, a toast confirms "Session Reset!" and the page reloads.
5. Go to **Workspace** and re-activate HA_test_copy1.fasta (you will need to re-upload it since the reset clears all session data, including uploaded files).
6. Alternatively, if you want to keep the file loaded but restore only the sequences to pre-filter state, use the **Data Mode** toggle in the sidebar: switch from **Current (Filtered)** to **Original (Pre-Filter)**.

**Expected result:** After a full reset, the sidebar shows no active sequences and no files loaded. After switching Data Mode to **Original (Pre-Filter)**, the full unfiltered sequence count is restored without re-uploading.

**Tip for beginners:** The **Data Mode: Original (Pre-Filter)** toggle is the faster option if you just want to go back one step. The full Reset is for starting completely fresh. Always export your results before resetting, because the reset cannot be undone.

---

## Category 3: Metadata and Header Filtering (Use Cases 16–23)

---

## Use Case 16: Filter to Only H3N2 Sequences

**Goal:** Isolate only sequences annotated as H3N2 subtype from the active dataset.

**Page:** Sequence Refinery

**Step-by-step:**
1. Navigate to **Sequence Refinery** and find the **Subtype Operations** section.
2. You will see a dropdown labelled **Select Subtype** containing all subtypes found in the active dataset, plus "All" at the top.
3. Click the dropdown and select **A_/_H3N2** (which is how the subtype appears after parsing the pipe-separated header).
4. Leave the **Custom (comma-sep):** text box empty.
5. Click **Filter by Subtype**.
6. A spinner reads "Filtering by subtype..." followed by a confirmation.

**Expected result:** Since HA_test_copy1.fasta contains only H3N2 sequences, the count should remain the same. This use case is most instructive as a verification step — confirming that the dataset is indeed a pure H3N2 collection.

**Tip for beginners:** In a mixed dataset containing H1N1, H3N2, and H5N1, this same procedure would reduce the active sequences to only those matching your chosen subtype. The custom text box lets you filter for multiple subtypes at once by typing them comma-separated, e.g., `H3N2, H1N1`.

---

## Use Case 17: Filter by Clade — Keep Only 3C.2a1b Sequences

**Goal:** Narrow the dataset to a single phylogenetic sub-lineage for focused analysis.

**Page:** Sequence Refinery

**Step-by-step:**
1. Navigate to **Sequence Refinery** and scroll to the **Clade-Based Monthly Filter** section.
2. Look for the **Mode** radio buttons and select **Single Clade**.
3. A dropdown labelled **Select Clade:** will appear. Click it to see all clades found in the active dataset.
4. Select the clade that begins with **3C.2a1b** (choose the most specific sub-clade you want; for a broad filter, select the parent).
5. In the **Keep per Month:** dropdown, choose **Both (First & Last)** to keep at least two representatives per month.
6. Click **Apply Clade Monthly Filter**.
7. The spinner reads "Applying clade monthly filter..." and the sidebar count updates.

**Expected result:** Only sequences belonging to the selected `3C.2a1b` branch are retained, with at minimum one early-month and one late-month representative per calendar month.

**Tip for beginners:** "3C.2a1b" is a major branch of H3N2 viruses that has been dominant globally since approximately 2019. Filtering to this clade lets you study the evolution of this specific lineage without sequences from older or divergent branches contaminating your analysis.

---

## Use Case 18: Filter by Date Range — January to June 2024

**Goal:** Keep only sequences collected in the first half of 2024.

**Page:** Sequence Refinery

**Step-by-step:**
1. Navigate to **Sequence Refinery** and go to the **Enhanced Temporal Diversity Filter** section.
2. In the **Group By** dropdown, select **No Grouping**. This will apply temporal filtering without splitting by host or location.
3. In the **Sort By** dropdown, select **Collection Date**.
4. In the **Keep per Group:** dropdown, select **Both (First & Last)** to keep representative sequences.
5. After applying the temporal filter, use the **Filter by EPI_ISL Accessions** section to verify dates, or proceed to the **Analytics** page and generate a **Temporal (Monthly)** line chart to visually confirm all remaining dates fall within January–June 2024.
6. For precise date-range filtering, use the **Split & Export by Metadata** feature on Sequence Refinery: set **Split Dataset By: Month**, click **Preview Split**, and then download only the months you want (January = `2024-01`, February = `2024-02`, etc.).

**Expected result:** After splitting by Month and downloading only months 2024-01 through 2024-06, you have a FASTA file containing only sequences from the first half of 2024.

**Tip for beginners:** Vir-Seq-Sift's Temporal filter works best for intelligent sub-sampling. For a hard date-range cut, the Split by Month approach combined with selective download gives you exact control.

---

## Use Case 19: Filter by Segment — Keep Only HA Sequences

**Goal:** In a multi-segment dataset, isolate only the HA (hemagglutinin) segment.

**Page:** Sequence Refinery

**Step-by-step:**
1. Navigate to **Sequence Refinery**, **Subtype Operations** section.
2. Instead of the Subtype dropdown, go to **Custom (comma-sep):** and note that the subtype filter applies to the `type` field. For segment filtering, use the **Split & Export by Metadata** feature.
3. Scroll to the **Split & Export by Metadata** section on Sequence Refinery.
4. In the **Split Dataset By:** dropdown, select **Segment**.
5. Click **Preview Split** to see how many files would be created and how many sequences each segment contains.
6. In the individual download buttons that appear (or the ZIP), click the button labelled **HA (N seqs)** to download only the HA sequences.

**Expected result:** A separate FASTA file containing only HA-segment sequences is downloaded. For HA_test_copy1.fasta, all sequences should be HA, so the downloaded file will be identical to the original in content.

**Tip for beginners:** This workflow is most valuable when analyzing whole-genome sequencing datasets that contain all eight influenza segments (PB2, PB1, PA, HA, NP, NA, M, NS) in a single FASTA file.

---

## Use Case 20: Filter by Location — Keep Only Novosibirsk Sequences

**Goal:** Confirm that all sequences in the dataset originate from Novosibirsk and demonstrate location-based filtering.

**Page:** Sequence Refinery

**Step-by-step:**
1. Navigate to **Sequence Refinery**, **Split & Export by Metadata** section.
2. Set **Split Dataset By:** to **Location**.
3. Click **Preview Split**. A table will appear listing each unique location and the number of sequences from that location.
4. For HA_test_copy1.fasta, you should see only one location entry: **Novosibirsk** (or **Russia** depending on how the location field was parsed from the header).
5. Click the download button for the Novosibirsk entry to get a FASTA file with only those sequences.
6. Alternatively, use the **Enhanced Temporal Diversity Filter** with **Group By: Location** to sub-sample sequences per location.

**Expected result:** The location filter confirms a single geographic origin for this dataset. For a mixed dataset from multiple Russian cities, this step would let you isolate Novosibirsk sequences specifically.

**Tip for beginners:** Location data is parsed from the sequence name field (Field 1 in the header, e.g., `A/Novosibirsk/RII-7.429/2024`). The parser extracts the second component (between slashes) as the location. This is standard WHO nomenclature for influenza isolate names.

---

## Use Case 21: Filter by a Specific EPI_ISL Accession Number

**Goal:** Retrieve exactly one sequence from the dataset by its GISAID accession number.

**Page:** Sequence Refinery

**Step-by-step:**
1. Navigate to **Sequence Refinery** and scroll to the **Filter by EPI_ISL Accessions** section.
2. Confirm that the **Input Method** radio is set to **Text Input**.
3. In the text area labelled **Enter EPI_ISL accessions (any format):** type the accession number, for example:
   ```
   EPI_ISL_19324838
   ```
4. The **Potential Matches** metric box to the right will immediately show the number of matching sequences found (should be 1).
5. Click the **Filter Sequences by Accessions** button.
6. A green success box reports: "Found 1 sequences" and "Matched: 1 / 1 accessions."
7. Navigate to **Export** to download the single-sequence FASTA.

**Expected result:** The active dataset is reduced to exactly one sequence: the isolate with accession EPI_ISL_19324838. The Export page download button will reflect 1 sequence.

**Tip for beginners:** You can paste a list of many accession numbers at once — one per line, or comma-separated. The filter will find all matching sequences simultaneously. This is useful when a collaborator sends you a list of accessions they want analyzed.

---

## Use Case 22: Filter by Multiple EPI_ISL Accessions from a File

**Goal:** Retrieve a specific set of sequences using a plain-text file containing accession numbers.

**Page:** Sequence Refinery

**Step-by-step:**
1. Create a plain text file on your computer (e.g., `my_accessions.txt`) and put several EPI_ISL accession numbers from HA_test_copy1.fasta in it, one per line.
2. Navigate to **Sequence Refinery**, **Filter by EPI_ISL Accessions** section.
3. Click the **Input Method** radio option **Upload File**.
4. A file upload widget appears labelled **Upload text file with EPI_ISL accessions:**. Click it and select your `my_accessions.txt` file.
5. A green success message confirms how many unique accessions were loaded: "Loaded N unique accessions from file."
6. An expandable preview shows the first 20 accessions read from the file.
7. Click **Filter Sequences by Accessions**.
8. The active dataset shrinks to include only those sequences.

**Expected result:** The active dataset contains exactly the sequences corresponding to your accession list. The success message reports how many were found versus how many you searched for.

**Tip for beginners:** The file parser is flexible. Accession numbers can be separated by newlines, commas, spaces, or any combination. You can even copy-paste a column from an Excel spreadsheet into a `.txt` file and it will work.

---

## Use Case 23: Extract All EPI_ISL Accession Numbers from the Active Dataset

**Goal:** Generate a text list of all GISAID accession numbers present in the current active sequences for reporting or cross-referencing.

**Page:** Sequence Refinery

**Step-by-step:**
1. Ensure the dataset is activated. Navigate to **Sequence Refinery**.
2. Scroll to the **Extract EPI_ISL Accessions** section (below the Temporal filter area).
3. Click the **Extract EPI_ISL Accessions** button.
4. A preview text box appears showing the first 20 accessions found, formatted as:
   ```
   EPI_ISL_19324838
   EPI_ISL_19324839
   ...
   ```
5. A success message confirms: "Found N accessions. Download available in Export & Reports."
6. Click the navigation button **Go to Export** or switch to the **Export** page manually.
7. On Export, click the **Download Extracted Accessions (N IDs)** button to save the full list as a `.txt` file.

**Expected result:** A text file is downloaded containing all EPI_ISL accession numbers found in the active dataset, one per line.

**Tip for beginners:** This accession list is extremely useful for sharing with collaborators or for submitting a data request to GISAID to download additional sequences related to your cohort. You can also use it to track provenance — which sequences from a larger database contributed to your final analysis.

---

## Category 4: Visualization and Analytics (Use Cases 24–35)

---

## Use Case 24: Generate a Bar Chart of Clade Distribution

**Goal:** Create a horizontal bar chart showing how many sequences belong to each phylogenetic clade.

**Page:** Analytics

**Step-by-step:**
1. Activate the dataset and navigate to **Analytics**.
2. In the **Advanced Distribution Viewer** expander (which opens by default), find the **Chart Type** dropdown.
3. Select **Bar Chart (Single Category)**.
4. In the **Field to Visualize:** dropdown, select **Clade**.
5. Click the **Generate Chart** button (shown with a chart icon).
6. A spinner reads "Generating chart..." and the chart appears below the controls.
7. The chart shows clades on the y-axis and sequence counts on the x-axis, sorted by count in ascending order.

**Expected result:** You see a horizontal bar chart with clade labels like `3C.2a1b.2a.2a.3a.1` on the y-axis and their respective sequence counts on the x-axis. The dominant clade has the longest bar.

**Tip for beginners:** Bar charts are better than pie charts when you have many categories (more than 5–6 clades). The horizontal layout makes long clade names readable without truncation.

---

## Use Case 25: Generate a Pie Chart of Subtype Distribution

**Goal:** Create a pie chart to confirm that 100% of sequences are H3N2.

**Page:** Analytics

**Step-by-step:**
1. Navigate to **Analytics**.
2. Set **Chart Type** to **Pie Chart (Single Category)**.
3. Set **Field to Visualize:** to **Subtype**.
4. Click **Generate Chart**.
5. A pie chart appears. Each slice represents one subtype with its percentage label shown inside the slice.
6. For HA_test_copy1.fasta, the entire pie should be one color labeled `A_/_H3N2` at 100%.

**Expected result:** A single-slice pie chart confirming all sequences are H3N2.

**Tip for beginners:** Click any slice in the pie chart to highlight it. You can also click a legend label to temporarily hide that slice, which is useful when one dominant category overwhelms smaller slices.

---

## Use Case 26: Generate a Monthly Temporal Chart (Epidemic Curve)

**Goal:** Plot the number of new sequences collected per month throughout 2024 to visualize the epidemic curve.

**Page:** Analytics

**Step-by-step:**
1. Navigate to **Analytics**.
2. Set **Chart Type** to **Line Chart (Temporal)**.
3. Set **Time Interval:** to **Monthly**.
4. Click **Generate Chart**.
5. A line chart appears with months on the x-axis (e.g., 2024-01, 2024-02, ...) and sequence counts on the y-axis.
6. Data point labels appear above each marker showing the exact count for that month.

**Expected result:** The epidemic curve for HA_test_copy1.fasta shows peaks in certain months of 2024. Influenza typically shows a winter peak (January–March in Siberia), so you should see higher counts in those months.

**Tip for beginners:** This chart is the standard epidemiological "epidemic curve" (epi-curve). Each point represents how many new cases (sequences) were collected in that month. A sharp peak indicates an outbreak peak; a gradual decline afterward is the expected post-peak pattern.

---

## Use Case 27: Generate a Quarterly Temporal Chart

**Goal:** Aggregate the monthly sequence counts into quarters to see the seasonal pattern more clearly.

**Page:** Analytics

**Step-by-step:**
1. Navigate to **Analytics**.
2. Set **Chart Type** to **Line Chart (Temporal)**.
3. Set **Time Interval:** to **Quarterly**.
4. Click **Generate Chart**.
5. The x-axis now shows quarters: 2024Q1, 2024Q2, 2024Q3, 2024Q4.
6. Compare this with the monthly chart from Use Case 26 to see which resolution is clearer for your data.

**Expected result:** Quarterly aggregation reveals the seasonal pattern at a coarser level. Q1 (January–March) should have the highest count for Novosibirsk, consistent with Northern Hemisphere influenza seasonality.

**Tip for beginners:** Quarterly charts are useful in presentations or reports where you want to communicate trends without overwhelming the audience with month-by-month detail.

---

## Use Case 28: Generate a Stacked Bar Chart (Cross-Tab Analysis)

**Goal:** Visualize how clades are distributed across different months to see whether clade proportions shift over time.

**Page:** Analytics

**Step-by-step:**
1. Navigate to **Analytics**, **Advanced Distribution Viewer**.
2. Set **Chart Type** to **Stacked Bar (Two Categories)**.
3. In **Primary Category (X-axis/Groups):** select **Month (YYYY-MM)**.
4. In **Secondary Category (Stack/Color):** select **Clade**.
5. Set the **Top N** slider to 10 (to limit to the 10 most common months).
6. Click **Generate Chart**.
7. A stacked bar chart appears where each bar represents one month, and each colored segment within the bar represents a different clade.

**Expected result:** You can see at a glance whether the clade `3C.2a1b.2a.2a.3a.1` was dominant throughout 2024 or whether other clades had a larger presence at certain time points.

**Tip for beginners:** Stacked bars are powerful for showing composition change over time. If all bars have the same color distribution, the clade proportions are stable. If one clade "grows" from bottom to top across months, it may be indicating a lineage replacement event.

---

## Use Case 29: Generate a Heatmap of Sequence Counts by Location

**Goal:** Create a geographic heatmap showing which locations have the most sequences.

**Page:** Analytics

**Step-by-step:**
1. Navigate to **Analytics**.
2. Set **Chart Type** to **Heatmap (Geographic)**.
3. In **Field to Visualize:** select **Location**.
4. Set the **Top N:** slider to **20** to include the top 20 locations.
5. Click **Generate Chart**.
6. A heatmap appears where rows represent locations and intensity (color) represents sequence count.

**Expected result:** For HA_test_copy1.fasta, only Novosibirsk (or Russia) will appear since all sequences share the same geographic origin. In a multi-location dataset, this chart quickly identifies geographic hotspots.

**Tip for beginners:** Heatmaps are most useful with multi-location datasets. For single-location datasets like this one, use the heatmap to confirm data consistency — if you see unexpected location names, it may indicate a header parsing issue.

---

## Use Case 30: Explore the Sunburst Hierarchy Chart

**Goal:** Visualize the hierarchical relationship between subtypes, clades, and hosts in a nested circle diagram.

**Page:** Analytics

**Step-by-step:**
1. Navigate to **Analytics** and look for the **Sunburst Hierarchy** chart type option.
2. Select **Sunburst Hierarchy** from the chart type selector.
3. Configure the hierarchy levels if prompted (Subtype → Clade is a typical combination).
4. Click **Generate Chart**.
5. The sunburst chart appears as concentric rings. The innermost ring is the top-level grouping (Subtype), and each outer ring is a subdivision.
6. Click any segment in the chart to zoom into that branch.

**Expected result:** A multi-level circle where the center shows `A_/_H3N2` and the surrounding rings show the nested clade hierarchy. Clicking `3C.2a1b` will zoom in to show its sub-clades.

**Tip for beginners:** The sunburst chart is especially useful for understanding the evolutionary hierarchy of your sequences. It visually represents which clades are sub-divisions of which parent clades, similar to a collapsed phylogenetic tree.

---

## Use Case 31: Generate a Treemap Chart

**Goal:** Display the relative proportions of clades as nested rectangles, making it easy to compare sizes visually.

**Page:** Analytics

**Step-by-step:**
1. Navigate to **Analytics**.
2. Select **Treemap** from the chart type selector.
3. Set the primary grouping field to **Clade**.
4. Click **Generate Chart**.
5. A treemap appears where each rectangle represents one clade. Larger rectangles correspond to clades with more sequences.
6. Hover over any rectangle to see the exact count.

**Expected result:** The largest rectangle represents the dominant `3C.2a1b.2a.2a.3a.1` clade. Smaller rectangles represent minor variants. The area of each rectangle is proportional to its sequence count.

**Tip for beginners:** Treemaps are particularly good for comparing many categories simultaneously. If you have 10 clades, it is much easier to compare their sizes in a treemap than in a bar chart where you need to read the axis values carefully.

---

## Use Case 32: Generate a Bubble Timeline Chart

**Goal:** Plot sequences on a time axis where bubble size reflects the number of sequences per time point, giving a visual sense of collection intensity over time.

**Page:** Analytics

**Step-by-step:**
1. Navigate to **Analytics**.
2. Select **Bubble Timeline** from the chart type selector.
3. Choose the time resolution (Monthly is recommended for 2024 data).
4. Click **Generate Chart**.
5. A scatter plot appears with time on the x-axis and bubbles at each time point. Larger bubbles indicate months with more sequences.

**Expected result:** Bubbles appear at each month in 2024 that has at least one sequence. The January–March period should have the largest bubbles for a Siberian influenza dataset.

**Tip for beginners:** The bubble timeline shows the same information as the epidemic curve line chart (Use Case 26) but in a different visual form. Some people find it easier to compare relative sizes using circles than to compare heights of line-chart points.

---

## Use Case 33: Apply a Custom Color Palette to a Chart

**Goal:** Customize the colors of a bar chart to use your institution's brand colors or a colorblind-friendly palette.

**Page:** Analytics

**Step-by-step:**
1. Navigate to **Analytics** and configure any bar chart (e.g., Clade distribution bar chart as in Use Case 24).
2. Before clicking **Generate Chart**, look at the right column of the visualizer controls. Find the **Color Scheme:** dropdown and select a predefined scheme, or proceed to the Custom Palette Studio.
3. To use the Custom Palette Studio: expand the **Custom Palette Studio** section.
4. Set the **Number of Colors** slider to the number of clades you want to color (e.g., 6).
5. Click each **Color N** picker to choose a color. A color wheel/picker will appear.
6. After selecting all colors, click **Apply**.
7. Now click **Generate Chart** in the main controls. The chart will use your custom palette.

**Expected result:** The bar chart renders using your chosen colors instead of the default palette. The colors are applied in order, so Color 1 goes to the largest category, Color 2 to the second-largest, and so on.

**Tip for beginners:** For presentations to mixed audiences, consider using colorblind-friendly palettes. A safe combination is blue (#0077BB) and orange (#EE7733) instead of red/green. Click **DNA Colors** in the Custom Palette Studio for an automatically generated palette derived from the nucleotide composition of your sequences — a creative option for conference posters.

---

## Use Case 34: View the Dataset Overview Gauges

**Goal:** Check the three dataset health metrics (sequence count, average length, completeness percentage) that appear as gauges on the Analytics page.

**Page:** Analytics

**Step-by-step:**
1. Activate the dataset and navigate to **Analytics**.
2. Near the top of the page, before the chart configuration section, look for the **Current Dataset Overview** section.
3. You will see two Plotly indicator charts side by side:
   - Left: **Active Sequences** — a large number showing the total count.
   - Right: **Avg Sequence Length** — a gauge dial showing the mean length in bp against a colored range (green = good, yellow = moderate, red = too short).
4. The gauge needle position relative to the colored zones tells you at a glance whether your sequences are in the expected length range for HA.

**Expected result:** For HA_test_copy1.fasta, the gauge needle should sit in the green zone (around 1,695–1,701 bp), well within the acceptable range for full-length H3N2 HA.

**Tip for beginners:** The red zone on the gauge represents lengths that are unusually short for HA. If the needle is in the red, it is a signal to apply a minimum length filter before proceeding with downstream phylogenetic analysis.

---

## Use Case 35: Generate a Parallel Categories Chart

**Goal:** Explore multi-dimensional relationships between metadata fields — for example, how clades, hosts, and locations co-occur — in a single diagram.

**Page:** Analytics

**Step-by-step:**
1. Navigate to **Analytics**.
2. Select **Parallel Categories** from the chart type selector.
3. If prompted, choose three fields: **Clade**, **Host**, and **Location** as the parallel axes.
4. Click **Generate Chart**.
5. The parallel categories diagram shows lines flowing from one axis to the next. Each line represents a group of sequences sharing the same combination of attribute values.
6. Thicker lines indicate more sequences sharing that combination.

**Expected result:** Since HA_test_copy1.fasta is a homogeneous dataset (all H3N2, HA, human, Novosibirsk), most lines will flow to the same endpoints. In a heterogeneous dataset, the crossing patterns reveal which clades are associated with which hosts and locations.

**Tip for beginners:** Parallel categories charts become most informative when you have diversity in your metadata. This chart is excellent for discovering unexpected co-occurrence patterns, such as a clade that appears predominantly in a particular host species.

---

## Category 5: HITL Phylogenetic Sub-sampling (Use Cases 36–40)

---

## Use Case 36: Sub-sample by Clade — Keep First and Last Sequence Per Month

**Goal:** Reduce a large clade to a temporally representative subset by keeping the earliest and latest-collected sequence from each calendar month.

**Page:** Sequence Refinery

**Step-by-step:**
1. Navigate to **Sequence Refinery**, **Clade-Based Monthly Filter** section.
2. Set **Mode** to **Single Clade**.
3. In **Select Clade:** choose `3C.2a1b.2a.2a.3a.1` (the dominant clade in HA_test_copy1.fasta).
4. In **Keep per Month:** select **Both (First & Last)**.
5. Click **Apply Clade Monthly Filter**.
6. Check the updated sidebar sequence count. It will be significantly smaller than the original.

**Expected result:** For each month that has sequences from the selected clade, only the two sequences with the earliest and latest collection date are retained. If a month had only one sequence, that sequence is kept.

**Tip for beginners:** "First and Last" sub-sampling is a Human-in-the-Loop (HITL) strategy that preserves temporal diversity while dramatically reducing dataset size. Phylogenetic software like IQ-TREE or BEAST can handle smaller datasets more quickly, so this step is often performed before tree-building.

---

## Use Case 37: Sub-sample by Clade — Keep Only the First Sequence Per Month

**Goal:** Create a minimal representative dataset with a single sequence per clade per month, always using the earliest-collected sample.

**Page:** Sequence Refinery

**Step-by-step:**
1. Navigate to **Sequence Refinery**, **Clade-Based Monthly Filter** section.
2. Set **Mode** to **Single Clade**.
3. Select any clade from the **Select Clade:** dropdown.
4. In **Keep per Month:** select **First Only**.
5. Click **Apply Clade Monthly Filter**.
6. Observe the updated count: you will have at most one sequence per calendar month.

**Expected result:** A very sparse but temporally representative dataset. For a full-year 2024 dataset from a single clade, you would end up with at most 12 sequences (one per month).

**Tip for beginners:** "First Only" is useful when you need the smallest possible dataset that still spans the full time range. This is a common requirement for fast preliminary phylogenetic inference where you want to check overall tree topology before committing to a full analysis.

---

## Use Case 38: Sub-sample Multiple Clades Simultaneously

**Goal:** Apply the clade monthly filter to several clades at once, processing each clade independently to preserve per-clade temporal representation.

**Page:** Sequence Refinery

**Step-by-step:**
1. Navigate to **Sequence Refinery**, **Clade-Based Monthly Filter** section.
2. Set **Mode** to **Multiple Clades**.
3. A multi-select box labelled **Select Clades:** appears. Click to select all available clades (or a specific subset).
4. Check the box **Process each selected clade separately** if it is not already checked. This ensures each clade is sub-sampled independently.
5. In **Keep per Month:** select **Both (First & Last)**.
6. Click **Apply Clade Monthly Filter**.

**Expected result:** Each selected clade is independently reduced to at most two representatives per month. The total sequence count is the sum of retained sequences across all clades.

**Tip for beginners:** Processing clades separately (rather than together) means that rare clades are not crowded out by dominant ones. If you have one clade with 100 sequences in January and another with only 3, the "separate" option ensures both get their first-and-last kept, rather than the rare clade losing representation.

---

## Use Case 39: Apply Enhanced Temporal Diversity Filter by Location and Host

**Goal:** Sub-sample the dataset so that each unique location-host combination is represented by at most a few sequences per time period, ensuring geographic and host diversity is preserved.

**Page:** Sequence Refinery

**Step-by-step:**
1. Navigate to **Sequence Refinery**, **Enhanced Temporal Diversity Filter** section.
2. In the **Group By** dropdown, select **Location+Host**.
3. In the **Sort By** dropdown, select **Collection Date**.
4. In the **Keep per Group:** dropdown, select **Both (First & Last)**.
5. Click **Apply Enhanced Temporal Filter**.
6. The sidebar count updates. The resulting dataset has at most two sequences for each unique location-host pairing.

**Expected result:** Since HA_test_copy1.fasta is all from Novosibirsk/human, this will reduce the dataset to at most two sequences (the very first and very last collected across the entire dataset). In a multi-location, multi-host dataset, this step creates a balanced sub-sample.

**Tip for beginners:** The Enhanced Temporal Filter is the most flexible sub-sampling tool in Vir-Seq-Sift. By varying the **Group By** field, you can control what dimension you want represented. "Location+Host+Month+Clade" gives the finest-grained grouping; "No Grouping" treats the entire dataset as one group.

---

## Use Case 40: Use Custom Grouping for Specialized Sub-sampling

**Goal:** Define a completely custom set of metadata fields to group sequences by, for a sub-sampling strategy tailored to your specific research question.

**Page:** Sequence Refinery

**Step-by-step:**
1. Navigate to **Sequence Refinery**, **Enhanced Temporal Diversity Filter** section.
2. In the **Group By** dropdown, select **Custom**.
3. A text box labelled **Custom Grouping Fields (comma-sep):** appears with placeholder text `e.g., location, host`.
4. Type your desired grouping fields separated by commas, for example: `clade, location`
5. In **Sort By**, select **Collection Date**.
6. In **Keep per Group:**, select **First Only**.
7. Click **Apply Enhanced Temporal Filter**.

**Expected result:** The dataset is sub-sampled so that only the earliest-collected sequence for each unique clade-location combination is kept.

**Tip for beginners:** Custom grouping is a power-user feature. Use it when none of the predefined group-by options match your research design. For example, if you are studying spillover events, you might group by `host, clade` to ensure each clade's first detected host-jump event is represented.

---

## Category 6: Export and Reporting (Use Cases 41–47)

---

## Use Case 41: Download the Filtered FASTA File

**Goal:** After applying quality filters and sub-sampling, export the final set of sequences as a FASTA file for use in phylogenetic software.

**Page:** Export

**Step-by-step:**
1. Apply your desired filters on **Sequence Refinery** (e.g., length filter, clade filter, deduplication).
2. Navigate to the **Export** page.
3. In the left column under the **Last Analysis Report** heading, find the large primary-style button labelled **Download Current Active Data (N seqs)**.
4. Click it. Your browser will prompt you to save a file named `active_data_YYYYMMDD_HHMM.fasta`.
5. Save the file to your preferred location.

**Expected result:** A FASTA file is downloaded containing all sequences currently in the active dataset (after all filters). The file name includes a timestamp to help you track versions.

**Tip for beginners:** The sequence count shown in parentheses on the download button tells you exactly how many sequences you are about to export. Always verify this number matches your intention before downloading, especially if you have applied many sequential filters.

---

## Use Case 42: Download the Session Log

**Goal:** Save a complete record of every analysis step performed in this session for reproducibility and documentation.

**Page:** Export

**Step-by-step:**
1. Navigate to the **Export** page.
2. In the right column, find the **Export Logs** section.
3. Click the **Download Full Log** button.
4. A file named `analysis_log_YYYYMMDD_HHMM.txt` is saved.
5. Open the file in any text editor. You will see timestamped entries for each filter, deduplication step, and chart generation performed.

**Expected result:** A text file documenting the entire analysis pipeline: which file was loaded, which filters were applied with what parameters, how many sequences were removed at each step, and timestamps for each operation.

**Tip for beginners:** Keep this log file alongside your downloaded FASTA. Together they form a complete audit trail — you can always recreate your analysis by following the steps recorded in the log. This is important for scientific reproducibility and for manuscript methods sections.

---

## Use Case 43: Download the Analysis Report

**Goal:** Export a human-readable summary report of the most recent analysis operation (e.g., the deduplication run or quality filter result).

**Page:** Export

**Step-by-step:**
1. Run any analysis step that generates a report — for example, click **Apply Quality Filter** or **Deduplicate (Sequence Only)** on **Sequence Refinery**.
2. Navigate to the **Export** page.
3. In the left column under **Last Analysis Report**, a text area will show the report content.
4. Click the **Export Report** button.
5. A `.txt` file named `analysis_report_YYYYMMDD_HHMM.txt` is saved.

**Expected result:** A structured text report describing what the last operation did: for a quality filter, it reports how many sequences were checked, how many were removed, and which criteria were applied.

**Tip for beginners:** The report is overwritten each time you run a new analysis operation. If you want to keep reports from multiple operations, click **Export Report** after each individual step before running the next one.

---

## Use Case 44: Download a ZIP Bundle of All Original Files

**Goal:** Export the original (pre-filter) versions of all loaded files together in a single ZIP archive.

**Page:** Export

**Step-by-step:**
1. Ensure at least one file is loaded (e.g., HA_test_copy1.fasta) and activated.
2. Navigate to the **Export** page.
3. In the left column, look for the button labelled **Download Per-File ZIP (Originals, N files, N seqs)**.
4. Read the caption below it: "Exports pre-filter originals as separate FASTAs in a ZIP — no merging."
5. Click the button. A file named `per_file_originals_YYYYMMDD_HHMM.zip` is saved.
6. Unzip it on your computer. You will find HA_test_copy1.fasta inside.

**Expected result:** A ZIP archive containing the original unfiltered FASTA files as they were when first loaded into Vir-Seq-Sift.

**Tip for beginners:** This download gives you a clean backup of your raw data. It is good practice to save this alongside your filtered exports so you can always refer back to what you started with.

---

## Use Case 45: Split the Dataset by Clade and Download as ZIP

**Goal:** Create a separate FASTA file for each clade in the dataset and download all of them packaged in a single ZIP.

**Page:** Sequence Refinery

**Step-by-step:**
1. Navigate to **Sequence Refinery** and scroll to the **Split & Export by Metadata** section.
2. In the **Split Dataset By:** dropdown, select **Clade**.
3. In **Data Source:**, choose **Current** (to use your filtered dataset).
4. Click **Preview Split**. A table will appear listing each clade name and how many sequences it contains, along with average length.
5. Read the statistics caption: "N groups | N total sequences | Avg N seqs/group."
6. Click the large export button: **Export All as ZIP (N files, N seqs)**.
7. A spinner reads "Creating ZIP archive with N files..." and then a download button appears: **Download ZIP (N files)**.
8. Click it to save the ZIP.

**Expected result:** A ZIP file containing one `.fasta` file per clade, e.g., `clade_3C.2a1b.2a.2a.3a.1.fasta`. Each file contains only the sequences from that clade.

**Tip for beginners:** Splitting by clade is the standard workflow before running separate phylogenetic analyses for each clade. Having one FASTA per clade makes it easy to batch-submit jobs to a computing cluster or phylogenetic web server.

---

## Use Case 46: Download Accession List as Text File

**Goal:** Save the list of EPI_ISL accession numbers extracted from the active dataset as a plain-text file.

**Page:** Export (after extracting accessions on Sequence Refinery)

**Step-by-step:**
1. First, extract accessions: go to **Sequence Refinery**, scroll to **Extract EPI_ISL Accessions**, and click the **Extract EPI_ISL Accessions** button.
2. After extraction, navigate to the **Export** page.
3. In the left column, find the button **Download Extracted Accessions (N IDs)**.
4. Click it to save a file named `extracted_accessions_YYYYMMDD_HHMM.txt`.
5. Open the file. It will contain one EPI_ISL accession per line.

**Expected result:** A plain-text file with all EPI_ISL accession numbers from your current active sequences, one per line. This can be submitted directly to the GISAID EpiFlu download system.

**Tip for beginners:** GISAID allows batch download of sequences using an accession list. By exporting this list from Vir-Seq-Sift, you can easily download additional gene segments (e.g., NA, PB2) for the same isolates, enabling whole-genome analysis of the sequences you have already selected.

---

## Use Case 47: Quick Export from the Sidebar

**Goal:** Download the active FASTA instantly without navigating to the Export page.

**Page:** Any (sidebar Quick Export)

**Step-by-step:**
1. Ensure the dataset is activated and you have applied your desired filters.
2. Look at the left sidebar under **Quick Actions**.
3. Find the button labelled **Quick Export Active FASTA** (shown with a floppy disk icon).
4. Click it. Your browser immediately downloads a file named `quick_export_YYYYMMDD_HHMM.fasta`.

**Expected result:** The active dataset (post-filter) is saved as a FASTA file. This is identical in content to the **Download Current Active Data** button on the Export page but accessible from any tab.

**Tip for beginners:** Use Quick Export when you are mid-workflow and want to save a snapshot of your current state before applying another filter. You can create a series of snapshots at different stages and compare them later.

---

## Category 7: Advanced Combinations (Use Cases 48–55)

---

## Use Case 48: Full Quality-Control Pipeline in One Session

**Goal:** Run a complete QC workflow — upload, activate, filter by length, remove duplicates, check subtypes, and export — without leaving the app.

**Page:** Workspace, Sequence Refinery, Analytics, Export

**Step-by-step:**
1. **Workspace**: Upload HA_test_copy1.fasta and activate it.
2. **Sequence Refinery**: Set **Min Sequence Length** to **1600** and **Max N-Run Length** to **30**. Click **Apply Quality Filter**.
3. **Sequence Refinery**: Click **Deduplicate (Sequence Only)**.
4. **Analytics**: Set Chart Type to **Pie Chart** and Field to **Subtype**. Click **Generate Chart** to confirm 100% H3N2.
5. **Sequence Refinery**: Click **Extract EPI_ISL Accessions**.
6. **Export**: Download the filtered FASTA, the accession list, and the session log.
7. Save all three files to the same folder.

**Expected result:** Three output files: (1) a filtered FASTA with high-quality, deduplicated H3N2 HA sequences; (2) a text file of EPI_ISL accessions; (3) a session log documenting every step. This set of files is ready for submission to phylogenetic analysis tools.

**Tip for beginners:** Following a standardized QC pipeline before every analysis ensures reproducibility. By always running the same steps in the same order, your results will be comparable across different datasets and different sessions.

---

## Use Case 49: Prepare Sequences for Phylogenetic Analysis with Maximum Temporal Diversity

**Goal:** Create a sub-sampled dataset optimized for phylogenetic tree building where every month of 2024 is represented but the total sequence count stays manageable.

**Page:** Sequence Refinery, Export

**Step-by-step:**
1. Activate HA_test_copy1.fasta.
2. **Sequence Refinery**: Apply **Min Sequence Length: 1650** to ensure full-length sequences only.
3. **Sequence Refinery**: Apply **Deduplicate (Sequence Only)** to remove exact duplicates.
4. **Sequence Refinery**: In the **Enhanced Temporal Diversity Filter**, set **Group By: No Grouping**, **Sort By: Collection Date**, **Keep per Group: Both (First & Last)**.
5. Click **Apply Enhanced Temporal Filter**. This reduces the dataset to at most two sequences from the entire collection.
6. Alternatively, for better temporal coverage: set **Group By: Month** (using Custom grouping: `month`) to keep first and last per month.
7. **Export**: Download the filtered FASTA.

**Expected result:** A lean FASTA file with one or two sequences per month, spanning all of 2024. This dataset is small enough for rapid phylogenetic analysis while retaining temporal diversity.

**Tip for beginners:** Most phylogenetic tools (IQ-TREE, FastTree, MEGA) can comfortably handle up to a few hundred sequences. Sub-sampling ensures your tree is interpretable and runs in a reasonable amount of time.

---

## Use Case 50: Compare Clade Proportions Before and After a Date Cutoff

**Goal:** Visually compare the clade composition of the first half of 2024 versus the second half to detect any shift in dominant lineage.

**Page:** Sequence Refinery, Analytics

**Step-by-step:**
1. Activate HA_test_copy1.fasta.
2. **Analytics**: Generate a **Stacked Bar (Two Categories)** chart with **Primary Category: Month** and **Secondary Category: Clade**. Note the clade proportions for each month. Take a screenshot or export the chart.
3. **Sequence Refinery**: Use **Split & Export by Metadata**, split by **Month**, and download months 2024-01 through 2024-06 manually.
4. Upload and activate only the H1 (first-half) file, generate the same stacked bar chart, and compare.
5. Repeat steps 3–4 for months 2024-07 through 2024-12.

**Expected result:** Two charts showing clade composition for H1 and H2 of 2024. Any change in the dominant clade between halves would be visible as a shift in color proportions between the two charts.

**Tip for beginners:** Lineage replacement events in influenza often happen gradually over months. By comparing early-year and late-year clade proportions, you can detect whether a new sub-clade began to dominate during the year.

---

## Use Case 51: Build a Clade-Stratified Export for Multi-Clade Phylogenetic Study

**Goal:** Create separate sub-sampled FASTA files for each clade, with each file containing temporally representative sequences, for multi-clade phylogenetic comparison.

**Page:** Sequence Refinery, Export

**Step-by-step:**
1. Activate HA_test_copy1.fasta.
2. **Sequence Refinery**: Apply quality filters (length ≥ 1600, max N-run ≤ 30).
3. **Sequence Refinery**: Go to **Clade-Based Monthly Filter**, set **Mode: Multiple Clades**, select all clades, check **Process each selected clade separately**, and set **Keep per Month: Both (First & Last)**.
4. Click **Apply Clade Monthly Filter**.
5. **Sequence Refinery**: Go to **Split & Export by Metadata**, set **Split Dataset By: Clade**, click **Preview Split**, and then click the **Export All as ZIP** button.
6. The ZIP contains one FASTA per clade, each already sub-sampled to two sequences per month.

**Expected result:** A ZIP archive with multiple FASTA files — one per clade — where each file contains a temporally representative, quality-filtered subset of sequences for that clade.

**Tip for beginners:** This workflow produces a "gold standard" set of input files for multi-clade phylogenetic analysis. Each clade file can be analyzed separately with a phylogenetic tool, then the trees can be compared side-by-side to understand convergent evolution between lineages.

---

## Use Case 52: Validate Data Integrity After All Filters

**Goal:** After applying a chain of filters, verify that no unexpected sequences slipped through and that the metadata is internally consistent.

**Page:** Analytics, Sequence Refinery

**Step-by-step:**
1. After applying multiple filters, navigate to **Analytics**.
2. Generate four consecutive charts:
   - **Pie Chart** of **Subtype** — all slices should be H3N2.
   - **Bar Chart** of **Segment** — all bars should be HA.
   - **Bar Chart** of **Location** — should show only Novosibirsk.
   - **Line Chart (Temporal)** with Monthly interval — dates should all fall in 2024.
3. Any unexpected entry in any of these charts (e.g., a different subtype, a non-HA segment, a 2023 date) indicates a metadata inconsistency.
4. If inconsistencies are found, return to **Sequence Refinery** and use the accession filter to identify and remove the problematic sequences.

**Expected result:** All four charts show clean, consistent metadata: 100% H3N2, 100% HA, single location, all dates in 2024.

**Tip for beginners:** Data validation is a critical but often overlooked step. Even well-curated databases occasionally contain mislabeled entries. Running these four quick charts takes less than two minutes and could save you from basing your analysis on incorrect data.

---

## Use Case 53: Create a Reproducible Analysis Protocol Document

**Goal:** Document your complete analysis workflow so it can be reproduced by a collaborator using the same FASTA file.

**Page:** Export, Analytics

**Step-by-step:**
1. Perform your full analysis pipeline (upload, quality filter, deduplication, clade filter, sub-sampling, export).
2. After each major step, note the sequence count shown in the sidebar.
3. Navigate to **Export** after completing the full pipeline.
4. Download the **Full Log** (records all steps with parameters and timestamps).
5. Download the **Analysis Report** (summary of the last major operation).
6. In a separate document, write down the sidebar sequence counts at each step, e.g.:
   - After upload: 350 sequences
   - After length filter (≥1600 bp): 348 sequences
   - After deduplication: 342 sequences
   - After clade filter (3C.2a1b, First & Last): 24 sequences
7. Share this document, the log file, and the final FASTA with your collaborator.

**Expected result:** A complete reproducibility package: raw log, summary report, sequence counts at each step, and final filtered FASTA.

**Tip for beginners:** Scientific analysis must be reproducible. The log file captures most details automatically, but writing down the sidebar counts at each step is a human-readable sanity check that even non-programmers can follow.

---

## Use Case 54: Compare Two Datasets Side by Side Using Data Mode Toggle

**Goal:** Use the **Data Mode** toggle to switch between your filtered and original datasets without re-running filters, enabling rapid before/after comparison in charts.

**Page:** Analytics (with Data Mode toggle in sidebar)

**Step-by-step:**
1. Activate HA_test_copy1.fasta and apply a quality filter (e.g., Min Length ≥ 1600).
2. Navigate to **Analytics** and generate a **Bar Chart** of **Clade**. Note the clade counts.
3. In the left sidebar, find the **Data Mode:** radio buttons. Switch from **Current (Filtered)** to **Original (Pre-Filter)**.
4. Return to **Analytics** and regenerate the same **Bar Chart** of **Clade**.
5. Compare the two charts. Any sequence removed by the filter will now be visible in the Original chart.

**Expected result:** The Original chart shows slightly more sequences in each clade bar compared to the Filtered chart. Clades with sequences shorter than 1,600 bp will show a difference.

**Tip for beginners:** The Data Mode toggle is a non-destructive switch. Switching to Original does not remove your filters — they are still stored. Switching back to Current (Filtered) immediately restores your filtered view. This is useful for convincing yourself that a filter is working correctly.

---

## Use Case 55: End-to-End Workflow — From Raw FASTA to Publication-Ready Output

**Goal:** Walk through the complete Vir-Seq-Sift workflow from file upload to a finalized, documented set of output files suitable for a scientific publication.

**Page:** Workspace, Sequence Refinery, Analytics, Export

**Step-by-step:**
1. **Workspace**: Upload HA_test_copy1.fasta. Activate it. Note the initial sequence count in the sidebar.
2. **Observatory**: Record the initial KPI values (sequence count, avg length, clade distribution) as your baseline.
3. **Sequence Refinery — Quality Filter**: Set Min Sequence Length to **1650**, Max N-Run to **20**. Click **Apply Quality Filter**. Record the new count.
4. **Sequence Refinery — Deduplication**: Click **Deduplicate (Sequence Only)**. Record the new count.
5. **Sequence Refinery — HITL Sub-sampling**: In **Clade-Based Monthly Filter**, set Mode to **Multiple Clades**, select all clades, enable **Process each selected clade separately**, set **Keep per Month: Both (First & Last)**. Click **Apply Clade Monthly Filter**. Record final count.
6. **Analytics — Validation**: Generate (a) Pie chart of Subtype, (b) Bar chart of Clade, (c) Monthly Line chart. Confirm all data is consistent with H3N2 HA from Novosibirsk 2024.
7. **Analytics — Publication Figure**: Generate a **Stacked Bar (Two Categories)** chart (Month × Clade) with a custom color scheme. Use this figure in your methods section.
8. **Sequence Refinery — Accessions**: Click **Extract EPI_ISL Accessions**.
9. **Export**: Download (a) filtered FASTA, (b) accession list, (c) session log, (d) analysis report.
10. Save all outputs to a dated project folder.

**Expected result:** A complete set of publication-ready outputs: (1) a quality-filtered, deduplicated, sub-sampled FASTA file for phylogenetic analysis; (2) an accession list for data availability statements; (3) a session log for methods documentation; (4) a chart for the results figure; (5) a report for the methods section. This represents a full, reproducible influenza surveillance analysis using Vir-Seq-Sift v2.1.

**Tip for beginners:** Congratulations — you have completed the full Vir-Seq-Sift workflow. Each output file serves a specific purpose in a scientific publication: the FASTA feeds your phylogenetic analysis, the accession list goes into your data availability statement, the log becomes your supplementary methods, and the charts become your figures. Vir-Seq-Sift is designed so that a single session produces everything you need.

---

## Category 8: RSV, Avian Flu, Multi-Virus & Molecular Timeline (Use Cases 56–70)

---

## Use Case 56: Load and Analyze RSV-A FASTA Data

**Goal:** Upload an RSV-A dataset and verify the parser handles RSV headers correctly.

**Page:** Workspace

**Step-by-step:**
1. Prepare an RSV-A FASTA file. RSV headers follow this format:
   ```
   >RSV-A/US/VIDRL-2021-10945/2021|RSV-A|G|2021-03-15|EPI_ISL_123456|GA2.3.5
   ```
2. The fields mean: strain name | type | gene segment | date | accession | genotype.
   - Gene segment `G` = attachment glycoprotein; `F` = fusion protein.
   - Genotype `GA2.3.5` indicates an RSV-A genotype in the GA2.3 lineage; RSV-B genotypes use `GB` prefix.
3. Upload the file via **Workspace** exactly as described in Use Case 1.
4. After activation, open the preview table in Workspace. Confirm the **Subtype** column reads `RSV-A`, the **Segment** column reads `G`, and the **Accession** column contains valid EPI_ISL values.
5. Navigate to **Observatory** and check the KPI cards. The **Avg Length** card should show approximately 900 bp for G-gene sequences.

**Expected result:** The preview table displays all RSV-A header fields correctly parsed. The Observatory clade distribution chart shows RSV genotype labels (GA2.x.x format) rather than influenza-style HxNx clade names.

**Tip for beginners:** RSV genotypes use GA/GB (A subtypes) or GB (B subtypes) format, which is completely different from influenza's HxNx notation. Do not be surprised if the clade distribution panel shows unfamiliar labels — they are correct for RSV.

---

## Use Case 57: Filter RSV-A vs RSV-B Sequences

**Goal:** In a mixed RSV dataset containing both RSV-A and RSV-B sequences, isolate only RSV-A.

**Page:** Sequence Refinery

**Step-by-step:**
1. Upload and activate a combined RSV-A/RSV-B FASTA file. The Observatory KPI cards will show a total count combining both types.
2. Navigate to **Sequence Refinery**, **Subtype Operations** section.
3. In the **Select Subtype** dropdown, choose **RSV-A**.
4. Click **Filter by Subtype**.
5. Confirm the sidebar **Active Sequences** count has dropped to reflect only RSV-A sequences.
6. Navigate to **Analytics** and generate a **Pie Chart** of **Subtype** to verify 100% RSV-A.

**Expected result:** The active dataset contains only RSV-A sequences. The pie chart shows a single slice labeled RSV-A.

**Tip for beginners:** RSV-A and RSV-B are distinct subtypes with different seasonal dynamics. RSV-A tends to predominate in early winter while RSV-B often surges in late winter. Analyzing them separately reveals subtype-specific patterns. Mixing them in a single phylogenetic analysis would produce a meaningless tree because the two subtypes diverged decades ago.

---

## Use Case 58: Set Correct Length Thresholds for RSV Genome

**Goal:** Apply a quality length filter appropriate for RSV — the correct threshold differs significantly from influenza HA.

**Page:** Sequence Refinery

**Step-by-step:**
1. Activate your RSV FASTA file and navigate to **Sequence Refinery**.
2. Before setting a threshold, go to **Analytics** and generate a **Violin/Box** chart to inspect your actual sequence length distribution.
3. Return to **Sequence Refinery**, **Quality Filter** section.
4. For **G-gene sequences** (~900 bp full length): set **Min Sequence Length** to **800**.
5. For **F-gene sequences** (~1,700 bp full length): set **Min Sequence Length** to **1,500**.
6. For **full RSV genome sequences** (~15,200 bp): set **Min Sequence Length** to **14,000**.
7. Click **Apply Quality Filter** and verify the sidebar count.

**Expected result:** Sequences shorter than your chosen threshold are removed. For a clean G-gene dataset, virtually all sequences should pass the 800 bp threshold; fragments under 800 bp are likely partial amplicons unsuitable for genotyping.

**Tip for beginners:** Always check what gene or segment your RSV sequences represent before setting a length threshold. Using an influenza HA threshold (1,600 bp) on RSV G-gene sequences (which are legitimately only ~900 bp) would incorrectly discard all of your data. The Violin chart in Analytics is the fastest way to determine what length range is appropriate for your specific dataset.

---

## Use Case 59: Analyze Avian Influenza (H5N1) Header Structure

**Goal:** Understand how Vir-Seq-Sift parses avian influenza headers and correctly identifies the host field.

**Page:** Workspace

**Step-by-step:**
1. Prepare a small avian influenza FASTA file. Avian H5N1 headers follow this format:
   ```
   >A/duck/Novosibirsk/12345/2024|A_/_H5N1|HA|2024-03-10|EPI_ISL_987654|
   ```
2. Upload and activate the file via **Workspace**.
3. In the **Preview: Selected Files** table, examine the **Host** column. The parser infers host from keywords in the strain name field.
4. The keyword `duck` maps to host = `Avian`. Other avian host keywords recognized by the parser include: `goose`, `chicken`, `swan`, `gull`, `teal`, `quail`, `pheasant`, `turkey`, `wild bird`.
5. The keyword `human` (or an absence of a recognized animal keyword) maps to host = `Human`. `swine` or `pig` maps to host = `Swine`.
6. Navigate to **Observatory** and check the KPI cards. A clade field that is blank or shows "Unknown" is normal for newly submitted avian sequences that have not yet been assigned to a clade.

**Expected result:** The preview table shows the **Host** column correctly populated as `Avian` for duck-origin sequences. The **Subtype** column shows `A_/_H5N1`.

**Tip for beginners:** The host inference step is automatic and keyword-based. If your avian sequences use an unusual host name (e.g., `mallard` instead of `duck`), the parser may not recognize it and will assign `Unknown`. In that case, use the header converter tool in Workspace to standardize the host field before activating the dataset.

---

## Use Case 60: Filter to Only Human Influenza (Exclude Avian and Swine)

**Goal:** In a mixed zoonotic surveillance dataset containing human, avian, and swine influenza sequences, keep only sequences from human hosts.

**Page:** Sequence Refinery

**Step-by-step:**
1. Upload and activate a mixed-host influenza FASTA file. The Observatory will show sequences from multiple host types.
2. Navigate to **Sequence Refinery** and find the **Filter Rules** section.
3. Add a filter rule: set **Field** = `host`, **Operator** = `equals`, **Value** = `human`.
4. Click **Apply Filter Rules**.
5. Verify the sidebar count. Only human-host sequences should remain.
6. Navigate to **Analytics** and generate a **Bar Chart** of **Host** to confirm a single bar labeled `human`.

**Expected result:** The active dataset contains only sequences annotated with host = human. All avian and swine sequences are excluded.

**Tip for beginners:** This filter is critical before phylogenetic analysis. Avian, swine, and human influenza strains have different evolutionary rates and selective pressures. Mixing host types in a single phylogenetic tree produces misleading branch length estimates and incorrect divergence time inferences.

---

## Use Case 61: Track H5N1 Avian-to-Human Spillover Events

**Goal:** Identify any avian H5N1 sequences in your dataset that were collected from human hosts, indicating spillover events.

**Page:** Sequence Refinery + Analytics

**Step-by-step:**
1. Activate a mixed H5N1 dataset containing both avian and human isolates.
2. Navigate to **Sequence Refinery**. Apply the first filter: **Subtype** = `H5N1`. Click **Filter by Subtype**.
3. Stay on **Sequence Refinery** and add a second filter rule: **Field** = `host`, **Operator** = `equals`, **Value** = `human`. Click **Apply Filter Rules**.
4. Check the sidebar count. If it shows 0, no human H5N1 cases are present in your dataset. If it shows any number > 0, these are spillover candidates.
5. Navigate to **Analytics** and generate a **Bubble Timeline** chart at monthly resolution. Look for H5N1 human cases clustering at specific months — temporal clustering can indicate an outbreak.
6. Generate a **Bar Chart** of **Location** to see which geographic areas the spillover cases came from.

**Expected result:** If your dataset contains H5N1 human spillover events, the filtered active dataset will show a small number of sequences with host = human and subtype = H5N1. The Bubble Timeline will reveal whether these occurred as isolated events or in temporal clusters.

**Tip for beginners:** Spillover events in zoonotic data are rare — if your two-step filter returns any results, these sequences are clinically significant and warrant close attention. H5N1 human cases have a case fatality rate exceeding 50% historically. The combination of subtype filter + host filter is the standard surveillance screen for detecting novel zoonotic transmission events.

---

## Use Case 62: Compare Influenza A Subtypes Across Hosts Using Stacked Bar

**Goal:** Visualize which influenza A subtypes circulate in which host species to reveal host-subtype associations.

**Page:** Analytics

**Step-by-step:**
1. Activate a multi-host, multi-subtype influenza A dataset (e.g., a surveillance panel containing H1N1, H3N2, H5N1, H7N9).
2. Navigate to **Analytics**, **Advanced Distribution Viewer**.
3. Set **Chart Type** to **Stacked Bar (Two Categories)**.
4. Set **Primary Category (X-axis/Groups):** to **Host**.
5. Set **Secondary Category (Stack/Color):** to **Subtype**.
6. Set **Top N** to 10.
7. Click **Generate Chart**.
8. Read the chart: each bar represents a host species, and each colored stack within the bar represents a subtype. Bar height reflects total sequences; stack proportions show subtype breakdown.

**Expected result:** The chart reveals host-subtype associations clearly. H3N2 and H1N1 bars will be predominantly under the `Human` host group. H5N1 will be predominantly under `Avian`. Any H5N1 stack appearing in the Human bar represents spillover sequences.

**Tip for beginners:** This visualization is a powerful one-chart summary of a zoonotic surveillance dataset. It immediately answers the question "which viruses are circulating in which animals?" without requiring any filtering. Use it as your first exploratory chart after activating a new multi-host dataset.

---

## Use Case 63: Parse and Analyze Influenza B Sequences

**Goal:** Upload Influenza B FASTA data and understand how Influenza B differs from Influenza A in the app's header parsing and analytics.

**Page:** Workspace + Observatory

**Step-by-step:**
1. Prepare an Influenza B FASTA file. Influenza B headers follow this format:
   ```
   >B/Location/Strain/Year|B_/_Victoria|HA|date|EPI_ISL_xxx|V1A.3a
   ```
2. Upload and activate the file via **Workspace**.
3. In the **Preview: Selected Files** table, confirm the **Subtype** column shows `B_/_Victoria` or `B_/_Yamagata`, not an HxNx format.
4. Navigate to **Observatory**. The clade distribution panel will show Influenza B clade labels (e.g., `V1A.3a`, `V1A.3a.2`, `3Del2017`) instead of influenza A clade notation.
5. Note in the KPI cards: the **Avg Length** for HA should still be approximately 1,700 bp, similar to influenza A HA.

**Expected result:** The app parses Influenza B headers correctly, showing Victoria or Yamagata lineage in the Subtype column and the corresponding B-lineage clade notation in the Clade column.

**Tip for beginners:** Influenza B does not use HxNx subtype notation because it has only one hemagglutinin type. Instead, Influenza B is classified by lineage: Victoria and Yamagata. Yamagata lineage is considered extinct since 2020 (no confirmed detections post-COVID-19 pandemic), so modern surveillance datasets should contain predominantly Victoria lineage sequences. Influenza B does not reassort with Type A, so analyzing B sequences separately from A is standard epidemiological practice.

---

## Use Case 64: Build a Molecular Timeline for Influenza B Victoria Persistence

**Goal:** Track how long a specific Influenza B Victoria clone persisted across two consecutive flu seasons by building a persistence timeline.

**Page:** Molecular Timeline

**Step-by-step:**
1. Activate an Influenza B Victoria dataset spanning at least two winter seasons (e.g., 2022-2023 and 2023-2024).
2. Navigate to **Molecular Timeline**.
3. **Phase 1 — Diagnostics**: Review the diagnostics panel. Note the counts for Total Sequences, Unique Molecular Clones, and Sequences in Duplicate Clusters. Download the cluster summary CSV if you want to inspect individual clone membership.
4. **Phase 2 — Configuration**: Set **Min Cluster Size** to `2` (only track clones that appear at least twice). Set **Representative Selection** to `Highest Quality`.
5. **Phase 3 — Timeline Matrix**: Click **Build Timeline**. The matrix loads with rows = molecular clones and columns = calendar months. Each cell shows whether that clone was detected in that month.
6. Review the matrix for rows that have filled cells in both the 2022-2023 winter column range AND the 2023-2024 winter column range — these represent persistent clones.
7. **Phase 4 — Export**: Download the timeline matrix as CSV and the methodology snapshot as JSON.

**Expected result:** The timeline matrix shows which Influenza B Victoria clones circulated across both seasons. Clones with filled cells in two separate winter periods represent overwintering or re-introduction events.

**Tip for beginners:** Influenza B tends to have lower mutation rates than Influenza A, making inter-season persistence more common. Finding the same clone across two winters is not surprising for B/Victoria — it reflects the lower evolutionary pressure compared to A/H3N2. The Molecular Timeline page makes this kind of multi-season tracking visual and straightforward.

---

## Use Case 65: Build a Molecular Timeline for RSV Overwintering

**Goal:** Determine if the same RSV-A clone circulated in winter 2022-2023 AND winter 2023-2024, a phenomenon known as overwintering.

**Page:** Molecular Timeline

**Step-by-step:**
1. Activate an RSV-A dataset covering at least the period October 2022 through April 2024 (two full RSV seasons).
2. Navigate to **Molecular Timeline**.
3. **Phase 1 — Diagnostics**: Review the panel. For RSV datasets, expect a higher rate of duplicate clusters than influenza because RSV has slower evolution per season. If Unique Clones is much less than Total Sequences, many clones are circulating for extended periods.
4. **Phase 2 — Configuration**: Set **Min Cluster Size** to `3` (track only clones seen at least three times). Set **Representative Selection** to `Earliest` (use the first-detected sequence as the clone representative).
5. **Phase 3 — Timeline Matrix**: Click **Build Timeline**. The matrix will span two years of month columns. Look for rows with cells filled in both the 2022-2023 winter months (October 2022 – April 2023) AND the 2023-2024 winter months (October 2023 – April 2024).
6. Each such row is an overwintering clone — the same molecular sequence was actively circulating in two consecutive RSV seasons.

**Expected result:** The matrix reveals whether any RSV-A clones persisted across the inter-season summer gap. Overwintering events appear as rows with a gap of empty cells in summer months (May–September) flanked by filled cells in both adjacent winters.

**Tip for beginners:** "Overwintering" in RSV means the same molecular clone survived the inter-season period (summer) and re-emerged in the following winter — rare but documented in the literature. Finding overwintering clones in your dataset suggests either true persistence in a reservoir host or continuous low-level transmission that was not sampled during summer. The Molecular Timeline matrix makes this distinction immediately visible.

---

## Use Case 66: Use the Dataset Diagnostics Panel on Molecular Timeline

**Goal:** Understand the Phase 1 diagnostics panel before committing to a timeline build, to ensure your dataset is suitable for persistence analysis.

**Page:** Molecular Timeline

**Step-by-step:**
1. Activate any FASTA dataset and navigate to **Molecular Timeline**.
2. The page opens at Phase 1 automatically. Read each metric in the diagnostics panel:
   - **Total Sequences**: the size of your input dataset.
   - **Unique Molecular Clones**: the number of distinct nucleotide sequences (after exact deduplication). This is the number of rows the timeline matrix will have.
   - **Sequences in Duplicate Clusters**: sequences that share their exact nucleotide string with at least one other sequence. A high percentage here means many clones circulated repeatedly.
3. Click **Download Cluster Summary CSV**. Open the CSV in a spreadsheet tool. Each row is a clone; columns show clone ID, representative sequence accession, cluster size, and date range.
4. If **Unique Molecular Clones ≈ Total Sequences**, there are no duplicate clusters. The timeline matrix will consist almost entirely of single-occurrence rows (clones seen only once), which means there are no persistence events to track.
5. In that case, consider relaxing your quality filters or merging datasets from a wider time window before building the timeline.

**Expected result:** You gain a clear picture of your dataset's clone structure before building the timeline. The cluster summary CSV provides the raw data underlying every row in the future matrix.

**Tip for beginners:** If Unique Clones equals Total Sequences, it means every sequence in your dataset has a unique nucleotide string. No two sequences are identical. In that case the timeline will show only single dots per row with no persistence patterns — the timeline analysis is still valid, but it will not reveal multi-month clone persistence because no clones repeat. This diagnostic panel saves you from investing time in a timeline build that will produce no interpretable persistence signal.

---

## Use Case 67: Export Methodology Snapshot from Molecular Timeline

**Goal:** Save a structured JSON record of your Molecular Timeline curation parameters for inclusion in supplementary materials as proof of reproducibility.

**Page:** Molecular Timeline (Phase 4 export)

**Step-by-step:**
1. Build a complete Molecular Timeline (Phases 1–3) as described in Use Case 64 or 65.
2. Navigate to **Phase 4 — Export** within the Molecular Timeline page.
3. Locate the **Export Methodology Snapshot** button. Click it.
4. A JSON file is downloaded. Open it in any text editor. The file contains:
   - `tool_version`: the Vir-Seq-Sift v2.1 version string.
   - `representative_logic`: the representative selection method you chose (e.g., `Highest Quality` or `Earliest`).
   - `min_cluster_size`: the threshold you set in Phase 2.
   - `input_sequence_count`: total sequences fed into the timeline.
   - `output_clone_count`: number of unique clones retained in the matrix.
   - `compression_percent`: percentage reduction from input to output (how many redundant sequences were collapsed).
   - `build_timestamp`: ISO 8601 date and time of the analysis run.
5. Attach this JSON file to your manuscript's supplementary data as "Molecular Timeline parameters."

**Expected result:** A self-contained JSON file documenting every parameter decision made during your timeline build. Any researcher with the same input FASTA and this JSON can reproduce your exact timeline matrix.

**Tip for beginners:** Journals increasingly require computational reproducibility documentation. The methodology snapshot JSON is designed to satisfy this requirement with zero manual effort on your part — the app generates it automatically from your session parameters. Treat it like a machine-readable methods section.

---

## Use Case 68: Multi-Virus Dataset — Load RSV and Influenza Together

**Goal:** Upload a combined FASTA file containing both RSV and influenza sequences (as produced by a multi-pathogen surveillance panel) and separate them for independent analysis.

**Page:** Workspace + Sequence Refinery

**Step-by-step:**
1. Prepare a combined FASTA file where some sequences have influenza headers (e.g., `>A/City/Strain/2024|A_/_H3N2|HA|...`) and others have RSV headers (e.g., `>RSV-A/City/Strain/2024|RSV-A|G|...`).
2. Upload and activate the combined file via **Workspace**. The Observatory KPI cards will show a mixed subtype count.
3. Navigate to **Sequence Refinery**. Add a filter rule: **Field** = `subtype`, **Operator** = `contains`, **Value** = `H3N2`. Click **Apply Filter Rules**.
4. The active dataset now contains only H3N2 influenza sequences. Proceed to **Analytics** for influenza-specific analysis.
5. To analyze the RSV sequences: reset the filter and apply a new filter rule with **Value** = `RSV-A` or `RSV-B`.

**Expected result:** After applying the subtype-contains filter, the active dataset is reduced to only the matching pathogen's sequences. The sidebar count reflects only the H3N2 (or RSV) sequences.

**Tip for beginners:** Combined datasets are increasingly common with multiplex PCR panels that simultaneously detect and sequence multiple respiratory viruses. Vir-Seq-Sift handles them as long as each sequence has the correct pipe-delimited header. The subtype `contains` filter (rather than `equals`) is more robust when subtype strings vary slightly in formatting between different pathogens in the same file.

---

## Use Case 69: Validate Cyrillic Headers Parse Correctly

**Goal:** Confirm that FASTA files with Russian-language location names written in Cyrillic script parse correctly without character corruption.

**Page:** Workspace (preview table)

**Step-by-step:**
1. Prepare a FASTA file that includes Cyrillic characters in the location field. A correctly formatted Cyrillic header looks like:
   ```
   >A/Новосибирск/RII-7.429/2024|A_/_H3N2|HA|2024-01-17|EPI_ISL_xxx|3C.2a1b
   ```
2. Ensure the file is saved with **UTF-8 encoding** (use Notepad++, VS Code, or any modern text editor and explicitly choose "Save As UTF-8 without BOM").
3. Upload and activate the file via **Workspace**.
4. In the **Preview: Selected Files** table, examine the **Location** column. You should see `Новосибирск` displayed correctly — not `?????` or garbled symbols.
5. Navigate to **Observatory** and check the clade distribution and epidemic curve. All charts should display normally.
6. Navigate to **Analytics** and generate a **Bar Chart** of **Location**. The Cyrillic location name should appear correctly on the axis.

**Expected result:** The **Location** column in the preview table displays `Новосибирск` (or whichever Cyrillic location was in your headers) without any corruption. All downstream charts and filters work normally with the Cyrillic text.

**Tip for beginners:** The app uses explicit UTF-8 encoding throughout all file reading and processing operations. If you see `???` or garbled characters in the Location column, the problem is in the source file's encoding — the file was saved with a non-UTF-8 encoding such as Windows-1251 (common for Russian-language files created on older Windows systems). Re-save the file with explicit UTF-8 encoding using a text editor before uploading. This is a one-time fix and will resolve all character display issues permanently.

---

## Use Case 70: End-to-End RSV Surveillance Analysis — From Upload to Publication-Ready Output

**Goal:** Complete a full surveillance analysis workflow for an RSV-A/B dataset, producing all outputs needed for a WHO-compliant hospital network surveillance report.

**Pages:** Workspace, Sequence Refinery, Molecular Timeline, Analytics, Export

**Step-by-step:**
1. **Workspace**: Upload your RSV FASTA file containing both RSV-A and RSV-B sequences. Activate it. Note the initial sequence count in the sidebar.
2. **Observatory**: Review the KPI cards. Check how RSV-A vs RSV-B sequences are represented in the subtype distribution. Record baseline counts for your methods section.
3. **Sequence Refinery — Quality Filter**: Set **Min Sequence Length** to **800** (appropriate for G-gene sequences). Set **Max N-Run Length** to **20**. Click **Apply Quality Filter**. Record the new count.
4. **Sequence Refinery — Deduplication**: Click **Deduplicate (Sequence Only)** to remove any exact duplicate submissions. Record the count.
5. **Sequence Refinery — Host Filter**: Add a filter rule: **Field** = `host`, **Operator** = `equals`, **Value** = `human`. Click **Apply Filter Rules**. This removes any bat or animal reservoir sequences that may have been included in the dataset, ensuring only human clinical isolates remain.
6. **Molecular Timeline**: Navigate to **Molecular Timeline**. Configure **Min Cluster Size** = `2` and **Representative Selection** = `Highest Quality`. Click **Build Timeline**. Review the matrix for RSV clones persisting across multiple months or seasons. Download the cluster summary CSV and methodology snapshot JSON.
7. **Analytics**: Generate a **Stacked Bar (Two Categories)** chart with **Primary Category** = `Month` and **Secondary Category** = `Subtype`. This shows RSV-A vs RSV-B prevalence month by month — the key figure for seasonal surveillance reports.
8. **Export**: Download (a) filtered FASTA, (b) accession list, (c) session log, (d) analysis report, (e) Molecular Timeline methodology JSON. Package all five files for submission.

**Expected result:** A complete set of publication-ready and reportable outputs: a quality-filtered human-only RSV FASTA, a Molecular Timeline showing clone persistence patterns, a month-by-month subtype prevalence chart, and a full methodology documentation package.

**Tip for beginners:** This workflow is directly applicable to RSV surveillance mandated by WHO for hospital networks. The Stacked Bar chart (Step 7) becomes your Figure 1 in the surveillance bulletin. The Molecular Timeline (Step 6) supports claims about clone persistence in your discussion. The methodology JSON (Step 8) satisfies data transparency requirements for WHO reporting and peer-reviewed publication alike.

---

## Category 9: Sidebar, Language & UI Navigation (Use Cases 71–73)

---

## Use Case 71: Navigate Between Pages Using the Sidebar

**Goal:** Understand how to move between the six Vir-Seq-Sift pages and identify which page you are currently on at a glance.

**Page:** Any (sidebar always visible)

**Step-by-step:**
1. Open the app. The left sidebar shows the **Vir-Seq-Sift logo** at the very top, followed immediately by the **Language** selector.
2. Below the language selector you will find the **Dataset Status** metrics and Quick Actions buttons.
3. At the bottom of the sidebar — separated by a thin horizontal line — is the page navigation list showing all six pages:
   - 🌍 Observatory
   - 📁 Workspace
   - 🔬 Sequence Refinery
   - 🧬 Molecular Timeline
   - 📊 Analytics
   - 📋 Export
4. The page you are currently on is highlighted with a **bright cyan-blue left border** and **bold white text**. This is the active page indicator.
5. All other pages appear in a muted grey color. Hovering over any page link shows a faint blue hover state.
6. Click any page name to navigate to it instantly. The sidebar persists — you never lose your sidebar controls when switching pages.

**Expected result:** Clicking a page link navigates you there immediately. The previously active page loses its highlight; the newly active page gains the cyan border and white bold text.

**Tip for beginners:** The active page highlight is your "you are here" marker. If you ever lose track of which page you are on (especially after following instructions in a tutorial), look at the sidebar nav — the highlighted entry is your current location. The logo and language selector always stay at the very top, above the nav links, so you never have to scroll to find them.

---

## Use Case 72: Switch the Interface Language to Russian

**Goal:** Switch Vir-Seq-Sift's entire user interface to Russian (Cyrillic) mode without losing your loaded data.

**Page:** Any (language selector is always in the sidebar)

**Step-by-step:**
1. Look at the very top of the left sidebar, just below the Vir-Seq-Sift logo. You will see a **Language** dropdown (default: 🇬🇧 English).
2. Click the dropdown and select **🇷🇺 Русский (Russian)**.
3. The page will reload automatically (`st.rerun()`). All visible UI text — button labels, metric names, error messages, dropdown options, chart axis labels, expander titles — switches to Russian.
4. Your loaded dataset, filtered data, and session state are all preserved. The **Active Sequences** metric in the sidebar will still show the same number.
5. Navigate to any page to confirm the localized text appears correctly. Visit **Observatory** and check that the KPI metric labels appear in Russian.
6. To switch back: return to the Language dropdown at the top of the sidebar and select **🇬🇧 English**.

**Expected result:** The full interface renders in Russian after the switch. Data is not lost. Language switching completes in under one second (translations are cached at startup — no file I/O during switching).

**Tip for beginners:** Language switching is non-destructive. Your filters, uploaded files, and active dataset all survive the switch. This is by design: switching from English to Russian during a multi-hour analysis session does not require starting over. The app stores the language setting in session state, so the chosen language persists until you explicitly change it or reset the session.

---

## Use Case 73: Use the Sidebar Quick Actions During Active Analysis

**Goal:** Use the sidebar's Quick Actions section to reset the session or clear all filters without navigating to a separate page.

**Page:** Any (sidebar Quick Actions)

**Step-by-step:**
1. Activate HA_test_copy1.fasta and apply any filter in **Sequence Refinery**.
2. In the left sidebar, scroll to the **Quick Actions** section (below the Dataset Status metrics).
3. If active filters are present, a filter badge appears: "Global Filters (N active)" with a count of the active rules.
4. Click **Clear All Filters** to remove all active filters at once and restore the full active dataset.
5. The sidebar **Active Sequences** count will return to the original pre-filter number.
6. Click **Reset Session** (at the bottom of the Quick Actions section) to completely clear all loaded files, filters, and data. This is equivalent to a fresh browser reload — use it when starting a completely new analysis.

**Expected result:** After clicking Clear All Filters, the filtered dataset resets to match the active dataset. After Reset Session, the sidebar shows "No active dataset loaded" and the Raw Files list is empty.

**Tip for beginners:** Use **Clear All Filters** regularly during exploratory analysis when you want to try a different filter without the previous filter affecting your results. Use **Reset Session** only when you are genuinely starting a new experiment — it cannot be undone without re-uploading your files.

---

## Category 10: Molecular Timeline Advanced Features (Use Cases 74–76)

---

## Use Case 74: Reading the Duplication Burden Chart in Phase 1 Diagnostics

**Goal:** Interpret the horizontal bar chart in the Molecular Timeline diagnostics panel to identify which viral clones are the most persistent (highest duplication burden).

**Page:** Molecular Timeline (Phase 1)

**Step-by-step:**
1. Activate any dataset that contains duplicate sequences (e.g., a multi-season FASTA where the same clone circulated repeatedly).
2. Navigate to **Molecular Timeline**. Phase 1 (Dataset Diagnostics) opens automatically.
3. Below the three KPI metric cards, look for a **Top Persistent Sequence Clusters** section. If any duplicate clusters exist, a horizontal bar chart appears (instead of the old flat table).
4. Each bar represents one molecular clone. The **bar length** corresponds to how many times that clone appears in the dataset.
5. The clone with the longest bar is the most duplicated — the viral sequence that appeared most often across your dataset. This is the primary persistence signal.
6. The bars are colored by cluster size: longer bars (larger clusters) receive a deeper shade of blue. This color gradient makes it immediately obvious which clones dominate the dataset.
7. Hover over any bar to see the exact clone label and count in a tooltip.
8. After inspecting the chart, click **⬇ Download Cluster Summary CSV** to export the full cluster table (including all clusters, not just the top 10 shown in the chart) for detailed inspection in a spreadsheet.

**Expected result:** A horizontal bar chart showing the top 10 clones sorted by cluster size (smallest to largest, reading bottom-to-top). The longest bar is the most persistent clone in your dataset.

**Tip for beginners:** The duplication burden chart is your pre-flight check before building the timeline matrix. A very long top bar means one clone vastly dominates the dataset — this clone will produce a wide row in the Phase 3 matrix spanning many months. Many short bars of similar length means diversity is high and persistence is distributed across many clones rather than concentrated in one.

---

## Use Case 75: Understanding Singleton Pass-Through in the Molecular Timeline Export

**Goal:** Understand how Vir-Seq-Sift handles sequences that are too rare to appear in the timeline matrix (singletons and rare clusters), ensuring they are not silently dropped from your export.

**Page:** Molecular Timeline (Phase 2 config + Phase 4 export)

**Step-by-step:**
1. Activate a dataset and navigate to **Molecular Timeline**.
2. In **Phase 2 — Configuration**, set the **Minimum cluster size** slider to `3`. This means only clones that appear 3 or more times will be shown as rows in the matrix.
3. In **Phase 3 — Timeline Matrix**, the matrix renders. Notice that clones appearing only 1 or 2 times in your dataset are NOT shown — they are "below the threshold."
4. In **Phase 4 — Impact Preview & Export**, click **⚡ Generate Preview & Extract Sequences**.
5. After the preview generates, look for a blue caption below the metrics. It reads something like:
   `↪ 12 singleton/rare sequences (clusters < 5 threshold) auto-included as First+Last anchors.`
   This tells you that 12 sequences from below-threshold clones were automatically added to the export.
6. These singleton sequences are included as First (and Last, if the clone appeared more than once) anchor points — one or two representatives per rare clone.
7. The curated FASTA you download will contain: your selected matrix sequences **plus** these automatically included singletons. No sequences are silently lost.

**Expected result:** The "After" metric count is higher than you might expect if you counted only the matrix checkboxes. The difference represents the singleton/rare-clone pass-through sequences that were auto-included. The blue caption confirms exactly how many were added.

**Tip for beginners:** Without singleton pass-through, raising the minimum cluster size slider would delete all rare sequences from your export — even unique sequences that might represent important early introductions or spillover events. Singleton pass-through ensures that the slider only controls **what you see in the matrix UI**, not what gets exported. Every sequence, no matter how rare, is represented by at least its first occurrence in the final exported FASTA.

---

## Use Case 76: Compare Before and After Epidemic Curves After Timeline Curation

**Goal:** Use the built-in before/after comparison charts in Phase 4 to visually confirm that your Molecular Timeline curation preserved the overall temporal distribution of your dataset.

**Page:** Molecular Timeline (Phase 4)

**Step-by-step:**
1. Build a complete Molecular Timeline (Phases 1–3) using at least a two-season dataset.
2. In **Phase 4 — Impact Preview & Export**, check some boxes in the Phase 3 matrix for the intermediate months between First and Last for your major clones.
3. Click **⚡ Generate Preview & Extract Sequences**.
4. Two columns appear side by side:
   - **Left column — Before (Raw Data):** shows the total sequence count from your original dataset and a grey bar chart of sequence counts per month — this is the raw epidemic curve.
   - **Right column — After (Curated Timeline):** shows the curated count and a blue bar chart of the curated dataset — this is your molecular timeline epidemic curve.
5. Compare the two charts. The curated chart should have far fewer sequences per month (you removed duplicates) but should preserve the same temporal peaks and valleys.
6. If the curated chart loses a month entirely (the bar drops to zero), that month had sequences but none of them matched your minimum cluster threshold OR no boxes were checked for that month. Return to Phase 3 and check the relevant boxes.
7. Below the comparison, review the three metrics: **Compression** (% reduction), **Timeline Coverage** (% of months retained), and **Clones Retained** (unique hashes in the output).

**Expected result:** The "Before" epidemic curve shows the original temporal density of your dataset. The "After" curve shows a leaner version that maintains the same seasonal shape but with significantly fewer sequences per month. A high Coverage percentage (close to 100%) means your curation preserved all time points; a high Compression percentage (e.g., 85%) means you successfully collapsed most redundant sequences.

**Tip for beginners:** A good molecular timeline curation has: **Compression > 60%** (meaningful de-duplication), **Coverage near 100%** (all months represented), and **Delta (After minus Before) shown as negative** (you removed sequences, not added them). If your delta is positive, it means singleton pass-through added more singletons than the matrix removed — common in very diverse datasets with few duplicates.

---

*End of 76 Use Cases — Vir-Seq-Sift v2.1 with HA_test_copy1.fasta*
