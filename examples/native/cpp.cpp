#include "skillbridge.h"
#include <iostream>
static char* echo(const char* json, void*) { return sb_string_new(json); }
int main() {
    void* bridge = sb_create();
    if (!bridge || sb_register(bridge, "echo", echo, nullptr) != 0) return 1;
    char* result = sb_call(bridge, "echo", "{\"hello\":\"Forge\"}");
    if (result) { std::cout << result << "\n"; sb_string_free(result); }
    sb_destroy(bridge);
}
