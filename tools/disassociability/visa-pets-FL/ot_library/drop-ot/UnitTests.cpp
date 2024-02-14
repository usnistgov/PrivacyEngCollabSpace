#include "UnitTests.h"
#include "IknpOtExt.h"
#include "MasnyRindal.h"

namespace dropOt
{
    oc::TestCollection unitTests([](oc::TestCollection& tests) {
        tests.add("Bot_MasnyRindal_Buff_test      ", tests::Bot_MasnyRindal_Buff_test);
        tests.add("OtExt_Iknp_Buff_test            ", tests::OtExt_Iknp_Buff_test);
        });
}