# Predictive Risk and Recording Decisions

Private research collaboration workspace for **Predictive Risk and Recording Decisions in Partially Observed Neural Networks**.

## Start here

- [Current manuscript PDF](01_READ_CURRENT/paper_current.pdf) · [Markdown source](01_READ_CURRENT/paper_current.md)
- [Current graphical abstract](01_READ_CURRENT/graphical_abstract.pdf) · [PNG](01_READ_CURRENT/graphical_abstract.png)
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

The current manuscript follows endpoint allocation, response uncertainty, recurrent parameter combinations and acquisition of information through a fifth recording. Its five main figures follow that sequence and the structural checks. Original criterion studies, their frozen primary comparisons and detailed fitting/budget diagnostics are retained in the supplementary analyses, with a summary of their outcomes in the main Results. The 100-unit evidence now comprises eight pilot networks, seven disjoint 40-network cohorts and an independent 80-network follow-up (368 base networks total); repeated analyses of a cohort are not additional networks.

At a fixed budget of five recordings, joint stimulation/readout coverage reduced held-out response MSE by 96.44% in the initial cohort and 98.13% in independent validation. Response-range searches, recording-precision changes and gain-information controls support a task-specific information mechanism. Endpoint allocation also improved prediction under rank-six augmentation and mild model errors.

The recurrent gain combinations identify internal information with predictive value after endpoint gains are known. A combination-directed fifth recording narrowed a prespecified nonlinear feasible range. An independent 80-network follow-up, with three noise repeats per network, then reduced actual combination estimation MSE by 31.07% relative to a random fifth site. In secondary comparisons, a response-directed or random fifth site reduced prediction MSE by about 30% relative to four-endpoint recording.

The follow-up's prespecified primary response-directed-versus-random fifth-site contrast was +0.24% (95% interval: -41.36% to +74.08%). Complete comparisons are in Supplementary Table 3. The 100-unit model configuration is collected at the start of Methods. New numerical records are in `03_REPRODUCIBLE_WORKSPACE/work/recording_extensions/round6/`; Fig. 4 shows the 40- and 80-network fifth-recording cohorts side by side.

- [Extension code, protocols and numerical records](03_REPRODUCIBLE_WORKSPACE/work/recording_extensions/)
- [Current canonical manuscript and build source](03_REPRODUCIBLE_WORKSPACE/outputs/endpoint_revision/)

The current graphical abstract keeps the original v5 layout — network illustration, three numbered evidence frames, formula and summary — with its frames updated to endpoint recording, the finite-response error factors and the fifth recording, and the stimulation and readout nodes drawn as recorded. Its takeaway is **Better risk estimates do not necessarily make better recording decisions.** All manuscript figures follow the refined manuscript's BentonSans typography and pink palette, with one meaning per colour, a common percentage-change scale for effects and printed estimates beside each interval; the figure rules are in `outputs/endpoint_revision/figure_style.py`. Earlier graphical abstracts remain in `03_REPRODUCIBLE_WORKSPACE/outputs/graphical_abstract/`; historical manuscripts, receipts and audits retain their original scope. The study has not been submitted.

## Verify

```sh
python3 validate_handoff.py
```

This checks file integrity, frozen result lineage and current asset consistency. It does not rerun the full experiments. Runtime requirements and rendering commands are in the reproduction guide.

## Working together

Use a branch and pull request for changes. Describe which scientific claims or assets change and how they were checked. Keep raw/frozen result folders unchanged; add new analyses in separate folders. Update source and regenerated assets together. Use Issues for research questions and decisions.

The initial import contains earlier GPT/Codex and Claude project extracts; it is not a claim that every chat or every cited paper's full text has been recovered. Preserve contributor attribution. Font files and third-party material retain their original rights; no blanket open-source license is applied.
