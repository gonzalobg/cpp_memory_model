/* C++23: well-defined, forbid(hang || !returns(0)) */

#include <barrier>
using namespace std;

int main(void) {
    barrier bar(2, []() { });

    (void)bar.arrive();
    bar.arrive_and_wait();

    return 0;
}
