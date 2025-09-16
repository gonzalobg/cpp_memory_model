/* C++23: allow(hang) */
/* C++20: allow(hang) */

#include <thread>
#include <atomic>


int main(void) {
    std::jthread thd1([]() {
        int x = 0;
        while(true) { 
            #pragma clang diagnostic push
            #pragma clang diagnostic ignored "-Wunused-value"
            *(&x);
            #pragma clang diagnostic pop
        }
    });

    std::jthread thd2([]() {
        std::exit(0);
    });
    
    return -1;
}
