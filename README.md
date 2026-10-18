# Neural recording research

Private research collaboration workspace for **Predictive Risk and Recording Decisions in Partially Observed Neural Networks**.

## Start here

- [Current manuscript PDF](01_READ_CURRENT/paper_current.pdf) · [Markdown source](01_READ_CURRENT/paper_current.md)
- [Current graphical abstract v5](01_READ_CURRENT/graphical_abstract.pdf) · [PNG](01_READ_CURRENT/graphical_abstract.png)
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

The manuscript is 22 pages. Graphical abstract v5 includes the exact takeaway **Better risk estimates do not necessarily make better recording decisions.** The previous version without that sentence is retained with its source at `03_REPRODUCIBLE_WORKSPACE/outputs/graphical_abstract/versions/v4_without_key_finding/`. The paper PDF did not change for this standalone graphical abstract revision.

This is a simulation-based study, prepared but not submitted. Primary error and forecast-score intervals include zero; the 100-unit extension is exploratory. Frozen numerical results and historical outputs are retained for traceability. Historical submission drafts and receipts describe their own snapshots, not necessarily the current draft.

## Verify

```sh
python3 validate_handoff.py
```

This checks file integrity, frozen result lineage and current asset consistency. It does not rerun the full experiments. Runtime requirements and rendering commands are in the reproduction guide.

## Working together

Use a branch and pull request for changes. Describe which scientific claims or assets change and how they were checked. Keep raw/frozen result folders unchanged; add new analyses in separate folders. Update source and regenerated assets together. Use Issues for research questions and decisions.

The initial import contains earlier GPT/Codex and Claude project extracts; it is not a claim that every chat or every cited paper's full text has been recovered. Preserve contributor attribution. Font files and third-party material retain their original rights; no blanket open-source license is applied.
