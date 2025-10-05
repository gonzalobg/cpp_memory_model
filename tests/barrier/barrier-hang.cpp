/* C++23: well-defined, forbid(!hang || returns(0)) */

#include <barrier>
using namespace std;

int main(void) {
    barrier bar(2, []() { });

    bar.arrive_and_wait();
    (void)bar.arrive();

    return 0;
}
