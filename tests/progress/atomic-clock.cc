/* C++23: forbid(hang) */
/* C++29: allow(hang) proposed */

#include <thread>
#include <atomic>

std::atomic<int> clk;

int main(void) {
    std::jthread thd1([&]() {
        int local_clk = 0;
        while(true) {
            clk.store(local_clk++, std::memory_order_relaxed);
        }
    });

    std::jthread thd2([]() {
        std::exit(0);
    });
    
    return -1;
}
