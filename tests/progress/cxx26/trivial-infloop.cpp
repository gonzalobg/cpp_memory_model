/* C++26: well-defined, forbid(hang || returns(1) || !returns(0)) */

#include <atomic>
#include <thread>
using namespace std;

int main(void) {
    jthread thd1([]() {
        while(true);
    });

    jthread thd2([]() {
        exit(0);
    });

    return -1;
}
