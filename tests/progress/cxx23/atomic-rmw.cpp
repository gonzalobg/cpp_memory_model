/* C++23: well-defined, forbid(hang || returns(-1) || !returns(0)) */

#include <atomic>
#include <thread>
using namespace std;

atomic<int> a = 0;

int main(void) {
    jthread t0([&]() {
        while(true) atomic_fetch_add_explicit(&a, 0, memory_order_relaxed);
    });

    jthread t1([]() {
        exit(0);
    });

    return -1;
}
