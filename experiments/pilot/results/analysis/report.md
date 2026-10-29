# 50-issue two-model pilot

Exploratory localization against unreviewed patch-change proxies. Completed-case cost excludes interrupted attempts. No full-study completion claim.

## Qwen/Qwen2.5-Coder-7B-Instruct

50 issues have all four workflows and eligible file labels.

| Workflow | File Top1 | File Top5 | Function Top1 | Mean tokens | Mean seconds | Mean resets |
|---|---:|---:|---:|---:|---:|---:|
| morph | 42.0% | 72.0% | 16.7% | 28256.8 | 93.6 | 0.2 |
| no_forgetting | 42.0% | 74.0% | 16.7% | 27573.5 | 89.5 | 0.0 |
| fixed_reset | 42.0% | 76.0% | 14.6% | 29114.4 | 94.7 | 1.0 |
| stateless_summary | 50.0% | 78.0% | 22.9% | 29325.2 | 140.3 | 0.0 |

Paired MORPH minus comparator File Top1 differences; descriptive 95% repository-cluster bootstrap intervals (2,000 draws):

- no_forgetting: +0.0 percentage points [+0.0, +0.0]; 12 repositories.
- fixed_reset: +0.0 percentage points [+0.0, +0.0]; 12 repositories.
- stateless_summary: -8.0 percentage points [-16.0, +0.0]; 12 repositories.

## deepseek-ai/deepseek-coder-6.7b-instruct

50 issues have all four workflows and eligible file labels.

| Workflow | File Top1 | File Top5 | Function Top1 | Mean tokens | Mean seconds | Mean resets |
|---|---:|---:|---:|---:|---:|---:|
| morph | 40.0% | 70.0% | 0.0% | 29196.8 | 55.0 | 0.6 |
| no_forgetting | 40.0% | 70.0% | 0.0% | 27911.7 | 48.3 | 0.0 |
| fixed_reset | 40.0% | 70.0% | 0.0% | 29553.1 | 53.8 | 1.4 |
| stateless_summary | 40.0% | 72.0% | 12.5% | 29920.4 | 111.5 | 0.0 |

Paired MORPH minus comparator File Top1 differences; descriptive 95% repository-cluster bootstrap intervals (2,000 draws):

- no_forgetting: +0.0 percentage points [+0.0, +0.0]; 12 repositories.
- fixed_reset: +0.0 percentage points [+0.0, +0.0]; 12 repositories.
- stateless_summary: +0.0 percentage points [-9.8, +12.0]; 12 repositories.

