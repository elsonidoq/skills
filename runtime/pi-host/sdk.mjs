// Resolve the Pi SDK without starting the workflow transport.
import { existsSync, readFileSync } from 'node:fs';
import { homedir } from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const SDK_PACKAGE = '@earendil-works/pi-coding-agent';
const SDK_ENTRY = ['node_modules', ...SDK_PACKAGE.split('/'), 'dist', 'index.js'];

function sdkEntry() {
  const local = path.join(path.dirname(fileURLToPath(import.meta.url)), ...SDK_ENTRY);
  if (existsSync(local)) return local;

  const packageDir = process.env.PI_PACKAGE_DIR;
  if (packageDir) return path.join(packageDir, 'dist', 'index.js');

  const defaultAgentDir = path.join(homedir(), '.pi', 'agent');
  for (const agentDir of new Set([process.env.PI_CODING_AGENT_DIR, defaultAgentDir].filter(Boolean))) {
    const versionFile = path.join(agentDir, 'install', 'current-version');
    if (!existsSync(versionFile)) continue;
    const version = readFileSync(versionFile, 'utf8').trim();
    if (version) return path.join(agentDir, 'install', 'releases', version, ...SDK_ENTRY);
  }
  throw new Error(`Pi SDK unavailable: install ${SDK_PACKAGE}, or run the explicit isolated workflow setup.`);
}

// An explicit isolated workflow install keeps its lockfile-resolved SDK beside
// this host. Source worktrees instead reuse Pi's installed SDK, which is not
// copied into every Git worktree.
const piSdkEntry = sdkEntry();
export const piSdkPackageDir = path.dirname(path.dirname(piSdkEntry));
export const piSdk = await import(pathToFileURL(piSdkEntry).href);
