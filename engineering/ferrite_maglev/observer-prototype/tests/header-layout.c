#include "../include/osr_normal_wrench_observer.h"
#include <stddef.h>
_Static_assert(sizeof(OsrObserverConfig) == 64, "config ABI");
_Static_assert(sizeof(OsrObserverState) == 88, "state ABI");
_Static_assert(sizeof(OsrObserverGroup) == 160, "group ABI");
_Static_assert(sizeof(OsrObserverFrame) == 33320, "frame ABI");
_Static_assert(sizeof(OsrObserverInput) == 33472, "input ABI");
_Static_assert(sizeof(OsrObserverOutput) == 2696, "output ABI");
_Static_assert(offsetof(OsrObserverFrame, groups) == 168, "group offset");
_Static_assert(offsetof(OsrObserverInput, frame) == 152, "frame offset");
_Static_assert(offsetof(OsrObserverOutput, raw_wrench_up_roll_pitch) == 96, "wrench offset");
