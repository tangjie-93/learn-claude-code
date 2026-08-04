import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');

const requiredFiles = [
  'package.json',
  'index.html',
  'vite.config.ts',
  'src/main.ts',
  'src/App.vue',
  'src/router/index.ts',
  'src/stores/app.ts',
  'src/views/HomeView.vue',
  'src/views/TimelineView.vue',
  'src/views/LayersView.vue',
  'src/views/CompareView.vue',
  'src/views/VersionView.vue',
  'src/data/generated/versions.json',
  'src/data/generated/docs.json',
];

for (const file of requiredFiles) {
  assert.ok(existsSync(resolve(root, file)), `missing ${file}`);
}

const router = readFileSync(resolve(root, 'src/router/index.ts'), 'utf8');
for (const path of ['/:locale(en|zh|ja)', '/:locale(en|zh|ja)/timeline', '/:locale(en|zh|ja)/compare', '/:locale(en|zh|ja)/layers', '/:locale(en|zh|ja)/:version(s\\\\d{2})']) {
  assert.ok(router.includes(path), `router missing ${path}`);
}

const versions = JSON.parse(readFileSync(resolve(root, 'src/data/generated/versions.json'), 'utf8'));
assert.equal(versions.versions.length, 20, 'expected 20 versions');
assert.equal(versions.versions[0].id, 's01');
assert.equal(versions.versions.at(-1).id, 's20');

const pkg = JSON.parse(readFileSync(resolve(root, 'package.json'), 'utf8'));
for (const dep of ['@vitejs/plugin-vue', 'vue', 'vue-router', 'pinia', 'less', 'typescript']) {
  assert.ok(pkg.dependencies?.[dep] || pkg.devDependencies?.[dep], `missing dependency ${dep}`);
}
