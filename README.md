# Predictive Risk and Recording Decisions

Private research collaboration workspace for **Predictive Risk and Recording Decisions in Partially Observed Neural Networks**.

## Start here

- [Current manuscript PDF](01_READ_CURRENT/paper_current.pdf) · [Markdown source](01_READ_CURRENT/paper_current.md)
- [Criterion-comparison graphical abstract v5](01_READ_CURRENT/graphical_abstract.pdf) · [PNG](01_READ_CURRENT/graphical_abstract.png)
- [Research narrative and version audit](01_研究主线与版本审计.md)
- [Reproduction and code entry points](02_重现与代码入口.md)
- [Collaboration context and decisions](COLLABORATION.md)

## Contents

| Directory | Purpose |
|---|---|
| `01_READ_CURRENT` | Current paper and graphical abstract |
| `02_RESEARCH_FOUNDATION` | Conference, literature and methodological research, including Claude outputs |
| `03_REPRODUCIBLE_WORKSPACE` | Manuscript sources, plotting code, frozen results, validators and figure assets |
| `04_CONTEXT_AND_HISTORY` | GPT/Codex and Claude project conversation extracts, earlier proposals and design iterations |
| `05_AUDIT` | Provenance, numerical lineage, integrity checks and historical receipts |

## Current status

The current manuscript integrates the original criterion comparisons with endpoint-allocation, parameter-combination mechanism, structural robustness and limited-budget experiments. The 100-unit evidence now comprises eight pilot networks and six disjoint 40-network cohorts (248 base networks total); repeated analyses of a cohort are not additional networks.

At a fixed budget of five recordings, joint stimulation/readout coverage reduced held-out response MSE by 96.44% in the initial cohort and 98.13% in independent validation. A further independent cohort supports a task-specific information mechanism through response-range searches, recording-precision changes and gain-information controls. The original prior-averaging comparisons and the new covariance-based comparisons do not establish a robust additional method advantage after fitting sensitivity is considered. The new information control shows complementary value in four recurrent gain combinations after endpoint gains are known: MSE changed by -91.45% relative to an equal-dimensional ordinary-gain control. Endpoint allocation retained a -92.08% effect under rank-six augmentation; random rank-six and positive-gain conditions remain less certain. Under budgets two and three with unequal recording precision, pair lookahead matched ensemble-greedy sets in 237/240 settings and added negligible benefit. These findings concern the tested simulations.

- [Extension code, protocols and numerical records](03_REPRODUCIBLE_WORKSPACE/work/recording_extensions/)
- [Current canonical manuscript and build source](03_REPRODUCIBLE_WORKSPACE/outputs/endpoint_revision/)

The existing graphical abstract retains the criterion-comparison takeaway **Better risk estimates do not necessarily make better recording decisions.** It has not been redesigned to summarize the endpoint and mechanism findings. Historical manuscripts, receipts and audits retain their original scope. The study has not been submitted.

## Verify

```sh
python3 validate_handoff.py
```

This checks file integrity, frozen result lineage and current asset consistency. It does not rerun the full experiments. Runtime requirements and rendering commands are in the reproduction guide.

## Working together

Use a branch and pull request for changes. Describe which scientific claims or assets change and how they were checked. Keep raw/frozen result folders unchanged; add new analyses in separate folders. Update source and regenerated assets together. Use Issues for research questions and decisions.

The initial import contains earlier GPT/Codex and Claude project extracts; it is not a claim that every chat or every cited paper's full text has been recovered. Preserve contributor attribution. Font files and third-party material retain their original rights; no blanket open-source license is applied.
