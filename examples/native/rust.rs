// Example using the Rust crate directly (in a separate Cargo project):
// skillbridge_native is the native crate; its public API is the C ABI.
use std::ffi::{CStr, CString};
use std::ptr;
use skillbridge_native::{sb_create, sb_destroy, sb_register, sb_call, sb_string_new, sb_string_free};
unsafe extern "C" fn echo(s: *const std::ffi::c_char, _: *mut std::ffi::c_void) -> *mut std::ffi::c_char { sb_string_new(s) }
fn main() {
    unsafe {
        let h = sb_create();
        let name = CString::new("echo").unwrap();
        let json = CString::new("{\"hello\":\"Forge\"}").unwrap();
        assert_eq!(sb_register(h, name.as_ptr(), Some(echo), ptr::null_mut()), 0);
        let out = sb_call(h, name.as_ptr(), json.as_ptr());
        println!("{}", CStr::from_ptr(out).to_string_lossy());
        sb_string_free(out); sb_destroy(h);
    }
}
