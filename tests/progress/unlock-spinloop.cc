/* C++23: forbid(hang) */

#include <thread>
#include <atomic>

std::atomic<int> lock;

int main(void) {
    std::jthread thd([]() {
        lock.store(1, std::memory_order_relaxed);
    });

    std::jthread thd2([]() {
        while(lock.load(std::memory_order_relaxed) == 0) {}
        std::exit(0);
    });

    return -1;
}
