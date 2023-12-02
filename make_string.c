
/*
 * author: Marco Chieppa | crap0101
 */

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <stdarg.h>

typedef char* String;

void foo (String format, String arg);
void die_bad (int exitcode, String format, ...);
String make_string(String format, ...);

int main (int argc, char **argv) {
  int i;
  String s = NULL;
  for (i=1; i < argc; i++) {
    s = make_string("arg %d: <%s>", i, argv[i]);
    if (s == NULL) {
      fprintf(stderr, "error in make_string! (%d, <%s>) | s=<%s>\n", i, argv[i], s);
      return 1;
	} else {
      foo("indirection: %s\n", s);
      free(s);
    }
  }
  if (argc < 2)
    die_bad(EXIT_FAILURE, "%s: not enought arguments (argc=%d)\n", argv[0], argc);
  return 0;
}


String make_string(String format, ...) {
  /* Returns a pointer to a newly allocated string. */
  int n = 0;
  size_t size = 0;
  char *p = NULL;
  va_list lst;
  va_start(lst, format);
  n = vsnprintf(p, size, format, lst); // test length...
  va_end(lst);
  if (n < 0) {
    return NULL;
  }
  if (NULL == (p = malloc((n + 1) * sizeof(char)))) {
    return NULL;
  }
  va_start(lst, format);
  size = 1 + n;
  n = vsnprintf(p, size, format, lst);
  va_end(lst);
  if (n < 0) {
    free(p);
    return NULL;
  }
  return p;
}

void foo (String format, String arg) {
  fprintf(stderr, format, arg);
}

void die_bad (int exitcode, String format, ...) {
  va_list lst;
  va_start(lst, format);
  vfprintf(stderr, format, lst);
  va_end(lst);
  exit(exitcode);
}


/*
$ gcc -Wall -Wextra -ggdb make_string.c
$ ./a.out 
./a.out: not enought arguments (argc=1)
$ ./a.out xx "" foobar
indirection: arg 1: <xx>
indirection: arg 2: <>
indirection: arg 3: <foobar>
$ 
*/
