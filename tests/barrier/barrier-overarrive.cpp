/* C++23: undefined */

#include <barrier>
using namespace std;

int main(void) {
    barrier bar(1, []() { });

    auto t = bar.arrive();
    (void)bar.arrive();
    bar.wait(std::move(t));

    return 0;
}
