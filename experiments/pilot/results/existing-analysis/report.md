# Existing completed Qwen comparisons — exploratory snapshot

Exploratory localization against unreviewed patch-change proxies. Completed-case cost excludes interrupted attempts. No full-study completion claim.

## Qwen/Qwen2.5-Coder-7B-Instruct

472 issues have all four workflows and eligible file labels.

| Workflow | File Top1 | File Top5 | Function Top1 | Mean tokens | Mean seconds | Mean resets |
|---|---:|---:|---:|---:|---:|---:|
| morph | 42.8% | 71.0% | 20.3% | 27287.2 | 94.7 | 0.3 |
| no_forgetting | 43.2% | 71.6% | 19.8% | 26602.1 | 91.8 | 0.0 |
| fixed_reset | 42.2% | 71.2% | 19.4% | 28140.6 | 97.6 | 1.1 |
| stateless_summary | 52.5% | 73.5% | 24.7% | 28916.2 | 144.5 | 0.0 |

Paired MORPH minus comparator File Top1 differences; descriptive 95% repository-cluster bootstrap intervals (2,000 draws):

- no_forgetting: -0.4 percentage points [-1.4, +0.0]; 11 repositories.
- fixed_reset: +0.6 percentage points [-0.5, +1.5]; 11 repositories.
- stateless_summary: -9.7 percentage points [-12.5, -4.3]; 11 repositories.

