# -*- coding: utf-8 -*-
"""
pages/07_📚_Documentation.py — Platform Documentation, FAQ & Use Case Library

Sections:
  • Quick-Start Guide  — 5-step workflow walkthrough
  • Feature Reference  — tab-by-tab capability table
  • Tips & FAQ         — activation, caching, session, large files
  • FASTA Header Format— pipe-delimited field specification & examples
  • Use Case Library   — inline preview + download of usecase.md
"""

import os

import streamlit as st

from utils.minimal_i18n import T

# ─────────────────────────────────────────────────────────────────────────────
# Language-keyed long-form content blocks (avoid 100s of T() JSON keys)
# ─────────────────────────────────────────────────────────────────────────────
_lang = st.session_state.get("lang", st.session_state.get("language", "en"))

_QUICKSTART = {
    "en": """\
### Step 1 — 📁 Upload Your Data
Navigate to **Workspace** in the sidebar. Click *File Upload*, drag-and-drop
your `.fasta`, `.fa`, `.fas`, `.fna`, `.txt`, or `.gz` file, then wait
for the success banner. Your file is now in the session.

### Step 2 — ✅ Activate the Dataset
Scroll down to **Loaded Datasets**. Select your file in the multi-select box,
then click **Activate Selected Files**. The sidebar Quick Stats will update.
> **Nothing works until you activate.**

### Step 3 — 🔬 Filter & Refine
Go to **Sequence Refinery**. Use the quality sliders (min/max length, N-run),
header-component filters (subtype, clade, date, host), and the HITL Smart
Sampler to get a representative phylogenetic subset.

### Step 4 — 📊 Explore & Visualize
Open **Analytics** for 10+ chart types (distribution, temporal, stacked,
epidemic curve, sunburst, treemap, violin, bubble, parallel, Gantt). Use the
**Palette Studio** to customise colours. Visit **Molecular Timeline** for
clone-persistence and overwintering analysis.

### Step 5 — 📋 Export
Go to **Export** to download the final FASTA, a CSV of metadata, a
methodology JSON, or a ZIP bundle of all three. Use *Split & Export* to
create one FASTA file per subtype / clade / host automatically.
""",
    "ru": """\
### Шаг 1 — 📁 Загрузите данные
Перейдите в **Рабочее пространство** на боковой панели. Нажмите *Загрузка
файла*, перетащите `.fasta`, `.fa`, `.gz`, `.txt` или другой поддерживаемый
файл, дождитесь зелёного баннера успеха.

### Шаг 2 — ✅ Активируйте набор данных
Прокрутите до раздела **Загруженные наборы**. Выберите файл в списке,
нажмите **Активировать выбранные файлы**. Панель статистики обновится.
> **Без активации ничего не работает.**

### Шаг 3 — 🔬 Фильтрация и уточнение
Перейдите в **Очиститель последовательностей**. Используйте ползунки качества
(мин./макс. длина, N-серии), фильтры по полям заголовка (субтип, клад, дата,
хозяин) и интеллектуальный сэмплер HITL.

### Шаг 4 — 📊 Анализ и визуализация
Откройте **Аналитику** для 10+ типов диаграмм. Используйте **Студию палитры**
для настройки цветов. В **Молекулярной временной шкале** — анализ устойчивости
клонов и зимовки.

### Шаг 5 — 📋 Экспорт
Перейдите в **Экспорт** для скачивания итогового FASTA, CSV с метаданными,
JSON методологии или ZIP-архива. *Разделить и экспортировать* создаёт один
FASTA-файл на субтип / клад / хозяина автоматически.
""",
}

_FEATURE_TABLE = {
    "en": """\
| Page | Key Actions | Notes |
|------|-------------|-------|
| **📁 Workspace** | File upload, URL download, Google Drive, activate, merge | Activate before any other step |
| **🔬 Sequence Refinery** | Min/max length, N-run filter, deduplication, subtype/clade/date/host/location filters, HITL Smart Sampler | Filtered results flow to all pages |
| **🧬 Molecular Timeline** | Clone persistence matrix, per-month representative selection, dataset diagnostics, methodology snapshot | Needs `sequence_hash` column |
| **📊 Analytics** | 10+ chart types, custom palettes, dataset-overview gauges (count, avg length, completeness) | Use Palette Studio for custom colours |
| **📋 Export** | FASTA, CSV, JSON, ZIP bundle, accession list (.txt), session log, split-by-group export | Always export before closing the browser |
""",
    "ru": """\
| Страница | Ключевые действия | Примечания |
|----------|-------------------|-----------|
| **📁 Рабочее пространство** | Загрузка файла, URL, Google Drive, активация, слияние | Сначала активируйте |
| **🔬 Очиститель последовательностей** | Мин./макс. длина, N-серии, дедупликация, фильтры по субтипу / кладу / дате / хозяину, сэмплер HITL | Результаты отражаются на всех страницах |
| **🧬 Молекулярная временная шкала** | Матрица устойчивости клонов, представители по месяцам, диагностика датасета | Нужен столбец `sequence_hash` |
| **📊 Аналитика** | 10+ типов диаграмм, палитры, датасет-метрики (количество, средняя длина, полнота) | Студия палитры — создание собственных цветов |
| **📋 Экспорт** | FASTA, CSV, JSON, ZIP, список аккессий (.txt), журнал сессии, экспорт по группам | Обязательно экспортируйте перед закрытием браузера |
""",
}

_TIPS_FAQ = {
    "en": """\
### 💡 Tips

| Tip | Detail |
|-----|--------|
| **Activation is Key** | Only sequences from *activated* datasets are used for analysis. Think of it as "loading the experiment." |
| **Large Files** | Processing large files can take time. Watch the progress bar spinners as indicators. The default row limit is 5,000 for some charts — increase via the slider. |
| **Caching** | Parsing is cached per file content hash. Re-uploading the same file is faster on re-run. Clear the cache by resetting the session. |
| **Session Data** | All work lives in your browser session and is lost on tab close or refresh. Use the Export page to save your results *before* closing. |
| **Filtered vs Active** | Most pages prefer the *filtered* dataset if one exists, falling back to the full *active* dataset. The source label shows which is in use. |
| **Language Toggle** | Switch between English and Russian at any time from the sidebar — all labels, buttons, and charts update immediately. |

---

### ❓ Frequently Asked Questions

**Q: My sequences show "Unknown" subtype after upload. Why?**
> The header parser expects pipe-delimited fields matching GISAID's export format. If your headers use a different separator or order, use the *Header Converter* in Sequence Refinery to normalise them first.

**Q: Why is the Molecular Timeline matrix empty?**
> The timeline requires a `sequence_hash` column (added during deduplication in Sequence Refinery) and at least one sequence present in two or more months. Run *Deduplicate* first.

**Q: Analytics charts show "No data." after filtering.**
> The filter may have reduced the dataset to zero sequences. Check the sidebar *Active Sequences* count. Reset filters in Sequence Refinery if needed.

**Q: I uploaded the same file twice — why does it still show two entries?**
> Vir-Seq-Sift detects duplicate filenames and skips re-parsing, but the entry persists in the loaded files list until you remove it. Click *Remove* next to the duplicate in Workspace.

**Q: How do I export per-subtype FASTA files?**
> In the Export page, open *Split & Export*, select **Subtype** as the split field, click *Preview Groups*, then download the ZIP of all sub-FASTAs.

**Q: Can I use VirSift offline?**
> Yes — run `streamlit run app.py` locally after installing requirements. All processing is local; no sequences are ever uploaded to external servers.
""",
    "ru": """\
### 💡 Советы

| Совет | Подробности |
|-------|-------------|
| **Активация — ключ** | Только последовательности из *активированных* наборов участвуют в анализе. |
| **Большие файлы** | Обработка больших файлов занимает время. Следите за полосой прогресса. |
| **Кеширование** | Разбор файла кешируется по хешу содержимого. Повторная загрузка одного файла выполняется быстрее. |
| **Данные сессии** | Все данные хранятся в сессии браузера. Экспортируйте результаты *перед* закрытием вкладки. |
| **Фильтрованный vs активный** | Большинство страниц используют фильтрованный датасет, если он существует, иначе — полный активный. |
| **Переключение языка** | Переключайтесь между English и Русским в любое время из боковой панели. |

---

### ❓ Часто задаваемые вопросы

**В: Субтипы показываются как "Unknown". Почему?**
> Парсер ожидает поля в формате GISAID с вертикальной чертой. Если заголовки другого формата — используйте *Конвертер заголовков* в Очистителе.

**В: Матрица Молекулярной временной шкалы пустая.**
> Требуется столбец `sequence_hash` (добавляется при дедупликации) и хотя бы одна последовательность, встречающаяся в двух и более месяцах. Сначала запустите дедупликацию.

**В: Аналитика показывает "Нет данных" после фильтрации.**
> Фильтрация могла обнулить датасет. Проверьте счётчик *Активных последовательностей* в боковой панели.

**В: Как экспортировать FASTA-файлы по субтипу?**
> В Экспорте откройте *Разделить и экспортировать*, выберите **Субтип**, нажмите *Предпросмотр групп*, затем скачайте ZIP.

**В: Как запустить VirSift локально?**
> Установите зависимости (`pip install -r requirements.txt`) и запустите `streamlit run app.py`. Никакие данные не отправляются на внешние серверы.
""",
}

# ─────────────────────────────────────────────────────────────────────────────
# Header format — three-virus reference (hRSV | Avian Flu | Human Flu)
# ─────────────────────────────────────────────────────────────────────────────
_HEADER_FORMAT = {
    "en": """\
Vir-Seq-Sift supports **GISAID pipe-delimited** headers for three virus groups.
Each group uses a different field count and ordering — choose the one that matches
your GISAID download.

---

## 🫁 Human Respiratory Syncytial Virus (hRSV)

**Header structure:**
```
>Isolate_Name|GISAID_Accession|Collection_Date
```

| # | Field | Example | Format |
|---|-------|---------|--------|
| 1 | **Isolate Name** | `hRSV/B/Argentina/BA-HNRG-206/2016` | hRSV/Subtype/Location/ID/Year |
| 2 | **Accession** | `EPI_ISL_1074181` | EPI_ISL_XXXXXXX |
| 3 | **Collection Date** | `2016-04-18` | YYYY-MM-DD, YYYY-MM, YYYY, or `unknown` |

**Valid hRSV examples:**
```fasta
>hRSV/B/South_Korea/YSU-96B19/un|EPI_ISL_19159645|unknown
>hRSV/A/Argentina/BA-HNRG-206/2016|EPI_ISL_1074181|2016-04-18
>RSV/Human/GBR/2023-001|RSV_A|G|2023-11-04|EPI_ISL_17000001|ON1
```

**GISAID download settings for RSV:**
- FASTA Header field: **Isolate name | Isolate ID | Collection date**
- Date format: YYYY-MM-DD (2009-02-28)
- ☑ Replace spaces with underscores in FASTA header
- ☑ Remove spaces before and after values in FASTA header

---

## 🐦 Avian Influenza

**Header structure:**
```
>Isolate_Name|Virus_Type/Subtype|Gene_Segment|Collection_Date|GISAID_Accession|Clade_Assignment
```

| # | Field | Example | Format |
|---|-------|---------|--------|
| 1 | **Isolate Name** | `A/duck/Bangladesh/33676/2017` | A/Host/Location/ID/Year |
| 2 | **Type / Subtype** | `A_/_H4N6` | `A_/_HxNy` or `A/HxNy` |
| 3 | **Segment** | `PA` | HA, NA, PA, PB1, PB2, NP, MP, NS |
| 4 | **Date** | `2017-09-28` | YYYY-MM-DD, YYYY-MM, YYYY, or unknown |
| 5 | **Accession** | `EPI_ISL_329573` | EPI_ISL_XXXXXXX |
| 6 | **Clade** | `6B.1A.5a.2a.1` | Any format, empty, or `unassigned` |

**Valid avian influenza examples:**
```fasta
>A/duck/Bangladesh/33676/2017|A_/_H4N6|PA|2017-09-28|EPI_ISL_329573|6B.1A.5a.2a.1
>A/duck/Tottori/311018/2015|A_/_H3N6|PA|2015-10-01|EPI_ISL_237156|unassigned
>A/mallard/Republic_of_Georgia/13/2011|A_/_H6N2|PA|2011-11-26|EPI_ISL_189700|
>A/goose/China/1234/2020|A/H5N1|HA|2020-03|EPI_ISL_400001|2.3.4.4h
>A/wild_bird/Japan/567/2019|A_/_H7N9|NA|2019|EPI_ISL_300123|unassigned
```

**GISAID download settings for Avian Influenza:**
- Proteins: select segment (e.g., HA, PA, NP)
- FASTA Header field: **Isolate name | Type | Collection date | Isolate ID | Lineage**
- Date format: YYYY-MM-DD (2009-02-28)
- ☑ Replace spaces with underscores in FASTA header
- ☑ Remove spaces before and after values in FASTA header
- *Note: Add segment name manually or download each segment separately.*

---

## 🦠 Human Influenza

**Header structure:**
```
>Isolate_Name|Virus_Type/Subtype|Gene_Segment|Collection_Date|GISAID_Accession|Clade_Assignment
```

| # | Field | Examples | Notes |
|---|-------|----------|-------|
| 1 | **Strain name** | `A/Novosibirsk/RII-7.429/2024` · `B/Victoria/2/1987` | Full GISAID-style isolate name |
| 2 | **Type / Subtype** | `A/_H3N2` · `A/_H1N1` · `B` | Flu A uses `A/_HxNx`; Flu B has no subtype — write `B` |
| 3 | **Segment** | `HA` · `NA` · `NP` · `MP` · `PA` | Any of the 8 influenza gene segments |
| 4 | **Collection date** | `2024-01-17` · `2009-04-09` · `1987` | ISO 8601 preferred; year-only (`YYYY`) also accepted |
| 5 | **Accession** | `EPI_ISL_19324838` · `EPI_ISL19324838` | With or without underscore between ISL and digits — both parsed |
| 6 | **Clade** | `3C.2a1b.2a.2a.3a.1` · `V1A.3a.2` · `6B.1A` | Nextclade / GISAID phylogenetic label |

**Valid human influenza examples:**
```fasta
>A/Novosibirsk/RII-7.429/2024|A/_H3N2|NP|2024-01-17|EPI_ISL19324838|3C.2a1b.2a.2a.3a.1
>B/Novosibirsk/RII-7.893S/2025|B|MP|2025-04-09|EPI_ISL_20154061|V1A.3a.2
>A/California/07/2009|A/_H1N1|HA|2009-04-09|EPI_ISL_29553|6B.1A
>B/Victoria/2/1987|B|NA|1987|EPI_ISL_100123|V1A.3a.2
>A/Hong_Kong/4801/2014|A/_H3N2|PA|2014-03-15|EPI_ISL_200456|3C.2a
```

**What these examples demonstrate:**

| Observation | Detail |
|-------------|--------|
| **Multi-subtype surveillance** | H3N2 (NP, PA), H1N1 (HA), and Flu B (MP, NA) coexist — use Subtype filter to isolate any one |
| **Multi-segment dataset** | NP, MP, HA, NA, PA all present — use Segment filter before phylogenetic analysis |
| **Year-only date** | `B/Victoria/2/1987` has just `1987` — parsed as Jan 1st 1987; appears correctly in temporal charts |
| **Accession without underscore** | `EPI_ISL19324838` (no `_` between ISL and digits) — the parser normalises both formats |
| **Flu B without subtype** | Second field is simply `B` — no H/N designation needed for influenza B |
| **Multi-decade span** | 1987 → 2025 = 38-year dataset — ideal for Gantt Range chart in Analytics |

**GISAID download settings for Human Influenza:**
- FASTA Header field: **Isolate name | Type | Collection date | Isolate ID | Lineage**
- Date format: YYYY-MM-DD (2009-02-28)
- ☑ Replace spaces with underscores in FASTA header
- ☑ Remove spaces before and after values in FASTA header

---

## ⚠️ Common Issues

- **Missing pipes**: If headers use spaces or commas, run the *Header Converter* in Sequence Refinery.
- **Year-only dates in temporal charts**: Sequences with only `YYYY` dates will cluster at month 1 — expected behaviour.
- **Blank segments**: Write `||` (empty field) rather than `N/A` — the parser treats "N/A" as a segment name.
- **Mixed accession formats**: Both `EPI_ISL_12345` and `EPI_ISL12345` are valid; the accession extractor handles both.

> 📄 For the complete format specification, see **1 FASTA Header Format Guide - Complete Reference.pdf** (included in the project download).
""",
    "ru": """\
VirSift поддерживает **формат GISAID с вертикальной чертой** для трёх групп вирусов.
Каждая группа имеет различное количество и порядок полей — выберите тот, который
соответствует вашей выгрузке из GISAID.

---

## 🫁 РСВ человека (hRSV)

**Структура заголовка:**
```
>Isolate_Name|GISAID_Accession|Collection_Date
```

| № | Поле | Пример | Формат |
|---|------|--------|--------|
| 1 | **Название изолята** | `hRSV/B/Argentina/BA-HNRG-206/2016` | hRSV/Субтип/Место/ID/Год |
| 2 | **Аккессия** | `EPI_ISL_1074181` | EPI_ISL_XXXXXXX |
| 3 | **Дата сбора** | `2016-04-18` | ГГГГ-ММ-ДД, ГГГГ-ММ, ГГГГ или `unknown` |

**Допустимые примеры hRSV:**
```fasta
>hRSV/B/South_Korea/YSU-96B19/un|EPI_ISL_19159645|unknown
>hRSV/A/Argentina/BA-HNRG-206/2016|EPI_ISL_1074181|2016-04-18
>RSV/Human/GBR/2023-001|RSV_A|G|2023-11-04|EPI_ISL_17000001|ON1
```

**Настройки загрузки GISAID для RSV:**
- Поля заголовка FASTA: **Isolate name | Isolate ID | Collection date**
- Формат даты: ГГГГ-ММ-ДД
- ☑ Заменить пробелы на подчёркивания в заголовке FASTA
- ☑ Удалить пробелы до и после значений

---

## 🐦 Птичий грипп

**Структура заголовка:**
```
>Isolate_Name|Virus_Type/Subtype|Gene_Segment|Collection_Date|GISAID_Accession|Clade_Assignment
```

| № | Поле | Пример | Формат |
|---|------|--------|--------|
| 1 | **Название изолята** | `A/duck/Bangladesh/33676/2017` | A/Хозяин/Место/ID/Год |
| 2 | **Тип / Субтип** | `A_/_H4N6` | `A_/_HxNy` или `A/HxNy` |
| 3 | **Сегмент** | `PA` | HA, NA, PA, PB1, PB2, NP, MP, NS |
| 4 | **Дата** | `2017-09-28` | ГГГГ-ММ-ДД, ГГГГ-ММ, ГГГГ или unknown |
| 5 | **Аккессия** | `EPI_ISL_329573` | EPI_ISL_XXXXXXX |
| 6 | **Клад** | `6B.1A.5a.2a.1` | Любой формат, пустое или `unassigned` |

**Допустимые примеры птичьего гриппа:**
```fasta
>A/duck/Bangladesh/33676/2017|A_/_H4N6|PA|2017-09-28|EPI_ISL_329573|6B.1A.5a.2a.1
>A/duck/Tottori/311018/2015|A_/_H3N6|PA|2015-10-01|EPI_ISL_237156|unassigned
>A/mallard/Republic_of_Georgia/13/2011|A_/_H6N2|PA|2011-11-26|EPI_ISL_189700|
>A/goose/China/1234/2020|A/H5N1|HA|2020-03|EPI_ISL_400001|2.3.4.4h
>A/wild_bird/Japan/567/2019|A_/_H7N9|NA|2019|EPI_ISL_300123|unassigned
```

**Настройки загрузки GISAID для птичьего гриппа:**
- Белки: выберите сегмент (например, HA, PA, NP)
- Поля заголовка FASTA: **Isolate name | Type | Collection date | Isolate ID | Lineage**
- Формат даты: ГГГГ-ММ-ДД
- ☑ Заменить пробелы на подчёркивания
- ☑ Удалить пробелы до и после значений
- *Примечание: добавьте название сегмента вручную или скачивайте каждый сегмент отдельно.*

---

## 🦠 Человеческий грипп

**Структура заголовка:**
```
>Isolate_Name|Virus_Type/Subtype|Gene_Segment|Collection_Date|GISAID_Accession|Clade_Assignment
```

| № | Поле | Примеры | Примечания |
|---|------|---------|-----------|
| 1 | **Название штамма** | `A/Novosibirsk/RII-7.429/2024` · `B/Victoria/2/1987` | Полное название изолята в стиле GISAID |
| 2 | **Тип / Субтип** | `A/_H3N2` · `A/_H1N1` · `B` | Для гриппа А — `A/_HxNx`; для гриппа В — просто `B` |
| 3 | **Сегмент** | `HA` · `NA` · `NP` · `MP` · `PA` | Любой из 8 генных сегментов гриппа |
| 4 | **Дата сбора** | `2024-01-17` · `2009-04-09` · `1987` | ISO 8601; только год (`ГГГГ`) тоже принимается |
| 5 | **Аккессия** | `EPI_ISL_19324838` · `EPI_ISL19324838` | С подчёркиванием и без — оба варианта поддерживаются |
| 6 | **Клад** | `3C.2a1b.2a.2a.3a.1` · `V1A.3a.2` · `6B.1A` | Метка клада от Nextclade / GISAID |

**Допустимые примеры человеческого гриппа:**
```fasta
>A/Novosibirsk/RII-7.429/2024|A/_H3N2|NP|2024-01-17|EPI_ISL19324838|3C.2a1b.2a.2a.3a.1
>B/Novosibirsk/RII-7.893S/2025|B|MP|2025-04-09|EPI_ISL_20154061|V1A.3a.2
>A/California/07/2009|A/_H1N1|HA|2009-04-09|EPI_ISL_29553|6B.1A
>B/Victoria/2/1987|B|NA|1987|EPI_ISL_100123|V1A.3a.2
>A/Hong_Kong/4801/2014|A/_H3N2|PA|2014-03-15|EPI_ISL_200456|3C.2a
```

**Что демонстрируют эти примеры:**

| Наблюдение | Подробности |
|------------|-------------|
| **Мультисубтипный надзор** | H3N2, H1N1 и грипп B сосуществуют — используйте фильтр Субтип |
| **Многосегментный датасет** | NP, MP, HA, NA, PA — используйте фильтр Сегмент перед анализом |
| **Дата только год** | `B/Victoria/2/1987` содержит лишь `1987` — разбирается как 1 января 1987 |
| **Аккессия без подчёркивания** | `EPI_ISL19324838` — парсер нормализует оба варианта |
| **Грипп B без субтипа** | Второе поле — просто `B`, без обозначения H/N |
| **Многодесятилетний охват** | 1987–2025 = 38 лет — идеально для диаграммы Ганта в Аналитике |

**Настройки загрузки GISAID для человеческого гриппа:**
- Поля заголовка FASTA: **Isolate name | Type | Collection date | Isolate ID | Lineage**
- Формат даты: ГГГГ-ММ-ДД
- ☑ Заменить пробелы на подчёркивания
- ☑ Удалить пробелы до и после значений

---

## ⚠️ Типичные проблемы

- **Отсутствующие вертикальные черты**: Используйте *Конвертер заголовков* в Очистителе.
- **Только год в дате**: Последовательности с `ГГГГ` будут кластеризованы в месяце 1 — ожидаемое поведение.
- **Пустые сегменты**: Пишите `||`, а не "N/A" — парсер воспримет "N/A" как название сегмента.
- **Смешанные форматы аккессий**: Оба варианта `EPI_ISL_12345` и `EPI_ISL12345` допустимы.

> 📄 Полная спецификация — **1 FASTA Header Format Guide - Complete Reference.pdf** (включён в загрузку проекта).
""",
}

# ─────────────────────────────────────────────────────────────────────────────
# Page
# ─────────────────────────────────────────────────────────────────────────────
st.title(f"📚 {T('docs_page_header')}")
st.caption(T("docs_page_caption"))

tab_qs, tab_feat, tab_tips, tab_hdr, tab_uc = st.tabs([
    f"🚀 {T('docs_tab_quickstart')}",
    f"🔧 {T('docs_tab_features')}",
    f"💡 {T('docs_tab_tips')}",
    f"🧬 {T('docs_tab_header_format')}",
    f"📚 {T('docs_tab_usecases')}",
])

# ── Tab 1: Quick-Start Guide ──────────────────────────────────────────────────
with tab_qs:
    st.markdown(_QUICKSTART.get(_lang, _QUICKSTART["en"]))

    st.divider()
    st.markdown(f"### 🗺️ {T('docs_nav_map_header')}")
    col_pages = st.columns(5)
    _pages_info = [
        ("📁", T("nav_workspace"),  T("docs_nav_workspace_desc"),  "pages/02_📁_Workspace.py"),
        ("🔬", T("nav_refinery"),   T("docs_nav_refinery_desc"),   "pages/03_🔬_Sequence_Refinery.py"),
        ("🧬", T("nav_timeline"),   T("docs_nav_timeline_desc"),   "pages/04_🧬_Molecular_Timeline.py"),
        ("📊", T("nav_analytics"),  T("docs_nav_analytics_desc"),  "pages/05_📊_Analytics.py"),
        ("📋", T("nav_export"),     T("docs_nav_export_desc"),     "pages/06_📋_Export.py"),
    ]
    for col, (icon, name, desc, path) in zip(col_pages, _pages_info):
        with col:
            st.markdown(f"**{icon} {name}**")
            st.caption(desc)
            try:
                st.page_link(path, label=f"→ {name}", use_container_width=True)
            except Exception:
                st.markdown(f"[→ {name}]({path})")

# ── Tab 2: Feature Reference ──────────────────────────────────────────────────
with tab_feat:
    st.markdown(f"### {T('docs_feature_ref_header')}")
    st.markdown(_FEATURE_TABLE.get(_lang, _FEATURE_TABLE["en"]))

# ── Tab 3: Tips & FAQ ─────────────────────────────────────────────────────────
with tab_tips:
    st.markdown(_TIPS_FAQ.get(_lang, _TIPS_FAQ["en"]))

# ── Tab 4: FASTA Header Format ────────────────────────────────────────────────
with tab_hdr:
    st.markdown(_HEADER_FORMAT.get(_lang, _HEADER_FORMAT["en"]))

    _pdf_path = os.path.join("cases", "1 FASTA Header Format Guide - Complete Reference.pdf")
    if os.path.exists(_pdf_path):
        with open(_pdf_path, "rb") as _pdf_f:
            st.download_button(
                label=f"📄 {T('docs_download_pdf')}",
                data=_pdf_f.read(),
                file_name="FASTA_Header_Format_Guide.pdf",
                mime="application/pdf",
                use_container_width=False,
            )
    else:
        st.caption(T("docs_download_pdf_missing"))

    # ── Test datasets section ────────────────────────────────────────────────
    st.divider()
    st.markdown(f"### 🧪 {T('docs_test_data_header')}")
    st.warning(T("docs_test_data_disclaimer"))

    _cases_dir = "cases"
    _test_files = [
        (
            "RSV-B_for_filtration.fasta",
            "docs_dl_rsv_fasta",
            "RSV-B — 3-field GISAID format: `>Isolate_Name|EPI_ISL|Date`",
            "RSV-B_for_filtration.fasta",
        ),
        (
            "All H3N2_20250918_070704.fasta",
            "docs_dl_h3n2_fasta",
            "H3N2 — 6-field GISAID format: `>Name|Type|Segment|Date|Accession|Clade`",
            "All_H3N2_test.fasta",
        ),
        (
            "HA_test_copy1.fasta",
            "docs_dl_ha_fasta",
            "HA segment — mixed Influenza A subtypes, multi-clade",
            "HA_test_copy1.fasta",
        ),
    ]

    _dl_cols = st.columns(3)
    for _col, (_fname, _key, _desc, _dl_name) in zip(_dl_cols, _test_files):
        _fpath = os.path.join(_cases_dir, _fname)
        with _col:
            st.caption(_desc)
            if os.path.exists(_fpath):
                with open(_fpath, "rb") as _ff:
                    st.download_button(
                        label=T(_key),
                        data=_ff.read(),
                        file_name=_dl_name,
                        mime="text/plain",
                        use_container_width=True,
                        key=f"dl_test_{_fname[:8]}",
                    )
            else:
                st.caption(f"_(file not found: `{_fname}`)_")

# ── Tab 5: Use Case Library ───────────────────────────────────────────────────
with tab_uc:
    st.markdown(f"### {T('docs_usecase_header')}")
    st.caption(T("docs_usecase_caption"))

    _uc_file = "usecase_ru.md" if _lang == "ru" else "usecase.md"
    _uc_path = os.path.join("cases", _uc_file)
    if not os.path.exists(_uc_path):  # Fallback to English if Russian not present
        _uc_path = os.path.join("cases", "usecase.md")
    if os.path.exists(_uc_path):
        with open(_uc_path, encoding="utf-8") as _uc_f:
            _uc_content = _uc_f.read()

        # Download button
        st.download_button(
            label=f"📥 {T('docs_download_guide')}",
            data=_uc_content.encode("utf-8"),
            file_name="virsift_usecase_guide.md",
            mime="text/markdown",
            type="primary",
            use_container_width=False,
        )

        st.divider()

        # Inline preview — first 5 use cases with search
        _search = st.text_input(T("docs_uc_search"), placeholder="H3N2, RSV, timeline …")

        # Parse use-cases by "## Use Case" headings
        import re as _re
        _uc_blocks = _re.split(r"(?=^## Use Case \d+)", _uc_content, flags=_re.MULTILINE)
        _uc_blocks = [b for b in _uc_blocks if b.strip().startswith("## Use Case")]

        if _search:
            _uc_blocks = [b for b in _uc_blocks if _search.lower() in b.lower()]
            st.caption(f"{T('docs_uc_results', n=len(_uc_blocks))}")

        if _uc_blocks:
            for _block in _uc_blocks[:20]:
                _title_line = _block.split("\n", 1)[0].strip("# ").strip()
                with st.expander(_title_line, expanded=False):
                    st.markdown(_block)
            if len(_uc_blocks) > 20:
                st.caption(T("export_more_items", n=len(_uc_blocks) - 20))
        else:
            st.info(T("docs_uc_no_results"))
    else:
        st.warning(T("docs_usecase_missing"))

    # Download documentation as Markdown (combined guide + feature reference)
    st.divider()
    _doc_bundle = (
        f"# Vir-Seq-Sift v2.1 — {T('docs_page_header')}\n\n"
        f"## {T('docs_tab_quickstart')}\n\n{_QUICKSTART.get(_lang, _QUICKSTART['en'])}\n\n"
        f"## {T('docs_tab_features')}\n\n{_FEATURE_TABLE.get(_lang, _FEATURE_TABLE['en'])}\n\n"
        f"## {T('docs_tab_tips')}\n\n{_TIPS_FAQ.get(_lang, _TIPS_FAQ['en'])}\n\n"
        f"## {T('docs_tab_header_format')}\n\n{_HEADER_FORMAT.get(_lang, _HEADER_FORMAT['en'])}\n"
    )
    st.download_button(
        label=f"📥 {T('docs_download_docs')}",
        data=_doc_bundle.encode("utf-8"),
        file_name="virsift_documentation.md",
        mime="text/markdown",
        use_container_width=False,
    )

# ─────────────────────────────────────────────────────────────────────────────
# Inter-page navigation
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
_doc_n1, _doc_n2 = st.columns(2)
try:
    _doc_n1.page_link("pages/06_📋_Export.py",
                      label=f"← 📋 {T('nav_export')}",
                      use_container_width=True)
    _doc_n2.page_link("pages/01_🌍_Observatory.py",
                      label=f"🌍 {T('nav_observatory')} →",
                      use_container_width=True)
except AttributeError:
    _doc_n1.markdown(f"[← 📋 {T('nav_export')}](pages/06_📋_Export.py)")
    _doc_n2.markdown(f"[🌍 {T('nav_observatory')} →](pages/01_🌍_Observatory.py)")
