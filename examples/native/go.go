//go:build cgo
// Run with CGO_ENABLED=1 and linker search path set to native/target/release.
package main
/*
#cgo CFLAGS: -I../../native/include
#cgo linux LDFLAGS: -L../../native/target/release -lskillbridge_native
#cgo darwin LDFLAGS: -L../../native/target/release -lskillbridge_native
#cgo windows LDFLAGS: -L../../native/target/release -lskillbridge_native
#include <stdlib.h>
#include "skillbridge.h"
static char* echo(const char* input, void* ctx) { return sb_string_new(input); }
static int register_echo(void* h) { return sb_register(h, "echo", echo, NULL); }
*/
import "C"
import "fmt"
import "unsafe"
func main() {
    h := C.sb_create()
    defer C.sb_destroy(h)
    if C.register_echo(h) != 0 { panic("register failed") }
    name := C.CString("echo"); defer C.free(unsafe.Pointer(name))
    input := C.CString(`{"hello":"Forge"}`); defer C.free(unsafe.Pointer(input))
    out := C.sb_call(h, name, input)
    if out == nil { panic("call failed") }
    fmt.Println(C.GoString(out))
    C.sb_string_free(out)
}
