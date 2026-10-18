# 参考文献核查报告 / References audit (paper_v4.md, refs 1-17)

Audit date: 2026-10-17. Output: `05_data_and_code/references.bib` (keys `ref01`-`ref17` in the manuscript's order; `ref18`-`ref25` are suggested additions). `paper_v4.md` was not modified.

## 方法 / Method

- Every DOI was resolved against the Crossref REST API (title, authors, journal, volume, issue, article number or pages, date). eLife status was also checked against the eLife API. Krause et al. was checked on the JMLR page.
- Only fields returned by these registries are in the .bib. No DOI was invented.
- Limits: the Nature/IEEE publisher pages were not reachable by the fetch tool (redirect to login), so those entries are verified by Crossref only. Content claims (whether a paper supports the sentence citing it) were spot-checked only where an abstract was available (see column "Claim check").

## 1. 逐条核查状态 / Per-reference status

| # | Status | Findings / corrections |
|---|---|---|
| 1 | Verified | Matches. Missing in manuscript: vol 8, issue 74 (25 Jan 2023). 21 authors; first author Kim Y (Yongdeok). |
| 2 | Verified | Matches. Add vol 10, issue 106 (3 Sep 2025). 21 authors. |
| 3 | Verified | Matches (Biomimetics 10(6), 359, 2025). First author Wang Xingchen. Claim check: the abstract describes an image-to-pulse stimulation encoding validated by unsupervised training and image recognition on in vitro networks. The manuscript's "support decoding of responses to patterned electrical inputs" is a loose paraphrase; consider "encoding of visual information into patterned stimulation and recognition from the evoked activity". |
| 4 | Verified | Add vol 7(12), 1345-1352, 2004. |
| 5 | Verified | Add vol 28(12), 2561-2574, 2025 (online 27 Oct 2025). Claim check: the preprint abstract (bioRxiv 10.1101/2024.02.22.581667) states that recordings from a small neuron subset resolve connectome degeneracy and that theory prioritises which neurons to record; this supports the Introduction sentence. |
| 6 | Verified | Add vol 634(8036), 1132-1140, 2024. |
| 7 | Verified | Journal name is IEEE Transactions on Control of Network Systems; add vol 5(2), 694-708, June 2018. Claim check (observability vs. practical estimation accuracy): NOT checked, IEEE page not reachable. |
| 8 | Verified, wording fixed | "formal version 3" is not standard. The eLife API lists this as status `vor` (Version of Record), published 16 Jan 2026, eLife 14:RP106827; DOI suffix `.3` is the VoR DOI. |
| 9 | Verified, version flag | An eLife Reviewed Preprint, not a journal article (Crossref type: posted-content; no volume or pages). Version 1 is dated 9 Mar 2026. The eLife API and Crossref show a version 2 (10.7554/eLife.110030.2, 9 Sep 2026). Authors: Ogino M, Sekizawa D, Kitazono J, Oizumi M. Decide whether to cite v1 (as now) or update to v2. |
| 10 | Verified | Add vol 34(9), 095009, 2018. |
| 11 | Verified, completed | "Zhong et al." should be Zhong S, Shen W, Catanach T, Huan X. SIAM/ASA JUQ 14(1), 19-47, 2026. |
| 12 | Verified | Add vol 6, article 120, 2012. |
| 13 | Verified | Matches (12(12), e1005227, 6 Dec 2016); 6 authors, first author White A. |
| 14 | Verified | Matches; add issue 477 (JASA 102:359-378, 2007). |
| 15 | Verified, completed | Manuscript lists no authors. Waltemath D et al. (28 authors). PLoS Comput Biol 7(4), e1001122, 2011. Full title: "Minimum Information About a Simulation Experiment (MIASE)". |
| 16 | Verified, completed | No authors in manuscript. Walsh I et al. (group author ELIXIR Machine Learning Focus Group). Nature Methods 18(10), 1122-1127, 2021. |
| 17 | Verified, completed | No authors in manuscript. Macleod M et al. PNAS 118(17), e2103238118, 2021. Full title: "The MDAR (Materials Design Analysis Reporting) Framework for transparent reporting in the life sciences"; "The MDAR Framework" is a shortened title. |

Not verified: nothing in refs 1-17 failed to resolve. Unchecked items are the content-support claims noted above (refs 1, 2, 7, 8, 9, 10, 11, 12, 13 were not read against the sentences citing them), and publisher-page confirmation for Nature/IEEE entries.

## 2. 对稿件引用文本的修改清单 / Corrections to the manuscript's citation text

(Suggested only; the manuscript itself was not edited.)

1. Ref 1: add "8(74)".
2. Ref 2: add "10(106)".
3. Ref 4: add "7(12), 1345-1352 (2004)".
4. Ref 5: add "28(12), 2561-2574 (2025)".
5. Ref 6: add "634, 1132-1140 (2024)".
6. Ref 7: "IEEE TCNS" -> "IEEE Transactions on Control of Network Systems 5(2), 694-708 (2018)".
7. Ref 8: replace "formal version 3 (2026)" with "eLife 14, RP106827 (2026), Version of Record".
8. Ref 9: state it is an eLife Reviewed Preprint; consider updating to v2 (10.7554/eLife.110030.2, Sep 2026).
9. Ref 10: add "34(9), 095009".
10. Ref 11: "Zhong et al." -> "Zhong S, Shen W, Catanach T, Huan X"; add "14(1), 19-47".
11. Ref 12: add "6, 120".
12. Ref 14: add issue "(477)".
13. Refs 15-17: add author lists (Waltemath D et al.; Walsh I et al.; Macleod M et al.), journal names, years, volumes, article numbers; use the full titles above.
14. Ref 3 claim wording: see table row 3.

The in-text numbering ([1,2], [3], [4]-[9], [10], [11], [12], [13], [14], [15,16,17]) matches the reference list order; no re-numbering is needed. Note that `05_data_and_code/citation_number_map.json` records a previous-to-current mapping (including a removed "Pickard 2025" and "Apgar 2010"); it was not changed and these are not in the .bib.

## 3. 建议新增引用 / Suggested additional references (ref18-ref25)

All eight were confirmed to exist via Crossref (ref25 via the JMLR page; JMLR issues no DOI, so none is given).

| Key | Reference | Would support (sentence / location) |
|---|---|---|
| ref18 | Chaloner K, Verdinelli I. Bayesian Experimental Design: A Review. *Stat Sci* 10(3):273-304 (1995). 10.1214/ss/1177009939 | Intro I4, "Goal-oriented experimental design provides established criteria for valuing observations according to a quantity of interest": the classic decision-theoretic background (A-, c-optimal, expected utility). |
| ref19 | Ryan EG, Drovandi CC, McGree JM, Pettitt AN. A Review of Modern Computational Algorithms for Bayesian Optimal Design. *Int Stat Rev* 84(1):128-154 (2016; Crossref online date 2015). 10.1111/insr.12107 | Intro I4, "A nominal-parameter approximation is inexpensive; ... more complete nonlinear approaches ...": review of computational routes to expected utility. |
| ref20 | Rainforth T, Foster A, Ivanova DR, Bickford Smith F. Modern Bayesian Experimental Design. *Stat Sci* 39(1):100-114 (2024). 10.1214/23-STS915 | Intro I4 / Discussion D3, "more complete nonlinear approaches" and the suggestion of integrating posteriors accurately in small models. |
| ref21 | Alexanderian A, Petra N, Stadler G, Ghattas O. A Fast and Scalable Method for A-Optimal Design of Experiments for Infinite-Dimensional Bayesian Nonlinear Inverse Problems. *SIAM J Sci Comput* 38(1):A243-A272 (2016). 10.1137/140992564 | Intro I4, "averaging local criteria over a parameter ensemble": A-optimal design with a local linearisation and prior-averaging for nonlinear models. |
| ref22 | Huan X, Marzouk YM. Simulation-based optimal Bayesian experimental design for nonlinear systems. *J Comput Phys* 232(1):288-317 (2013). 10.1016/j.jcp.2012.08.013 | Discussion D3, "Local risk may differ from actual response error ...": a non-local (simulation-based) benchmark against which local risk could be compared. |
| ref23 | Raue A, Kreutz C, Maiwald T, Bachmann J, Schilling M, Klingmueller U, Timmer J. Structural and practical identifiability analysis of partially observed dynamical models by exploiting the profile likelihood. *Bioinformatics* 25(15):1923-1929 (2009). 10.1093/bioinformatics/btp358 | Discussion D3, next to ref 12 ("Prediction-profile approaches ..."): profile-likelihood identifiability under partial observation. |
| ref24 | Lindley DV. On a Measure of the Information Provided by an Experiment. *Ann Math Stat* 27(4):986-1005 (1956). 10.1214/aoms/1177728069 | Intro I4: origin of the expected-information-gain design criterion that A-/c-optimal criteria are contrasted with. |
| ref25 | Krause A, Singh A, Guestrin C. Near-Optimal Sensor Placements in Gaussian Processes. *J Mach Learn Res* 9:235-284 (2008). No DOI. | Intro I3 (sensor selection) and Methods on greedy selection of recording sets under a budget. |

Considered and dropped: Manohar et al. 2018 (IEEE Control Syst Mag 38(3):63-86, DOI 10.1109/MCS.2018.2810460). The DOI and title exist in Crossref, but Crossref returns no author list and I could not verify the authors from a second source, so it was not added.
Also not added (beyond the cap of 8): Gneiting & Katzfuss 2014 (probabilistic forecasting review), Gutenkunst et al. 2007 (universally sloppy parameter sensitivities); neither was searched, so neither is verified here.
