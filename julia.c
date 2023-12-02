/*
 * Julia set (v.0.5)
 * compile with: gcc -Wall -Wextra -pedantic julia.c -lm -o j
 * author: Marco Chieppa | crap0101
 */

#include <getopt.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define FILENAME "julia.ppm"

#define Julia_rp -0.835
#define Julia_ip -0.2321 

typedef struct {
    double real;
    double img;
} Complex;

void help (char **);
double c_abs(Complex c);
Complex c_mult(Complex, Complex);
Complex c_sum(Complex, Complex);
void write_number(unsigned char *color, FILE *fout);

int main (int argc, char **args) {
  unsigned char t = 0, color[3];
  unsigned int
    i, n, j,
    red, green, blue,
    height = 800,
    width = 1200,
    iter = 1024;
  int
    val, opt,
    limit,
    xmin = -2,
    xmax = 2,
    ymin = -2,
    ymax = 2;
  double dx, dy;
  Complex julia, succ, newsucc;
  FILE *fout;
  char *filename = NULL;

  julia.real = Julia_rp;
  julia.img = Julia_ip;
  while ((opt = getopt(argc, args, "W:H:o:x:X:y:Y:i:R:I:h")) != -1) {
    switch (opt) {
    case 'W':
      val = atoi(optarg);
      if (val < 1) {
	fprintf(stderr, "Illegal value for width: %s\n", optarg);
	exit(EXIT_FAILURE);
      };
      width = val;
      break;
    case 'H':
      val = atoi(optarg);
      if (val < 1) {
	fprintf(stderr, "Illegal value for height: %s\n", optarg);
	exit(EXIT_FAILURE);
      }
      height = val;
      break;
    case 'o':
      filename = optarg;
      break;
    case 'x':
      xmin = atoi(optarg);
      break;
    case 'X':
      xmax = atoi(optarg);
      break;
    case 'y':
      ymin = atoi(optarg);
      break;
    case 'Y':
      ymax = atoi(optarg);
      break;
    case 'i':
      val = atoi(optarg);
      if (val < 1) {
	fprintf(stderr, "Illegal value for iter: %s\n", optarg);
	exit(EXIT_FAILURE);
      }
      iter = val;
      break;
    case 'R':
      julia.real = atof(optarg);
      break;
    case 'I':
      julia.real = atof(optarg);
      break;
    case 'h':
      help(args);
      exit(EXIT_SUCCESS);
    case '?':
      exit(EXIT_FAILURE);
    default:
      help(args);
      exit(EXIT_FAILURE);
    }
  }

  dx = (xmax - xmin) / (double) width,
  dy = (ymax - ymin) / (double) height;
  limit = (xmax > ymax) ? xmax : ymax;

  if ((fout = fopen(filename == NULL ? FILENAME : filename, "w")) == NULL) {
    fprintf(stderr, "Error opening %s\n", FILENAME);
    exit(EXIT_FAILURE);
  }
  fprintf(fout, "P3\n#Julia set\n%d %d\n255\n", width, height); 

  for (i=0; i < height; i++) {
    succ.img = ymin + i*dy;
    for (n=0; n < width; n++) {
      succ.real = xmin + n*dx;
      newsucc = succ;
      for (j=0; j < iter; j++) {
        newsucc = c_sum(c_mult(newsucc, newsucc), julia);
        if (c_abs(newsucc) > limit) {
          red = 100+j/4;
          green = j/2;
          blue = 4*j;
          color[0] = (red > 128) ? 128 : red;
          color[1] = (green > 128) ? 128 : green;
          color[2] = (blue > 255) ? 255 : blue;
          t = 1;
          break;
        }
      }
      if (t == 1) {
	write_number(color, fout);
	t=0;
      } else { 
	fprintf(fout, "0\n0\n0\n");
      }
    }
  }
  fclose(fout);
  return 0;
}

void
write_number (unsigned char *color, FILE *fout) {
  fprintf(fout, "%d\n%d\n%d\n", color[0], color[1], color[2]);
}

double
c_abs (Complex c) {
  return sqrt(c.real*c.real + c.img*c.img);
}

Complex
c_mult (Complex cn1, Complex cn2) {
  Complex m;
  m.real = cn1.real*cn2.real + (cn1.img*cn2.img)*(-1);
  m.img = cn1.real*cn2.img + cn1.img*cn2.real;
  return m;
}

Complex
c_sum (Complex cn1, Complex cn2) {
  Complex sum;
  sum.real = cn1.real + cn2.real;
  sum.img = cn1.img + cn2.img;
  return sum;
}

void
help (char **args) {
  fprintf(stderr,
	  "USAGE: %s [args]\n"
	  "\t-h  show this help and exit\n"
	  "\t-W  image width (default 1200)\n"
	  "\t-H  image height (default 800)\n"
	  "\t-o  output file (default: mandelbrot.ppm)\n"
	  "\t-x  x min value (default: -2)\n"
	  "\t-X  x max value (default: 2)\n"
	  "\t-y  y min value (default: -2)\n"
	  "\t-Y  y max value (default: 2)\n"
	  "\t-i  number of iterations (default 1024)\n"
	  "\t-R  real part (default %f)\n"
	  "\t-I  imag part (default %f)\n"
	  "\n",
	  args[0], Julia_rp, Julia_ip);
}

