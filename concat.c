/*
 * author: Marco Chieppa | crap0101
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>

#define DEBUGLVL 2
#if (DEBUGLVL == 0)
int print(char *fmt, ...) { return (int) *fmt; };
#define print_ print
#elif (DEBUGLVL == 1)
#define print(fmt, ...) fprintf(stderr, fmt, ##__VA_ARGS__)
int print_(char *fmt, ...) { return (int) *fmt; };
#else
#define print(fmt, ...) fprintf(stderr, fmt, ##__VA_ARGS__)
#define print_ print
#endif

typedef enum {False, True} Bool;

char *aconcat (char *sep, char **args) {
  /*
   * concat strings from a char **,
   * returns a pointer to the resulting string.
   */
  char *p, *cstr = NULL;
  unsigned int len, space = 1024, used = 0;
  unsigned int sep_len = strlen(sep);
  
  print("aconcat:calloc...\n");
  if (NULL == (cstr = (char *) calloc(space, sizeof(char)))) {
    print("aconcat:calloc fail!\n");
    return NULL;
  }
  while (NULL != *args) {
    if (0 < (len = strlen(*args))) {
      print("aconcat:arg: <%s>\n", *args);
      if (len + sep_len + used >= space) {
	while (len + sep_len + used >= space) {
	  space *= 2;
	}
	print("aconcat:realloc...\n");
	if (NULL == (p = realloc(cstr, space * sizeof(char)))) {
	  print("aconcat:realloc fail!\n");
	  free(cstr);
	  return NULL;
	} else { cstr = p; }
      }
      used += len + sep_len; // not already used...
      if (used > len + sep_len) {
	cstr = strncat(cstr, sep, sep_len * sizeof(char));
	print_("aconcat:cstr + sep <%s>\n", cstr);
      } else { used -= sep_len; }
      cstr = strncat(cstr, *args, len * sizeof(char));
      print_("aconcat:cstr + sep + arg <%s>\n", cstr);
    }
    args += 1;
  }
  print("aconcat:space = %d | used = %d\n", space, used);
  return cstr;
}

char *concat (int total_args, ...) {
  /*
   * Concatenates strings.
   * Returns a newly allocate char * to the resulting string
   * or NULL if something goes bad.
   * Args:
   * $total_args: total number of strings to concat
   * ...: the next argument must be a separator string (even "")
   * the others arguments are the strings to join.
   */

  va_list alist;
  char *arg, *cstr, *sep, *p = NULL;
  unsigned int i = total_args;
  unsigned int len, sep_len, space = 1024, used = 0;
  
  print("concat:calloc...\n");
  if (NULL == (cstr = (char *) calloc(space, sizeof(char)))) {
    print("concat:calloc fail!\n");
    return NULL;
  }

  va_start(alist, total_args);
  sep = va_arg(alist, char *);
  sep_len = strlen(sep);
  while (0 < i--) {
    arg = va_arg(alist, char *);
    if (NULL != arg && (len = strlen(arg))) {
      print("concat:arg %d: <%s>\n", total_args - i, arg);
      if (len + sep_len + used >= space) {
	while (len + sep_len + used >= space) {
	  space *= 2;
	}
	print("concat:realloc...\n");
	if (NULL == (p = realloc(cstr, space * sizeof(char)))) {
	  print("concat:realloc fail!\n");
	  free(cstr);
	  return NULL;
	} else { cstr = p; }
      }
      used += len + sep_len; // not already used...
      if (used > len + sep_len) {
	cstr = strncat(cstr, sep, sep_len * sizeof(char));
	print_("concat:cstr + sep <%s>\n", cstr);
      } else { used -= sep_len; }
      cstr = strncat(cstr, arg, len * sizeof(char));
      print_("concat:cstr + sep + arg <%s>\n", cstr);
    }
  }
  va_end(alist);
  print("concat:space = %d | used = %d\n", space, used);
  return cstr;
}

Bool test(int cc, char *sep) {
  if (cc == 1) {
    print_("*t1 = <%s>\n", concat(1, "_", "X")); // senseless but...
    print_("*t2 = <%s>\n", concat(1, "_", ""));  // senseless but...
    print_("*t2 = <%s>\n", concat(3, "", "", NULL, ""));  // senseless but...
    print_("*t2 = <%s>\n", concat(3, "", "", "A", ""));
    print_("*t2 = <%s>\n", concat(2, "-", "1", "2", "3"));  // result: "1-2"
    //print_("*t3 = <%s>\n", concat(2, "_", "X")); // invalid call, good chance of segfault
  }
  char *s0 = "foo";
  char *s1 = NULL;
  const char *s2 = "bar";
  char s3[] = "X";
  // char s4[] = {'x','y','z'}; //nope, must be null-terminated
  char s4[] = {'x','y','z','\0'};
  char s5[] = {'X','Y','Z','\0'};
  char *p;
  if (NULL == (p = concat(8, sep, s0, s1, s2, s3, s4, s5, "", "foobar"))) {
    print("Error:concat");
    return False;
  } else {
    printf("%s\n", p);
  }
  free(p);
  return True;
}

int main(int argc, char **argv) {
  if (argc > 1) {
    if (0 == strcmp(argv[1], "-ctest")) {
      print("* running test() ...\n");
      (test(1, "") && test(0, "-")) ? exit(EXIT_SUCCESS) : exit(EXIT_FAILURE);
    } else if (0 == strcmp(argv[1], "-atest")) {
      char *sa[] = {"X","YYYYY","", NULL, "ZZZ"};
      char *p;
      if (NULL == (p = aconcat("_", sa))) { print("Error:aconcat");exit(EXIT_FAILURE);}
      else { printf("%s\n", p); free(p);}
      if (NULL == (p = aconcat("", ++argv))) { print("Error:aconcat");exit(EXIT_FAILURE);}
      else { printf("%s\n", p); free(p);}
    }
  exit(EXIT_SUCCESS);
  }
  perror("No args no party");
  exit(EXIT_FAILURE);
}



/* DEBUGLVL 0
crap0101@orange:/tmp$ ./a.out -ctest foo bar baz
X

X_H=
foobarXxyzXYZfoobar
foo-bar-X-xyz-XYZ-foobar
crap0101@orange:/tmp$ ./a.out -atest foo bar baz
X_YYYYY
-atestfoobarbaz
*/

/* DEBUGLVL 1
crap0101@orange:/tmp$ gcc -Wall -Wextra concat.c 
crap0101@orange:/tmp$ ./a.out -atest foo bar baz
aconcat:calloc...
aconcat:arg: <X>
aconcat:arg: <YYYYY>
aconcat:space = 1024 | used = 7
X_YYYYY
aconcat:calloc...
aconcat:arg: <-atest>
aconcat:arg: <foo>
aconcat:arg: <bar>
aconcat:arg: <baz>
aconcat:space = 1024 | used = 15
-atestfoobarbaz
crap0101@orange:/tmp$ ./a.out -ctest foo bar baz
* running test() ...
concat:calloc...
concat:arg 1: <X>
concat:space = 1024 | used = 1
X
concat:calloc...
concat:space = 1024 | used = 0

concat:calloc...
concat:arg 1: <X>
concat:arg 2: <H=>
concat:space = 1024 | used = 4
X_H=
concat:calloc...
concat:arg 1: <foo>
concat:arg 3: <bar>
concat:arg 4: <X>
concat:arg 5: <xyz>
concat:arg 6: <XYZ>
concat:arg 8: <foobar>
concat:space = 1024 | used = 19
foobarXxyzXYZfoobar
concat:calloc...
concat:arg 1: <foo>
concat:arg 3: <bar>
concat:arg 4: <X>
concat:arg 5: <xyz>
concat:arg 6: <XYZ>
concat:arg 8: <foobar>
concat:space = 1024 | used = 24
foo-bar-X-xyz-XYZ-foobar
crap0101@orange:/tmp$ 
*/


/* DEBUGLVL 2
crap0101@orange:/tmp$ ./a.out -ctest foo bar baz
* running test() ...
concat:calloc...
concat:arg 1: <X>
concat:cstr + sep + arg <X>
concat:space = 1024 | used = 1
*t1 = <X>
concat:calloc...
concat:space = 1024 | used = 0
*t2 = <>
concat:calloc...
concat:arg 1: <X>
concat:cstr + sep + arg <X>
concat:arg 2: <H=>
concat:cstr + sep <X_>
concat:cstr + sep + arg <X_H=>
concat:space = 1024 | used = 4
*t3 = <X_H=>
concat:calloc...
concat:arg 1: <X>
concat:cstr + sep + arg <X>
concat:space = 1024 | used = 1
X
concat:calloc...
concat:space = 1024 | used = 0

concat:calloc...
concat:arg 1: <X>
concat:cstr + sep + arg <X>
concat:arg 2: <H=>
concat:cstr + sep <X_>
concat:cstr + sep + arg <X_H=>
concat:space = 1024 | used = 4
X_H=
concat:calloc...
concat:arg 1: <foo>
concat:cstr + sep + arg <foo>
concat:arg 3: <bar>
concat:cstr + sep <foo>
concat:cstr + sep + arg <foobar>
concat:arg 4: <X>
concat:cstr + sep <foobar>
concat:cstr + sep + arg <foobarX>
concat:arg 5: <xyz>
concat:cstr + sep <foobarX>
concat:cstr + sep + arg <foobarXxyz>
concat:arg 6: <XYZ>
concat:cstr + sep <foobarXxyz>
concat:cstr + sep + arg <foobarXxyzXYZ>
concat:arg 8: <foobar>
concat:cstr + sep <foobarXxyzXYZ>
concat:cstr + sep + arg <foobarXxyzXYZfoobar>
concat:space = 1024 | used = 19
foobarXxyzXYZfoobar
concat:calloc...
concat:arg 1: <foo>
concat:cstr + sep + arg <foo>
concat:arg 3: <bar>
concat:cstr + sep <foo->
concat:cstr + sep + arg <foo-bar>
concat:arg 4: <X>
concat:cstr + sep <foo-bar->
concat:cstr + sep + arg <foo-bar-X>
concat:arg 5: <xyz>
concat:cstr + sep <foo-bar-X->
concat:cstr + sep + arg <foo-bar-X-xyz>
concat:arg 6: <XYZ>
concat:cstr + sep <foo-bar-X-xyz->
concat:cstr + sep + arg <foo-bar-X-xyz-XYZ>
concat:arg 8: <foobar>
concat:cstr + sep <foo-bar-X-xyz-XYZ->
concat:cstr + sep + arg <foo-bar-X-xyz-XYZ-foobar>
concat:space = 1024 | used = 24
foo-bar-X-xyz-XYZ-foobar
*/
