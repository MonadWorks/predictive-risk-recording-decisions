# Graphical abstract — current v5

2026-10-18. Current version adds the exact key finding: **Better risk estimates do not necessarily make better recording decisions.**

The two equations move down together by about 2.1 mm relative to the previous preview. Their internal clearance stays about 1.6 mm; title clearance is about 5.8 mm. The title stays centered and aligned with the right key-finding baseline. Right-hand body spacing and the upper content are unchanged.

- `graphical_abstract.pdf/png/svg`: current formal assets.
- `graphical_abstract_v5.pdf/png/svg`: explicit version snapshot.
- `versions/v4_without_key_finding/`: complete previous asset/source snapshot without the key sentence.
- `source/render_graphical_abstract.py`: current portable rendering entry.
- `source/render_graphical_abstract_v4.py`: reused previous layout engine.
- `current_audit.json`, `verification.json`: current geometry, spacing and text checks.

Run `python source/render_graphical_abstract.py`; generated files go to `rendered/graphical_abstract_current.*` and do not overwrite formal snapshots. Use the same dependencies and fonts as the previous version. The old `audit_graphical_abstract.py` remains a v4-specific historical validator.

Scientific values and statistical geometry are unchanged. Manuscript PDF and the earlier collaborator ZIP have not been rebuilt for this standalone graphical abstract update.
