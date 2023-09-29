
#include <stdio.h>
#include <stdlib.h>

#define LINELEN 100

char *mygetline(void) {
  /*read from stdin*/
  int c, i;
  int size = LINELEN;
  char *line = malloc(size*sizeof(char));
  if (line == NULL) {
    fprintf(stderr, "getline: malloc: memory error\n");
    return NULL;
  }
  for (i=0; (c = getchar()) != '\n' && c != EOF; i++) {
    if (i >= size-1) {
      size += LINELEN;
      if ((line = realloc(line, size*sizeof(char))) == NULL) {
	fprintf(stderr, "getline: realloc: memory error\n");
	return NULL;
      }
    }
    line[i] = c;
  }
  if (i == 0)
    return NULL;
  if ((line = realloc(line, i*sizeof(char))) == NULL) {
    fprintf(stderr, "getline: realloc: memory error\n");
    return NULL;
  }
  return line;
}

int main (void) {
  char *line = NULL;
  while ((line = mygetline()) != NULL)
      printf("|%s|\n", line);
  return 0;
}
