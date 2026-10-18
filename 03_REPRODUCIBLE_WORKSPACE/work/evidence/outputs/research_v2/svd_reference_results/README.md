# Independent linear reference calibration

This is a calibration of the published normalized-row/SVD selection criterion, not a reproduction of Fig. 8 and not a new scientific result. It must not be ranked directly against the main finite-time softplus experiment: here observations are noiseless internal state and the only unknown is additive bias.

Source: Beiran & Litwin-Kumar (2025), https://doi.org/10.1038/s41593-025-02080-4 ; fixed repository commit and source-file hash are in report.json. Code is independently implemented; no upstream source is copied.

We deliberately construct stable symmetric rank-30 networks with eigenvalues from 0.08 to 0.82 (N=100). Thus continuous dynamics -x+J(x+b) are stable and steady state is x=(I-J)^-1 J b. This construction is our adaptation, not the paper's network distribution. Isotropic b and exact observations make the orthogonal projection risk exact. Selected rows retain original neuron IDs.

Greedy uses the published normalized residual-row score and orthogonal-complement update. For random sampling, each of 20 independent random permutations supplies all five nested budgets. There are 12 independent networks. A separate random stream generates 2,048 full N-dimensional Gaussian bias draws per network; these are reused across methods for paired evaluation, never for selection. Full x vectors are explicitly reconstructed using the exact Gaussian conditional mean. The analytic risk is compared with Monte Carlo MSE, with its exact sampling standard error. The primary independent unit is the network. The curve shading is ±1 network SEM, not a confidence interval or 20×12 independent networks.

Checks include dense solve versus independent low-rank einsum evaluation, finite matmul output versus einsum, first selection against full A SVD, observation interpolation, and projection idempotence. Platform matmul warnings, if any, are re-emitted and recorded in report.json; they are not suppressed. Main numerical products use a separate einsum kernel.

Run from workspace root:
```sh
MPLCONFIGDIR=work/research_v2/svd_reference_results/mpl-cache work/research-v2-env/bin/python work/research_v2/svd_reference.py
```
Dependencies are preinstalled in the stated venv; this script installs nothing. Exact versions, hashes and measured runtime are in report.json. CSVs retain all network/random-set/budget measurements, including individual selected IDs. The PNG and vector PDF show analytic curves, Monte Carlo estimates and network-level variability.
