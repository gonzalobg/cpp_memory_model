/* C++23: forbid(hang) */

#include <thread>

int main(void) {
    std::jthread thd([]() {
        std::exit(0);
    });

    return -1;
}
