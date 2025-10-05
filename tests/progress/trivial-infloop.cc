/* C++23: forbid(hang) */
/* C++20: allow(hang) */

#include <thread>
#include <atomic>


int main(void) {
    std::jthread thd1([]() {
        while(true) {}
    });

    std::jthread thd2([]() {
        std::exit(0);
    });
    
    return -1;
}
