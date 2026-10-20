import os

files = [
    'reports/phase2_daily_mission.md',
    'reports/phase3a_shell_study_implementation.md',
    'reports/phase3a_test_report.md',
    'reports/phase3b_pyq_implementation.md',
    'reports/phase3b_pyq_test_report.md',
    'reports/phase3c_review_implementation.md',
    'reports/phase3c_review_test_report.md',
    'reports/phase3d_mock_exam_implementation.md',
    'reports/phase3d_mock_exam_test_report.md',
    'reports/phase3e_progress_implementation.md',
    'reports/phase3e_progress_test_report.md',
    'reports/phase3f_settings_implementation.md',
    'reports/phase3f_settings_test_report.md',
    'reports/phase4_preflight.md',
    'reports/phase4_integration_matrix.csv',
    'reports/phase4_integration_audit.md',
    'reports/phase4_security_audit.md',
    'reports/phase4_data_integrity_report.md',
    'reports/phase4_device_and_pwa_report.md',
    'reports/phase4_test_report.md',
    'reports/phase4_vps_readiness.md',
    'reports/phase4_release_decision.md'
]

out_lines = []
out_lines.append('# GPAT Learning OS — Consolidated Implementation & Audit Reports (Phase 2 to Phase 4)\n')
out_lines.append('**Generated:** 2026-10-19\n')
out_lines.append('**Scope:** Phase 2 (Daily Mission), Phase 3A-3F (Shell, Study Explorer, PYQ, Review/FSRS, Mock Exams, Progress Analytics, Settings/Account), and Phase 4 (Integration & Release-Readiness Audit)\n')
out_lines.append('---\n')
out_lines.append('## Table of Contents\n')
for f in files:
    fname = os.path.basename(f)
    anchor = fname.lower().replace('.', '').replace('_', '-')
    out_lines.append(f'- [{fname}](#{anchor})')
out_lines.append('\n---\n')

for f in files:
    fname = os.path.basename(f)
    anchor = fname.lower().replace('.', '').replace('_', '-')
    out_lines.append(f'<a id="{anchor}"></a>\n')
    out_lines.append('=' * 80)
    out_lines.append(f'# FILE: {fname}')
    out_lines.append('=' * 80 + '\n')
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as rf:
            content = rf.read()
        if f.endswith('.csv'):
            out_lines.append('```csv\n' + content + '\n```\n')
        else:
            out_lines.append(content + '\n')
    else:
        out_lines.append(f'*File not found: {f}*\n')
    out_lines.append('\n\n')

out_path = 'reports/PHASE_2_TO_4_CONSOLIDATED_REPORT.md'
with open(out_path, 'w', encoding='utf-8') as wf:
    wf.write('\n'.join(out_lines))

print(f'Successfully consolidated {len(files)} reports into {out_path} ({os.path.getsize(out_path)} bytes)')
