/* C++23: well-defined, forbid(hang || returns(-1) || !returns(0)) */

#include <atomic>
#include <thread>
using namespace std;

atomic<int> lock;

int main(void) {
    jthread t0([]() {
        atomic_store_explicit(&lock, 1, memory_order_relaxed);
    });

    jthread t1([]() {
        while(atomic_load_explicit(&lock, memory_order_relaxed) == 0) {}
        exit(0);
    });

    return -1;
}
