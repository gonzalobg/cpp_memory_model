/* C++23: forbid(hang) */

#include <thread>
#include <atomic>

volatile int x;

int main(void) {
    std::jthread thd1([&]() {
        while(true) { 
            x = 1;
        }
    });

    std::jthread thd2([]() {
        std::exit(0);
    });
    
    return -1;
}
