# SkillBridge v0.9.0 update overlay

This is a **patch ZIP**, not a full source repository. Based on the supplied SkillBridge v0.8.0 source archive. It adds a conservative `inspect-project` command and an agent skill for integrating SkillBridge into other applications. It does **not** autonomously modify foreign projects or provide new integration adapters.

Files overwritten: `src/skillbridge/cli.py` (based on v0.8.0). Files added: `src/skillbridge/project_inspect.py`, `tests/test_project_inspect.py`, marketplace skill and listing.

**Important:** Do not apply to a newer or modified CLI without reviewing the diff. The updater refuses if your current CLI does not match the supplied v0.8.0 baseline. No package version bump or PyPI publication is performed automatically.

Run `python -m skillbridge.cli inspect-project .` after installing the updated package (`python -m pip install -e .`).
