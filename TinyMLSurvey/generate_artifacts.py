import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
import warnings

# Suppress warnings for a clean console output
warnings.simplefilter(action='ignore', category=FutureWarning)

def load_file(base_name):
    """Checks for CSV first, then XLSX."""
    if os.path.exists(f'{base_name}.csv'):
        return pd.read_csv(f'{base_name}.csv', low_memory=False)
    elif os.path.exists(f'{base_name}.xlsx'):
        return pd.read_excel(f'{base_name}.xlsx')
    return None

def main():
    # 1. Load Data
    df_master = load_file('papers_master')
    df_log = load_file('screening_log')

    if df_master is None or df_log is None:
        print("❌ Error: Ensure 'papers_master' and 'screening_log' files exist in this folder.")
        return

    # 2. Process Master Data for Inclusion
    df_master['include_core'] = df_master['include_core'].astype(str).str.strip().str.title()
    core_df = df_master[df_master['include_core'].str.contains('Yes|In|Maybe', case=False, na=False)].copy()
    excluded_df = df_master[df_master['include_core'] == 'No'].copy()

    # --- ARTIFACT 1: CUSTOM TAXONOMY DIAGRAM ---
    # Explode multi-class rows (C01; C02) so they count for both
    core_df['class_id_clean'] = core_df['class_id'].astype(str).str.replace(',', ';')
    core_df['class_list'] = core_df['class_id_clean'].apply(
        lambda x: [c.strip() for c in x.split(';') if c.strip() and c.strip().lower() != 'nan']
    )
    exploded_classes = core_df.explode('class_list')
    counts = exploded_classes['class_list'].value_counts().to_dict()
    
    # Map counts to keys C01-C06
    class_map = {f'C{i:02}': counts.get(f'C{i:02}', 0) for i in range(1, 7)}

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(-6, 6); ax.set_ylim(-7, 1); ax.axis('off')

    # Draw Diagram (Matching TikZ colors and hierarchy)
    # Root
    ax.add_patch(patches.FancyBboxPatch((-2.1, -0.5), 4.2, 1, boxstyle="round,pad=0.1", fc="#F4E7FB", ec="#9C27B0", lw=1.5))
    ax.text(0, 0, "TinyML in IoT\n(Resource-Constrained Edge Intelligence)", ha='center', va='center', fontweight='bold', fontsize=11)
    
    ax.plot([0, 0], [-0.5, -1.2], color="#9E9E9E", lw=1.5) # Stem
    ax.plot([-4.8, 4.8], [-1.2, -1.2], color="#9E9E9E", lw=1.5) # Bar

    x_pos = [-4.8, -2.4, 0, 2.4, 4.8]
    labels = ["Wearable & IMU", "Audio & Acoustic", "Urban & Outdoor", "Industrial Anomaly", "Indoor Context"]
    for i, x in enumerate(x_pos):
        cid = f'C{i+1:02}'
        ax.plot([x, x], [-1.2, -1.8], color="#9E9E9E", lw=1.5)
        ax.add_patch(patches.FancyBboxPatch((x-1.1, -4.2), 2.2, 2.4, boxstyle="round,pad=0.1", fc="#E8F5E9", ec="#2E7D32", lw=1.2))
        ax.text(x, -3, f"{cid}\n{labels[i]}\n{class_map[cid]} papers", ha='center', va='center', fontsize=9)
        ax.plot([x, x], [-4.2, -5.2], color="#9E9E9E", lw=1, linestyle='--')

    # C06 Wide Box
    ax.add_patch(patches.FancyBboxPatch((-5, -6.5), 10, 1.3, boxstyle="round,pad=0.1", fc="#FFF3E0", ec="#EF6C00", lw=1.5))
    ax.text(0, -5.85, f"C06 — Benchmarking & Evaluation ({class_map['C06']} papers)", ha='center', fontweight='bold')
    ax.text(0, -6.2, "MLPerf Tiny • EdgeMark • MLino bench • TFLM", ha='center', fontsize=8, style='italic')

    plt.tight_layout()
    plt.savefig('fig_class_distribution.png', dpi=300)
    print("✅ Generated: fig_class_distribution.png")

    # --- ARTIFACT 2: PRISMA EXCLUSIONS TABLE ---
    # Agreement: Just count 'Yes' in the agreement column
    agreement_count = df_log['agreement'].astype(str).str.strip().str.lower().value_counts().get('yes', 0)
    total_screened = 151 # Total unique papers identified

    # Group Exclusion Reasons exactly as requested
    ex_platform = excluded_df['screen_reason'].str.contains('EX_PLATFORM|EX_NO_DEPLOY', case=False, na=False).sum()
    ex_dup = excluded_df['screen_reason'].str.contains('EX_DUP', case=False, na=False).sum()
    ex_metrics = excluded_df['screen_reason'].str.contains('EX_NO_METRICS|OUT_OF_SCOPE', case=False, na=False).sum()

    prisma_rows = [
        ['Identification', ''],
        ['  Records identified via database search (IEEE, ACM, Scopus)', total_screened],
        ['  Records after duplicate removal', total_screened],
        ['Screening', ''],
        ['  Total screening decisions recorded', total_screened],
        [f'  Records with initial inter-reviewer agreement ({(agreement_count/total_screened*100):.1f}%)', agreement_count],
        ['Eligibility', ''],
        ['  Full-text articles assessed for eligibility (post-adjudication)', total_screened],
        ['  Full-text articles excluded', len(excluded_df)],
        ['    -- Reason: EX_PLATFORM / EX_NO_DEPLOY', ex_platform],
        ['    -- Reason: EX_DUP', ex_dup],
        ['    -- Reason: EX_NO_METRICS / OUT_OF_SCOPE', ex_metrics],
        ['Inclusion', ''],
        ['  Total studies included in final Core Corpus', f"104 (100 core papers + 4 core surveys)"]
    ]

    pd.DataFrame(prisma_rows, columns=['Review Stage', 'Count']).to_csv('table_prisma_flow.csv', index=False)
    print("✅ Generated: table_prisma_flow.csv")

    # --- ARTIFACT 3: REPORTING GAPS TABLE ---
    def is_reported(series):
        return series.replace(['NA', 'NR', 'None', '', 'NaN', 'nan'], np.nan).notna()

    metrics_data = {
        'Metric Type': [
            'Classification accuracy', 'Inference latency (ms)', 'Model size (KB)',
            'RAM/Flash usage (KB)', 'Energy per inference (mJ)',
            'Real-world deployment validation', 'Quantization adoption', 'Code availability'
        ],
        'Number of Papers': [
            is_reported(core_df['metrics_primary_value']).sum(),
            is_reported(core_df['metrics_latency_ms']).sum(),
            is_reported(core_df['model_kb']).sum(),
            (is_reported(core_df['ram_kb']) | is_reported(core_df['flash_kb'])).sum(),
            is_reported(core_df['metrics_energy_mj']).sum(),
            core_df['real_world_eval'].astype(str).str.contains('Yes', case=False, na=False).sum(),
            core_df['quantization'].astype(str).str.contains('Yes', case=False, na=False).sum(),
            core_df['code_available'].astype(str).str.contains('Yes', case=False, na=False).sum()
        ]
    }

    metrics_table = pd.DataFrame(metrics_data)
    metrics_table['Percentage'] = (metrics_table['Number of Papers'] / 104 * 100).map('{:.1f}%'.format)
    metrics_table.to_csv('table_14_reporting_gaps.csv', index=False)
    print("✅ Generated: table_14_reporting_gaps.csv")

if __name__ == "__main__":
    main()