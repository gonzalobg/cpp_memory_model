/* C++23: well-defined, forbid(hang || returns(-1) || !return(0)) */

#include <atomic>
#include <thread>
using namespace std;

int main(void) {
    jthread t0([&]() {
      while(true) atomic_thread_fence(memory_order_acq_rel);
    });

    jthread t1([]() {
        exit(0);
    });

    return -1;
}
