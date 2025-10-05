/* C++23: well-defined, forbid(hang || returns(-1) || !return(0)) */

#include <atomic>
#include <thread>
using namespace std;

atomic<int> a;

int main(void) {
    jthread t0([&]() {
        while(true) (void)atomic_load_explicit(&a, memory_order_relaxed);
    });

    jthread t1([]() {
        exit(0);
    });

    return -1;
}
