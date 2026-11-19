// Node 18+; language-neutral CLI integration (no npm dependency).
import { execFileSync } from 'node:child_process';
const manifest = '../manifests';
const result = execFileSync('skillbridge', ['discover', manifest], { encoding: 'utf8', cwd: new URL('.', import.meta.url) });
console.log(JSON.parse(result).skills);
