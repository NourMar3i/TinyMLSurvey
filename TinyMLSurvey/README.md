🔬 TinyML Systematic Review: Reproducibility & Interactive Artifacts
====================================================================

This repository contains the reproducibility suite and interactive companion app for our TinyML Systematic Review. These tools dynamically process the `papers_master.xlsx` database and `screening_log.xlsx` to generate the manuscript's primary figures, validated reporting statistics, and an interactive exploration dashboard.

📦 Prerequisites & Installation
-------------------------------

Ensure you have **Python 3.8+** installed. To install the required dependencies (including Streamlit, Pandas, and Matplotlib), run the following command in your terminal:

Bash

```
pip install -r requirements.txt

```

*Note: The `openpyxl` library is included in requirements to enable reading the Excel-based database.*

* * * * *

📊 1. Generating Manuscript Artifacts (`generate_artifacts.py`)
---------------------------------------------------------------

This script performs the heavy lifting for the paper's data analysis. It handles multi-class label exploding, calculates inter-reviewer agreement from the screening logs, and groups exclusion reasons for the PRISMA flow.

**To run the script:**

Bash

```
python generate_artifacts.py

```

**Key Outputs:**

-   **`fig_class_distribution.pdf`**: A professional taxonomy tree showing paper counts across C01--C06.

-   **`table_prisma_flow.csv`**: The exact numerical breakdown for the PRISMA study selection diagram.

-   **`table_14_reporting_gaps.csv`**: Quantified reporting rates for latency, energy, memory, and code availability.

* * * * *

🌐 2. Interactive Corpus Companion (`app.py`)
---------------------------------------------

We have developed a professional **Streamlit Dashboard** that serves as an interactive companion to the manuscript. This allows reviewers and readers to verify our statistical claims and explore the raw data behind the findings.

**To launch the app:**

Bash

```
streamlit run app.py

```

**Features:**

-   **📊 Study Statistics Tab**: View live KPI cards (Real-World Eval %, Energy Reporting %, etc.) and the finalized taxonomy diagram and PRISMA tables.

-   **🔍 Corpus Explorer Tab**: Search the 104 core papers by keyword or filter by hardware platform, IoT subdomain, and code availability.

-   **📥 Data Export**: Filtered results can be exported to CSV directly from the browser for independent verification.

-   **📑 Documentation Tab**: Full data dictionary and class definitions for the C01--C06 taxonomy.

* * * * *

🗂️ File Structure Requirements
-------------------------------

For the suite to function correctly, the following files must remain in the same directory:

| **File** | **Description** |
| --- | --- |
| `papers_master.xlsx` | The primary database containing all extracted paper data. |
| `screening_log.xlsx` | The audit trail used to calculate inter-reviewer agreement. |
| `generate_artifacts.py` | The script that creates PDFs and CSVs for the manuscript. |
| `app.py` | The Streamlit interactive dashboard code. |
| `requirements.txt` | List of necessary Python libraries. |

* * * * *

✅ Quick Verification for Reviewers
----------------------------------

1.  Run `python generate_artifacts.py` to ensure the generated CSVs match the numbers cited in the manuscript.

2.  Launch the app via `streamlit run app.py`.

3.  Select all filters in the sidebar to verify the total core corpus count of **104 papers** (including the 2 general surveys used for introductory context).