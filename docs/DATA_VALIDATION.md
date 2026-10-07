# Data Validation
Validators run only after datasets are connected and output reports to `reports/documentation/`.
**Images:** readable files, allowed extensions, corrupt/zero-size, dimensions/channels, duplicate hashes (also across splits), class folder consistency, label set matches expected.
**Regional CSV:** schema check against verified columns, expected 12 regions x ~8 years, missing/duplicate (region, year), non-negative target, coordinate ranges, unit consistency, source field present. Expected counts are *checks*, not assumed truths.
**Output:** pass/fail with issue list (`ValidationReport`); failures block downstream stages.
