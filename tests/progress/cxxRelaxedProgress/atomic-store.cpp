/* C++RelaxedProgress: well-defined, allows(hang), forbid(returns(-1) || !returns(0)) */

#include <atomic>
#include <thread>
using namespace std;

atomic<int> a;

int main(void) {
    jthread t0([&]() {
        while(true) atomic_store_explicit(&a, 1, memory_order_relaxed);
    });

    jthread t1([]() {
        exit(0);
    });

    return -1;
}
