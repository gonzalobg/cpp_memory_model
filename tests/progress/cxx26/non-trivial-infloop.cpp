/* C++26: undefined-behavior, allow(hang || returns(0) || returns(-1)) */

#include <thread>
using namespace std;

int main(void) {
    jthread thd1([]() {
        bool True = true;
        while(True);
    });

    jthread thd2([]() {
        exit(0);
    });

    return -1;
}
