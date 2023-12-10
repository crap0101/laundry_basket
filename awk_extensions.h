/*
Copyright (C) 2023,  Marco Chieppa | crap0101

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 3 of the License,
or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <https://www.gnu.org/licenses>.
*/

/*
 * Description: utilities for gawk extensions.
 */


#ifndef _AWK_EXTENSIONS
#define _AWK_EXTENSIONS
#endif

/* headers used here: not re-include  */
#ifndef _STDIO_H
 #include <stdio.h>
#endif
#ifndef _TIME_H
 #include <time.h>
#endif
#ifndef _STDARG_H
 #include <stdarg.h>
#endif
#ifndef _SYS_RANDOM_H
 #include <stdlib.h>
#endif
#ifndef _STRING_H
 #include <string.h>
#endif
#ifndef _STDLIB_H
 #include <stdlib.h>
#endif


#if defined(__WIN32) || defined(__WIN64)
const char _PATHSEP[] = "\\";
#else
const char _PATHSEP[] = "/";
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

#ifdef Bool
#undef Bool
#endif

typedef enum {False, True} Bool;
typedef enum {USE_TIME, USE_CLOCK, USE_SEED} rand_init_t;
typedef char * String;

Bool __RAND_INIT_CALLED = False;

const String _val_types[] = {
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


/*
 * Some functions used by various extensions:
 */

String
alloc_string(String str, size_t size)
{
  /*
  * Allocates $size bytes for the String $str and returns a pointer
  * to the allocate memory (or NULL if something went wrong).
  * $str must be either NULL or a pointer returned from a
  * previously call of (c|m|re)alloc.
  */
    dprint("(re/alloc) size=%zu\n", size);
    str = realloc(str, sizeof(String) * size);
    return str;
}


int
copy_element(awk_value_t item, awk_value_t * dest )
{
  /*
   * Copies $item on $*dest using the make_* gawk's api functions.
   * Returns 1 if succedes, 0 otherwise.
   * Works with AWK_(STRING|REGEX|STRNUM|NUMBER|UNDEFINED) and,
   * if available, AWK_BOOL.
   * For others val_type (such AWK_ARRAY, which are much more complex
   * to handle), always returns 0. Such cases must be checked before or
   * after calling this function.
   */
  switch (item.val_type) {
  case AWK_STRING:
    make_const_string(item.str_value.str, item.str_value.len, dest);
    return 1;
  case AWK_REGEX:
    make_const_regex(item.str_value.str, item.str_value.len, dest);
    return 1;
  case AWK_STRNUM:
    make_const_user_input(item.str_value.str, item.str_value.len, dest);
    return 1;
  case AWK_NUMBER:
    make_number(item.num_value, dest);
    return 1;
/* not in gawkapi.h (3.0) */
#ifdef AWK_BOOL
  case AWK_BOOL:
    make_bool(item.bool_value, dest);
    return 1;
#endif
  case AWK_UNDEFINED:
    dprint("Undefined: type <%d>\n", AWK_UNDEFINED);
    make_null_string(dest);
    return 1;
  case AWK_ARRAY:        // we don't copy arrays here! o.O
    return 0;
  case AWK_SCALAR:       // should not happen
    eprint("Unsupported type: %d (scalar)\n", item.val_type);
    return 0;
  case AWK_VALUE_COOKIE: // should not happen
    eprint("Unsupported type: %d (value_cookie)\n", item.val_type);
    return 0;
  default:               // could happen
    eprint("Unknown val_type: <%d>\n", item.val_type);
    return 0;
  }
}


Bool rand_init(rand_init_t how, ...) {
  /*
   * Initialize the pseudo-random number generator (see <man 3 random>).
   * $how must be one of USE_TIME (calls time() to get the seed),
   * USE_CLOCK (uses clock()) or USE_SEED for using a custom seed. In the
   * latter case, the 2nd argument must be an unsigned int.
   * Return False if the initialization fails, else True.
   */
  unsigned int i, seed;
  va_list list;
  time_t t;
  
  switch (how) {
  case USE_TIME:
    for (i=0; i<10; i++)
      if (-1 != (t = time(NULL)))
	break;
    if (t == -1)
      return False;
    seed = (unsigned int) t;
    break;
  case USE_CLOCK:
    seed = clock();
    break;
  case USE_SEED:
    va_start(list, how);
    seed = va_arg(list, unsigned int);
    dprint("va_arg seed: <%u>\n", seed);
    va_end(list);
    break;
  default:
    eprint("Unknown value for $how: <%d>\n", how);
    return False;
  }
  srandom(seed);
  return True;
}


String rand_name(String prefix) {
  /*
   * Returns a pseudo random String, prefixed by $prefix.
   * To be used for add distinct array's names in the (g)awk symtable.
   * NOTE: the function checks if rand_init was called before, to assure
   * the randomness of the generated names.
   * Returns the random String or NULL if some errors occours
   * (String creation, the call to rand_init, ...).
   */
  if (! __RAND_INIT_CALLED) {
    dprint("RAND_INIT: first call");
    if (! rand_init(USE_TIME)) {
      eprint("rand_init() failed");
      return NULL;
    }
    __RAND_INIT_CALLED = True;
  }
  unsigned long int size;
  String name;
  size = strlen(prefix) + 50;
  if (NULL == (name = malloc(sizeof(char) * size))) {
    eprint("malloc() failed");
    return NULL;
  }
  if (0 > snprintf(name, size, "%s%ld", prefix, random())) {
    eprint("snprintf() failed");
    free(name);
    return NULL;
  }
  return name;
}
