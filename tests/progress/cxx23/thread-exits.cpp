/* C++23: well-defined, forbid(hang || returns(-1)) */

#include <thread>
using namespace std;

int main(void) {
    jthread t0([]() {
        exit(0);
    });

    return -1;
}
