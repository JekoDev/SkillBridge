// Optional Node FFI example: npm install koffi
// Build native/ first. Koffi loads the platform-specific shared library.
import koffi from 'koffi';
import path from 'node:path';
const libName = process.platform === 'win32' ? 'skillbridge_native.dll' :
  process.platform === 'darwin' ? 'libskillbridge_native.dylib' : 'libskillbridge_native.so';
const lib = koffi.load(path.resolve('native/target/release', libName));
const create = lib.func('void* sb_create(void)');
const destroy = lib.func('void sb_destroy(void*)');
const list = lib.func('void* sb_list(void*)');
const free = lib.func('void sb_string_free(void*)');
const handle = create();
try {
  const p = list(handle);
  console.log(koffi.decode(p, 'char', -1));
  free(p);
} finally { destroy(handle); }
