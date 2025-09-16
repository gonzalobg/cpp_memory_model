/* C++23: forbid(hang) */
/* C++29: allow(hang) proposed */

#include <thread>
#include <atomic>

std::atomic<int> clk;

int main(void) {
    std::jthread thd1([&]() {
        while(true) {
            #pragma clang diagnostic push
            #pragma clang diagnostic ignored "-Wunused-value"
            clk.load(std::memory_order_relaxed);
            #pragma clang diagnostic pop
        }
    });

    std::jthread thd2([]() {
        std::exit(0);
    });
    
    return -1;
}
