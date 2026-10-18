# science-plot-formatter

A Claude Code and Codex skill that beautifies matplotlib scripts for scientific paper submission.

## Example

<table align="center">
  <tr>
    <td align="center" width="50%"><img src="assets/before.png" width="100%" /></td>
    <td align="center" width="50%"><img src="assets/after.png" width="100%" /></td>
  </tr>
  <tr>
    <td align="center"><b>Before</b></td>
    <td align="center"><b>After</b></td>
  </tr>
</table>

## What it does

Given an existing `.py` plotting script, a target conference/journal, and the figure's fraction of column width on the page, the skill renders the chart, inspects it critically, rewrites the visual system (figsize, fonts, linewidths, markers, ticks, legend weight), and re-renders to verify the result. It always renders **before** editing and **again after** editing — no code is rewritten from equations alone.

## Skill

- **`beautify-chart`** — the render → inspect → rewrite → re-render → verify loop. The skill looks up the venue's official author guidelines live (column width, body font size, required font family) and derives the target visual system from the figure's final physical width on the page, not from the current code values.

## Installation

This repository ships two equivalent skill definitions:

- Claude Code: `.claude/skills/beautify-chart/SKILL.md`
- Codex: `.codex/skills/beautify-chart/SKILL.md`

### Claude Code

> The instructions below install the skill **only into the project you run them in**. User-level installation (making the skill available in every project on your machine) is intentionally not covered here.

#### Option A — Clone and copy the skill folder (recommended)

```bash
# 1. Get the repo (anywhere outside your project)
git clone https://github.com/preordinary/science-plot-formatter.git

# 2. From your own project's root, copy the skill in
mkdir -p .claude/skills
cp -r /path/to/science-plot-formatter/.claude/skills/beautify-chart .claude/skills/
```

To update later, `git pull` inside the clone and re-run the `cp -r` (it overwrites).

#### Option B — Download the single SKILL.md file

If you do not want to clone the repo:

```bash
mkdir -p .claude/skills/beautify-chart
curl -fsSL -o .claude/skills/beautify-chart/SKILL.md \
  https://raw.githubusercontent.com/preordinary/science-plot-formatter/main/.claude/skills/beautify-chart/SKILL.md
```

This grabs just the skill file. You lose the `git pull` update path — re-run the `curl` to refresh.

#### Verify the install

After installation your project should contain:

```
your-project/
└── .claude/
    └── skills/
        └── beautify-chart/
            └── SKILL.md
```

Start (or restart) Claude Code in that project and ask it to "beautify a matplotlib script for NeurIPS". The `beautify-chart` skill should be invoked.

#### Uninstall

```bash
rm -rf .claude/skills/beautify-chart
```

### Codex

Codex skills are installed as skill folders under `$CODEX_HOME/skills` (usually `~/.codex/skills`). Copy the Codex-adapted skill folder there:

```bash
# 1. Get the repo (anywhere outside your project)
git clone https://github.com/preordinary/science-plot-formatter.git

# 2. Install for Codex
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -r /path/to/science-plot-formatter/.codex/skills/beautify-chart \
  "${CODEX_HOME:-$HOME/.codex}/skills/"
```

After installation, restart Codex and ask it to use `$beautify-chart` on a matplotlib script.

To uninstall:

```bash
rm -rf "${CODEX_HOME:-$HOME/.codex}/skills/beautify-chart"
```

## Usage

Ask Claude Code or Codex something like:

> Beautify `path/to/plot.py` for NeurIPS 2026. It's one full column wide.

The skill will:

1. Look up NeurIPS 2026 author guidelines (column width, body pt).
2. Render the script headlessly (`MPLBACKEND=Agg`) and read the PNG.
3. List concrete visual issues at the target page width.
4. Propose a unified `plt.rcParams.update({...})` block plus per-call fixes (errorbar `capsize`/`capthick`, stale kwargs removed).
5. Apply the edits, re-render, and verify each listed issue is resolved.

Data, colors, colormaps, linestyles, axis limits, and the user's composition are never touched.

## Inputs

| Input | Example |
|---|---|
| `script_path` | `/path/to/plot.py` |
| `venue` | `NeurIPS 2026`, `Nature Communications`, `ICML 2026` |
| `fraction` | `0.5` (half column), `1.0` (one column), `2.0` (double columns) |

You do not need to supply column widths or body font sizes — the skill looks them up from the venue.

## Requirements

- Python with `matplotlib` installed on the machine running Claude Code or Codex.
- The user's script must be runnable end-to-end (data loadable from the script's working directory).
