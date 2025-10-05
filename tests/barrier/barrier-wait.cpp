/* C++23: well-defined, forbid(hang || !returns(0)) */

#include <barrier>
#include <thread>
using namespace std;

int main(void) {
    barrier bar(2, []() { });

    jthread t0([&bar]() {
        bar.arrive_and_wait();
    });

    jthread t1([&bar]() {
        bar.arrive_and_wait();
    });
    
    return 0;
}
