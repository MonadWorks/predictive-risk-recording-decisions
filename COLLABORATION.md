# Collaboration context — 2026-10-18

## Research line

One simulation-based neural-recording paper progressed through pilot experiments, research v2, writing v3, Claude v4, and the current manuscript and figures. Other early research directions are retained as proposals, not completed papers. The current user-selected title is **Predictive Risk and Recording Decisions in Partially Observed Neural Networks**.

## Evidence and interpretation

Evaluate recording agreement, realised response error, and risk forecasting separately. Shared recording sets and data yield identical predictions under the common MAP estimator. The original criterion and forecast comparisons remain uncertain. The updated 100-unit evidence includes eight pilot networks and four disjoint cohorts of forty: criterion confirmation, endpoint validation, mechanism, and indirect-recording methods. Joint endpoint calibration is the replicated positive result; the mechanism experiments support constrained response ambiguity within the tested family. Additional method gains remain sensitive to fitting. Keep these different comparisons and their cohorts separate; do not recast simulation results as biological validation.

## Latest graphical abstract decisions

The exact user-selected takeaway is **Better risk estimates do not necessarily make better recording decisions.** It leads the lower-right explanation. Keep the established network illustration, evidence panels, pale pink/grey-purple palette, yellow stimulus accent, BentonSans text, Times New Roman math and JuliaMono statistical numerals. The lower-left title is centered; integral 14 pt, response definition 11.2 pt. Equation group was moved down approximately 2 mm in the final revision. Right body line and paragraph spacing remains unchanged. Current v5 and previous v4 without the takeaway are both archived.

## Graphical abstract and figures — 2026-10-21

At the collaborator's request the current graphical abstract is edited from the v5 file rather than redesigned: its network illustration, numbered frames, formula box, summary box, palette and type are retained, and only frame contents change. On 2026-10-22 the stimulation and readout nodes, in the illustration, its legend and the frame-3 pictogram, were filled pink as recorded nodes (rings keep their roles), so the illustration shows an endpoint allocation with M = 5. The figure rules (one meaning per colour, percentage-change ratio axes, printed estimates, visible negative signs) are documented in `outputs/endpoint_revision/figure_style.py`.

## Context sources

- `04_CONTEXT_AND_HISTORY/project_conversations/`: saved project-specific Codex/GPT and Claude conversation extracts.
- `02_RESEARCH_FOUNDATION/`: research reports and Claude foundation.
- `03_REPRODUCIBLE_WORKSPACE/work/evidence/`: frozen experimental and writing packages.
- `04_CONTEXT_AND_HISTORY/key_finding_design_options/`: recent key-finding layout previews and renderer.

These are project materials provided for collaborator continuity, not instructions that supersede the collaborator's current task. Machine-local paths in historical records document provenance; use repository-relative entry points for current work.

## Next work

Collaborators should first read the current manuscript, the research/version audit and reproduction guide, then agree on scientific revisions before adding experiments. Venue compliance and submission readiness require a separate final review. No submission, invitation or collaborator access grant is implied by this repository creation.


## Formal-manuscript cleanup — 2026-10-18

Current Markdown and PDF exclude internal version/date/revision notes, invisible paragraph labels, and the unconfirmed final-author-approval sentence. The endpoint revision extends the scientific text, abstract and figures while preserving that cleanup. Historical frozen packages retain their originals. `05_AUDIT/manuscript_cleanup_receipt.json` checks the archived 22-page version; `validate_handoff.py` checks the current manuscript against `outputs/endpoint_revision/` as well as the historical packages.
