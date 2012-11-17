/*
 * csub.c : utility for *.srt subtitle files synchronization
 *
 *  Copyright (C) 2009  Marco Chieppa (a.k.a crap0101)
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not see <http://www.gnu.org/licenses/>
 */

/*
 * Name: csub
 * Version: 0.9.4
 * Description: utility for *.srt subtitle files synchronization
 * Author: Marco Chieppa ( a.k.a crap0101 )
 * contact: crap0101 [at] riseup [dot] net
 * Date: 20 Oct 2011
 * Changelog: - fixed typos
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <ctype.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>
/* uncomment the follow #undef to use custom readline function 
 * instead of Gnu readline by default... but why? */
/*#undef __USE_GNU */
#ifndef __USE_GNU    /* reference in /usr/include/bits/stdio.h */
#  define USE_MYGETLINE 1
#  define getline(s, n, t) do {} while (0)
#else
#  define USE_MYGETLINE 0
#endif

#define MAXMS    1000    /* used for time-delta computing, do not change! */
#define MAXMTS   60      /* used for time-delta computing, do not change! */
#define MAXHR    3600    /* used for time-delta computing, do not change! */
#define MAXLINES 100
#define MAXLINE  1000

#define NAME    "csub"
#define VERSION "0.9.2"
#define DATE    "20 Oct 2011"
#define AUTHOR  "Marco Chieppa (a.k.a crap0101)"
#define CONTACT "crap0101 [at] riseup [dot] net"
#define LICENSE "GNU GPL v3 or later"

typedef unsigned int Bool;
typedef char * String;

int DEBUG = 0x0;
Bool False = 0x0;
Bool True = 0x1;

typedef struct
{
  int ms;
  int s;
  int m;
  int h;
  int count;
  String inFile;
  String outFile;
} SubsTime;

typedef struct
{
  int totalSec;
  int ms;
} NewTime;

typedef String * (*FmtPrt) (String *, FILE *, String, 
                            int *, SubsTime *, SubsTime *);
FmtPrt print_out;

typedef ssize_t (*GetLine) (String *, size_t *, FILE *);
GetLine get_line__;

/**********************************************
 * F U N C T I O N S    D E C L A R A T I O N *
 **********************************************/

Bool check_int (const String, char);
SubsTime parse_cmline (int, String *);
void new_time (NewTime *, SubsTime *, SubsTime *);
Bool blank_line (const String);
void new_srt_sub (SubsTime *);
String * print_to_string (String *, FILE *, String,
                          int *, SubsTime *, SubsTime *);
String * print_to_file (String *, FILE *, String,
                        int *, SubsTime *, SubsTime *);
ssize_t mygetline (String *, size_t *, FILE *);
void help (const String);
void raise_error_and_exit (String message, int exit_status);

/***********
 * M A I N *
 ***********/

int
main (int argc, char **argv)
{
  SubsTime sub;
  sub = parse_cmline (argc, argv);
  if (DEBUG)
    fprintf (stderr, "millisecs: %d\nsecs: %d\nmins: %d\nhrs: %d\n"
            "count: %d\ninFile: %s\noutFile: %s\n",
            sub.ms, sub.s, sub.m, sub.h, sub.count, sub.inFile, sub.outFile);
  new_srt_sub (&sub);
  return 0;
}


/********************************************
 * F U N C T I O N S    D E F I N I T I O N *
 ********************************************/

void
raise_error_and_exit (String message, int exit_status)
{
  fputs (message, stderr);
  exit (exit_status);
}

Bool
check_int (String s, char c)
{
  while (isspace(*s))
    s++;
  if (*s == '-' || *s == '+' || isdigit(*s))
    s++;
  else
    return False;
  for ( ; *s; s++)
    if (!isdigit (*s))
      return False;
  return True;
}

SubsTime
parse_cmline (int argc, String *argv)
{
  int c, i = 0;
  SubsTime info = {0, 0, 0, 0, 0, NULL, NULL};
  static struct option loptions [] =
    {
      {"ms",           required_argument, 0, 'M'},
      {"sec",          required_argument, 0, 's'},
      {"min",          required_argument, 0, 'm'},
      {"hour",         required_argument, 0, 'h'},
      {"count",        required_argument, 0, 'c'},
      {"input-file",   required_argument, 0, 'i'},
      {"output-file",  required_argument, 0, 'o'},
      {"debug",        no_argument,       &DEBUG, 1},
      {"help",         no_argument,       0, 'H'},
      {0, 0, 0, 0}
    };

  while ((c = getopt_long (argc, argv, "M:s:m:h:c:i:o:dH", loptions, &i)) != -1)
    switch (c)
      {
      case 0:
        if (loptions [i].flag != 0)
          break;
      case 'M':
        if (!check_int (optarg, 'M'))
          raise_error_and_exit ("Error: option's -M argument must be a digit\n", 2);
        info.ms = atoi (optarg);
        if (info.ms > 999 || info.ms < -999)
          raise_error_and_exit ("Error: -M value out of range "
                                "(must be -999 .. 999)\n", 16);
        break;
      case 's':
        if (!check_int (optarg, 's'))
          raise_error_and_exit ("Error: option's -s argument must be a digit\n", 2);
        info.s = atoi (optarg);
        break;
      case 'm':
        if (!check_int (optarg, 'm'))
          raise_error_and_exit ("Error: option's -m argument must be a digit\n", 2);
        info.m = atoi (optarg);
        break;
      case 'h':
        if (!check_int (optarg, 'h'))
          raise_error_and_exit ("Error: option's -h argument must be a digit\n", 2);
        info.h = atoi (optarg);
        break;
      case 'c':
        if (!check_int (optarg, 'c'))
          raise_error_and_exit ("Error: option's -c argument must be a digit\n", 2);
        info.count = atoi (optarg);
        break;
      case 'i':
        info.inFile = optarg;
        break;
      case 'o':
        info.outFile = optarg;
        break;
      case 'd':
        DEBUG = True;
        break;
      case 'H':
        help (argv [0]);
      case '?':
        raise_error_and_exit ("What?\n", 2);
      default:
        raise_error_and_exit ("Error: malformed expression\n", 2);
      }
  if (argc - optind)
    {
      fprintf (stderr, "Error: Unknown values: ");
      while (optind < argc)
        fprintf (stderr, "%s, ", argv [optind++]);
      fprintf (stderr, "\n");
      exit (55);
    }
  return info;
}

void
new_time (NewTime *nt, SubsTime *delta, SubsTime *current)
{
  nt->ms = delta->ms + current->ms;
  nt->totalSec = (delta->h + current->h) * MAXHR;
  nt->totalSec += (delta->m + current->m) * MAXMTS;
  nt->totalSec += (delta->s + current->s);
  (nt->ms >= MAXMS)
    ? ({nt->totalSec += nt->ms / MAXMS; nt->ms %= MAXMS;})
    : (nt->ms < 0)
    ? ({nt->totalSec -= 1; nt->ms = abs (nt->ms) % MAXMS;})
    : ({});
  current->h = nt->totalSec / MAXHR;
  current->m = (nt->totalSec % MAXHR) / MAXMTS;
  current->s = nt->totalSec - current->m * MAXMTS - current->h * MAXHR;
  current->ms = nt->ms;
}

Bool 
blank_line (String s)
{
  while (*s)
    if (!isspace (*s++))
      return False;
  return True;
}

String *
print_to_string (String *pts, FILE *outfile, String line,
           int *num, SubsTime *s1, SubsTime *s2)
{
  static unsigned long
    aline = 0,
    clines = MAXLINES;
  String newline;
  if (aline >= (clines - 1))
    {
      clines += MAXLINES;
      if ((pts = (String *) realloc (pts, sizeof (String *) * clines)) == NULL)
        raise_error_and_exit ("Error (in function print_to_string): "
                              "realloc (pts)\n", 89);
    }
  if ((newline = malloc (sizeof (char) * (strlen (line)+10))) == NULL)
    raise_error_and_exit ("memory error (in function print_to_string)\n", 127);
  if (s1 != NULL && s2 != NULL)
    sprintf (newline, "%02d:%02d:%02d,%03d --> %02d:%02d:%02d,%03d\n",
             s1->h, s1->m, s1->s, s1->ms,
             s2->h, s2->m, s2->s, s2->ms);
  else if (num != NULL)
    sprintf (newline, "%d\n", *num + s1->count);
  else
    sprintf (newline, "%s", line);
  pts [aline++] = newline;
  return pts;
}

String *
print_to_file (String *newfile, FILE *outfile, String line,
           int *num, SubsTime *s1, SubsTime *s2)
{
  if (s1 != NULL && s2 != NULL)
    fprintf (outfile,
             "%02d:%02d:%02d,%03d --> %02d:%02d:%02d,%03d\n",
             s1->h, s1->m, s1->s, s1->ms,
             s2->h, s2->m, s2->s, s2->ms);
  else if (num != NULL)
    fprintf (outfile, "%d\n", *num + s1->count);
  else
    fprintf (outfile, "%s", line);
  return NULL;
}

void
new_srt_sub (SubsTime *ssubst)
{
  int
    rbytes,
    cargs,
    newBlock = True,
    sflag = False;
  String
    tmpString,
    *pts = NULL;
  size_t lbytes = MAXLINE;
  NewTime *nt;
  SubsTime
    *tsub1,
    *tsub2;
  FILE
    *inputFile,
    *outputFile;

  if (USE_MYGETLINE)
    get_line__ = mygetline;
  else
    get_line__ = getline;
  //if (DEBUG) fprintf (stderr,"USE_MYGETLINE: %d\n",USE_MYGETLINE);//exit (9);
  if (ssubst->inFile == NULL)
    inputFile = stdin;
  else if ((inputFile = fopen (ssubst->inFile, "r")) == NULL)
    {
      fprintf (stderr, "Error (in function new_srt_sub): "
              "cannot open %s\n", ssubst->inFile);
      exit (41);
    }
  if (ssubst->outFile == NULL)
    {
    print_out = print_to_file;
    outputFile = stdout;
    }
  else if (ssubst->inFile && strcmp (ssubst->inFile, ssubst->outFile) == 0)
    {
      if ((pts = malloc (sizeof (String) * MAXLINES)) == NULL)
        {
          fprintf (stderr, "Error (in function new_srt_sub): "
                   "malloc (pts)\n");
          exit (88);
        }
      print_out = print_to_string;
      sflag = True;
    }
  else if ((outputFile = fopen (ssubst->outFile, "w")) == NULL)
    {
      fprintf (stderr, "Error (in function new_srt_sub): "
              "cannot open %s\n", ssubst->outFile);
      exit (42);
    }
  else
    print_out = print_to_file;
  if ((tmpString = malloc (sizeof (char) * (lbytes + 1))) == NULL)
    {
      fprintf (stderr, "Error (in function new_srt_sub): "
              "failed to allocate memory for tmpString\n");
      exit (51);
    }
  if ((nt = malloc (sizeof (NewTime))) == NULL)
    {
      fprintf (stderr, "Error (in function new_srt_sub): "
              "failed to allocate memory for *nt\n");
      exit (61);
    }
  if ((tsub1 = malloc (sizeof (SubsTime))) == NULL)
    {
      fprintf (stderr, "Error (in function new_srt_sub): "
              "failed to allocate memory for *tsub1\n");
      exit (71);
    }
  if ((tsub2 = malloc (sizeof (SubsTime))) == NULL)
    {
      fprintf (stderr, "Error (in function new_srt_sub): "
              "failed to allocate memory for *tsub2\n");
      exit (72);
    }

  while (feof (inputFile) == False || ferror (inputFile))
    {
      rbytes = get_line__ (&tmpString, &lbytes, inputFile);
      if (rbytes < 0x0)
        break;
      if (blank_line (tmpString))
        {
          newBlock = True;
          pts = print_out (pts, outputFile, tmpString, NULL, NULL, NULL);
        }
      else if (newBlock)
        {
          if (! sscanf (tmpString, "%d", &cargs))
            {
              fprintf (stderr, "Error: bad formatted files (%d)\n", cargs);
              exit (91);
            }

          pts = print_out (pts, outputFile, tmpString, &cargs, ssubst, NULL); 
          rbytes = get_line__ (&tmpString, &lbytes, inputFile);
          cargs = sscanf (tmpString, "%d:%d:%d,%d --> %d:%d:%d,%d",
                          &tsub1->h, &tsub1->m, &tsub1->s, &tsub1->ms,
                          &tsub2->h, &tsub2->m, &tsub2->s, &tsub2->ms);
          if (cargs != 8) 
            {
              fprintf (stderr, "Error: bad formatted files (%s)\n", tmpString);
              exit (92);
            }
          new_time (nt, ssubst, tsub1);
          new_time (nt, ssubst, tsub2);
          pts = print_out (pts, outputFile, tmpString, NULL, tsub1, tsub2);
          newBlock = False;
        }
      else
       pts = print_out (pts, outputFile, tmpString, NULL, NULL, NULL);
    }
  fclose (inputFile);
  if (sflag)
    {
      inputFile = fopen (ssubst->inFile, "w");
      while (*pts)
        fprintf (inputFile, "%s", *pts++);
      fclose (inputFile);
    }
  else
    fclose (outputFile);
}

ssize_t
mygetline (String *line, size_t *n, FILE *stream)
{
  int i = 0;
  char c;
  while ((c = (*line) [i++] = getc (stream)) != '\n' && c != EOF && i < *n)
    ;
  if (i < *n)
    {
      (*line) [i] = '\n';
      (*line) [i++] = '\0';
    }
  else if (i >= *n)
    (*line) [*n] = '\n';
  return (c == EOF) ? -1 : i;
}

void
help (String pname)
{
  printf ("\nName: %s\nVersion: %s\nDate: %s\n"
          "Descriptions:  utility for *.srt subtitle files synchronization\n"
          "Author:  %s\n"
          "Contact: %s\n"
          "License: %s\n\n"
          "USAGE:\n"
          "  $ %s [-i infile] [-o outfile] [options]\n\n"
          "OPTIONS:\n"
          "  -M, --ms NUM\n"
          "      change the milliseconds values (must be in range -999..999)\n"
          "  -s, --sec NUM\n"
          "      change the seconds values\n"
          "  -m, --min NUM\n"
          "      change the minutes values\n"
          "  -h, --hour NUM\n"
          "      change the hours values\n"
          "  -c, --count NUM\n"
          "      change the subtitiles count numbers\n"
          "  -i, --input-file INFILE\n"
          "      Set INFILE as the subtitles file to change\n"
          "      (default: stdin)\n"
          "  -o, --output-file OUTFILE\n"
          "      Set OUTFILE as the new subs file which will be created\n"
          "      (default: stdout)\n"
          "  -d, --debug\n"
          "      debug. Print some info about the subs struct\n"
          "      NOTE: output redirected to stderr\n"
          "  -H, --help\n"
          "      Print this help\n\n"
          "EXAMPLES:\n"
          "  $ %s -i subfile.srt -o newsubsfile.srt -M 15 -s 11 -m -1\n"
          "  $ cat << EOF | %s -c 2   # read from stdin, write on stdout\n\n"
          "NOTE:\n"
          "  Running the program with the same file for input and output:\n"
          "  $ %s -i subfile1 -o subfile1\n"
          "  cause the input file to be rewritten in place\n\n",
          NAME, VERSION, DATE, AUTHOR, CONTACT,
          LICENSE, pname, pname, pname, pname);
  exit (11);
}
