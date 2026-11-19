#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
const python = process.env.SKILLBRIDGE_PYTHON || (process.platform === 'win32' ? 'py' : 'python3');
const args = process.platform === 'win32' && !process.env.SKILLBRIDGE_PYTHON ? ['-3', '-m', 'skillbridge.cli', ...process.argv.slice(2)] : ['-m', 'skillbridge.cli', ...process.argv.slice(2)];
const result = spawnSync(python, args, { stdio: 'inherit', shell: false });
if (result.error) {
  console.error(`SkillBridge: could not start ${python}. Install the Python runtime first: python -m pip install skillbridge-ai`);
  process.exit(1);
}
process.exit(result.status ?? 1);
