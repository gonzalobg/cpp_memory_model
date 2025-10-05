/* C++23: well-defined, forbid(!hang || returns(0)) */

#include <thread>
using namespace std;
volatile unsigned x;

int main(void) {
    jthread t0([]() {
      x = x + 1;
    });

    return -1;
}
