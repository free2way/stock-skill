# OpenClaw Install

This repository includes an OpenClaw-compatible package at:

- `openclaw/growth-stock-research/`

## Install options

Option 1: copy the skill into your OpenClaw skills directory

```bash
mkdir -p ~/.openclaw/skills
cp -R openclaw/growth-stock-research ~/.openclaw/skills/
```

Option 2: if your OpenClaw setup supports loading skills from a workspace path, point it at:

```text
openclaw/growth-stock-research
```

## Notes

- This package is adapted from the Codex-oriented version under `skills/growth-stock-research/`.
- The OpenClaw version keeps the same scripts, references, and sample data, but the `SKILL.md` is simplified and uses `{baseDir}`-style references.
- The package is self-contained and can be copied directly.
