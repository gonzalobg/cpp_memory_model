/* C++23: well-defined, forbid(hang || returns(-1) || !returns(0)) */

#include <thread>
using namespace std;

volatile int a;

int main(void) {
    jthread t0([&]() {
        while(true) a = 1;
    });

    jthread t1([]() {
        exit(0);
    });

    return -1;
}
