
@namespace "testing"

BEGIN {
    GLOBAL_MUST_EXIT = 1
    MSG_TRUE = "OK"
    MSG_FALSE = "FAIL"
    REPORT["ok_tests_count"] = 0
    REPORT["fail_tests_count"] = 0
    REPORT["running"] = 0
}

###################
# TESTS FUNCTIONS #
###################

function assert_true(condition, must_exit, msg,    ret) {
    # Check if $condition is true, exits with $must_exit
    # if the test fails.
    # Prints the optional message $mgs in any case.
    # For convenience, to *globally* ignore the $must_exit value,
    # one can set the GLOBAL_MUST_EXIT variable to 0
    # avoiding immediate exit in case of test failure.
    ret = 0
    if (! condition) {
	REPORT["fail_tests_count"] += 1
	if (msg)
	    message(ret, msg)
	if (must_exit && GLOBAL_MUST_EXIT)
	    exit(must_exit)
    } else {
	REPORT["ok_tests_count"] += ret = 1
	if (msg)
	    message(ret, msg)
    }
    return ret
}

function assert_false(condition, must_exit, msg,    ret) {
    # Check if $condition is false, exits with $must_exit
    # if the test fails.
    # Prints the optional message $mgs in any case.
    return assert_true(! condition, must_exit, msg)
}

function assert_nothing(condition, must_exit, msg,    ret) {
    # Returns always true, used only to check $condition.
    # Appends a string after $msg to signaling the actual evaluation of $condition. 
    if (! condition)
	return assert_false(condition, must_exit, msg "(assert nothing: FAILED)")
    else
	return assert_true(condition, must_exit, msg "(assert nothing: OK)")
}

function assert_equal(value1, value2, must_exit, msg,    ret) {
    # Check if $value1 == $values, exits with $must_exit
    # if the test fails.
    # Prints the optional message $mgs in any case.
    return assert_true(value1 == value2, must_exit, msg)
}

function assert_not_equal(value1, value2, must_exit, msg,    ret) {
    # Check if $value1 == $values, exits with $must_exit
    # if the test fails.
    # Prints the optional message $mgs in any case.
    return assert_true(value1 != value2, must_exit, msg)
}


#####################
# UTILITY FUNCTIONS #
#####################

function message(condition, msg) {
    # Print $msg and, either, MSG_TRUE or MSG_FALSE depending on $condition.
    printf("%s --> %s\n", msg, condition ? MSG_TRUE : MSG_FALSE) > "/dev/stderr"
}


#####################
# REPORTS FUNCTIONS #
#####################

function start_test_report() {
    REPORT["ok_tests_count"] = 0
    REPORT["fail_tests_count"] = 0
    REPORT["running"] = 1
}

function end_test_report() {
    REPORT["running"] = 0
}

function report() {
    if (REPORT["running"])
	print ("WARNING: tests seems to still be in progress...") > "/dev/stderr"
    printf ("===== TESTS REPORT =====\n" \
	    "total tests:      %3d\n" \
	    "successful tests: %3d\n" \
	    "failed tests:     %3d\n",
	    REPORT["ok_tests_count"] + REPORT["fail_tests_count"],
	    REPORT["ok_tests_count"],
	    REPORT["fail_tests_count"]) > "/dev/stderr"
}
