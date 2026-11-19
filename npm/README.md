# SkillBridge npm wrapper (source preview)

This is a **wrapper** for the Python runtime, not a standalone native implementation. It is **not published on npm**.

```bash
python -m pip install -e .
cd npm
npm link
skillbridge connect TestApp --root ../examples/autodiscovery
```

After publishing `@jekodev/skillbridge` to npm, users could run `npx @jekodev/skillbridge ...`. The npm package name is illustrative until ownership and availability are verified.
