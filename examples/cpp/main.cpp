#include <cstdio>
#include <iostream>
int main() {
    // Demo only: read-only discovery; run from examples/cpp.
#ifdef _WIN32
    FILE* p = _popen("skillbridge discover ../manifests", "r");
#else
    FILE* p = popen("skillbridge discover ../manifests", "r");
#endif
    if (!p) return 1;
    char buf[512];
    while (fgets(buf, sizeof(buf), p)) std::cout << buf;
#ifdef _WIN32
    return _pclose(p);
#else
    return pclose(p);
#endif
}
