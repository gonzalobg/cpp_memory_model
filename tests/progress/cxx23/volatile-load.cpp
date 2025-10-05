/* C++23: well-defined, forbid(hang || returns(-1) || !return(0)) */

#include <thread>
using namespace std;

volatile int a;

int main(void) {
    jthread t0([&]() {
        while(true) (void)*(&a);
    });

    jthread t1([]() {
        exit(0);
    });

    return -1;
}
