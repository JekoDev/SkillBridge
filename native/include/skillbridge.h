#ifndef SKILLBRIDGE_H
#define SKILLBRIDGE_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* All input strings are UTF-8, NUL-terminated. Callback results MUST be
   allocated using sb_string_new; consumers free results via sb_string_free. */
typedef char* (*sb_callback)(const char* json_input, void* context);
const char* sb_version(void);
void* sb_create(void);
void sb_destroy(void* handle);
int32_t sb_register(void* handle, const char* name, sb_callback callback, void* context);
int32_t sb_unregister(void* handle, const char* name);
char* sb_list(void* handle);
char* sb_call(void* handle, const char* name, const char* json_input);
char* sb_string_new(const char* value);
void sb_string_free(char* value);
#ifdef __cplusplus
}
#endif
#endif
