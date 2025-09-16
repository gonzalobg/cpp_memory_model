/* C++23: forbid(hang) */

#include <thread>
#include <barrier>


int main(void) {
    std::barrier bar(2, []() { });

    std::jthread thd1([&bar]() {
        bar.arrive_and_wait();
    });

    std::jthread thd2([&bar]() {
        bar.arrive_and_wait();
    });
    
    return 0;
}
