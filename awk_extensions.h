
/* Some dec/utilities for gawk extension */

/*
 * Before including this, include:
 * <stdio.h>
 */

#if defined(__WIN32) || defined(__WIN64)
 #define _PATHSEP "\\"
#else
 #define _PATHSEP "/"
#endif

#ifndef __module__
 #define __module__ "gawk extension"
#endif
#define eprint(fmt, ...) fprintf(stderr, __msg_prologue fmt, __module__, __func__, ##__VA_ARGS__)
#ifndef _DEBUGLEVEL
 #define _DEBUGLEVEL 0
#endif
#if (_DEBUGLEVEL)
#define dprint eprint
#define __msg_prologue "Debug: %s @%s: "
#else
#define __msg_prologue "Error: %s @%s: "
#define dprint(fmt, ...) do {} while (0)
#endif

#define name_to_string(name) #name

const char *_val_types[] = {
    "AWK_UNDEFINED",
    "AWK_NUMBER",
    "AWK_STRING",
    "AWK_REGEX",
    "AWK_STRNUM",
    "AWK_ARRAY",
    "AWK_SCALAR",
    "AWK_VALUE_COOKIE",
    "AWK_BOOL"
};

typedef char * String;
