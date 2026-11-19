//! Stable C ABI for an in-process capability registry.
//! Callbacks must return strings allocated by sb_string_new.
use std::collections::BTreeMap;
use std::ffi::{c_char, c_void, CStr, CString};
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::ptr;
use std::sync::Mutex;

pub type SkillCallback = unsafe extern "C" fn(*const c_char, *mut c_void) -> *mut c_char;
#[derive(Clone, Copy)]
struct Entry { callback: SkillCallback, context: *mut c_void }
// The embedding application owns the context and must keep it alive until unregister/destroy.
unsafe impl Send for Entry {}
struct Registry { entries: Mutex<BTreeMap<String, Entry>> }

fn read_string(p: *const c_char) -> Option<String> {
    if p.is_null() { return None; }
    unsafe { CStr::from_ptr(p) }.to_str().ok().map(str::to_owned)
}
fn into_raw(s: String) -> *mut c_char {
    CString::new(s).map(CString::into_raw).unwrap_or(ptr::null_mut())
}

#[no_mangle]
pub extern "C" fn sb_version() -> *const c_char { b"0.8.0\0".as_ptr() as *const c_char }

#[no_mangle]
pub extern "C" fn sb_create() -> *mut c_void {
    Box::into_raw(Box::new(Registry { entries: Mutex::new(BTreeMap::new()) })) as *mut c_void
}

/// The caller must not use the registry concurrently with destruction.
#[no_mangle]
pub unsafe extern "C" fn sb_destroy(handle: *mut c_void) {
    if !handle.is_null() { drop(Box::from_raw(handle as *mut Registry)); }
}

/// Returns 0 on success, -1 on invalid input, -2 on internal failure.
#[no_mangle]
pub unsafe extern "C" fn sb_register(handle: *mut c_void, name: *const c_char, callback: Option<SkillCallback>, context: *mut c_void) -> i32 {
    catch_unwind(AssertUnwindSafe(|| {
        let (Some(reg), Some(name), Some(callback)) = ((handle as *mut Registry).as_ref(), read_string(name), callback) else { return -1 };
        if name.is_empty() || name.len() > 256 { return -1; }
        match reg.entries.lock() { Ok(mut entries) => { entries.insert(name, Entry { callback, context }); 0 }, Err(_) => -2 }
    })).unwrap_or(-2)
}

#[no_mangle]
pub unsafe extern "C" fn sb_unregister(handle: *mut c_void, name: *const c_char) -> i32 {
    catch_unwind(AssertUnwindSafe(|| {
        let (Some(reg), Some(name)) = ((handle as *mut Registry).as_ref(), read_string(name)) else { return -1 };
        match reg.entries.lock() { Ok(mut entries) => if entries.remove(&name).is_some() { 0 } else { 1 }, Err(_) => -2 }
    })).unwrap_or(-2)
}

/// Returns a JSON array of capability names. Caller frees via sb_string_free.
#[no_mangle]
pub unsafe extern "C" fn sb_list(handle: *mut c_void) -> *mut c_char {
    catch_unwind(AssertUnwindSafe(|| {
        let Some(reg) = (handle as *mut Registry).as_ref() else { return ptr::null_mut() };
        let Ok(entries) = reg.entries.lock() else { return ptr::null_mut() };
        let names: Vec<String> = entries.keys().map(|name| format!("\"{}\"", escape_json(name))).collect();
        into_raw(format!("[{}]", names.join(",")))
    })).unwrap_or(ptr::null_mut())
}
fn escape_json(s: &str) -> String {
    let mut out = String::new();
    for c in s.chars() { match c { '"' => out.push_str("\\\""), '\\' => out.push_str("\\\\"), '\n' => out.push_str("\\n"), '\r' => out.push_str("\\r"), '\t' => out.push_str("\\t"), c if c <= '\u{1f}' => out.push_str(&format!("\\u{:04x}", c as u32)), c => out.push(c) } }
    out
}

/// Returns NULL for unknown skills or invalid input. The callback is responsible for validating JSON.
/// Do not unregister/destroy a callback's context while a call is in progress.
#[no_mangle]
pub unsafe extern "C" fn sb_call(handle: *mut c_void, name: *const c_char, json: *const c_char) -> *mut c_char {
    catch_unwind(AssertUnwindSafe(|| {
        let (Some(reg), Some(name)) = ((handle as *mut Registry).as_ref(), read_string(name)) else { return ptr::null_mut() };
        if json.is_null() { return ptr::null_mut(); }
        let entry = match reg.entries.lock() { Ok(entries) => entries.get(&name).copied(), Err(_) => None };
        match entry { Some(e) => (e.callback)(json, e.context), None => ptr::null_mut() }
    })).unwrap_or(ptr::null_mut())
}

#[no_mangle]
pub extern "C" fn sb_string_new(s: *const c_char) -> *mut c_char {
    read_string(s).map(into_raw).unwrap_or(ptr::null_mut())
}
#[no_mangle]
pub unsafe extern "C" fn sb_string_free(s: *mut c_char) {
    if !s.is_null() { drop(CString::from_raw(s)); }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn json_escaping() { assert_eq!(escape_json("a\"\\\n"), "a\\\"\\\\\\n"); }
    #[test] fn registry_roundtrip() {
        unsafe extern "C" fn echo(input: *const c_char, _: *mut c_void) -> *mut c_char { sb_string_new(input) }
        unsafe {
            let h=sb_create(); let n=CString::new("echo").unwrap(); let data=CString::new("{\"x\":1}").unwrap();
            assert_eq!(sb_register(h,n.as_ptr(),Some(echo),ptr::null_mut()),0);
            let names=sb_list(h); assert_eq!(CStr::from_ptr(names).to_str().unwrap(),"[\"echo\"]"); sb_string_free(names);
            let output=sb_call(h,n.as_ptr(),data.as_ptr()); assert_eq!(CStr::from_ptr(output).to_str().unwrap(),"{\"x\":1}"); sb_string_free(output);
            assert_eq!(sb_unregister(h,n.as_ptr()),0); sb_destroy(h);
        }
    }
}
