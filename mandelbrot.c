/* Mandelbrot 0.4 */

/*
# Copyright (C) 2010  Marco Chieppa (aka crap0101)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#include <math.h>
#include <stdio.h>
#include <string.h>

#define VERSION "0.4"
#define OUTFILE "mandelbrot.ppm"
#define USAGE "USAGE: prog [outfile]"

struct complex
{
    double real;
    double img;
};

double c_abs (struct complex c);
struct complex c_mult (struct complex cn1, struct complex cn2);
struct complex c_sum (struct complex cn1, struct complex cn2);
void write_number (unsigned char *color, FILE *fout);


int
main(int argc, char **argv)
{
    char *outfile;
    if (argc < 2)
        outfile = OUTFILE;
    else if (argc == 2)
        outfile = *++argv;
    else
    {
        puts(USAGE);
        return 1;
    }        
    unsigned char t = 0, color[3];
    int 
        i, n, j,
        red, green, blue,
        h = 800,
        w = 1200,
        iter = 1024,
        xmin = -2,
        xmax = 2,
        ymin = -2,
        ymax = 2,
        limit = (xmax > ymax) ? xmax : ymax;
    double
        dx = (xmax - xmin) / (double) w,
        dy = (ymax - ymin) / (double) h;
    struct complex 
        succ, 
        newsucc;
    FILE *fout;

    if ((fout = fopen(outfile, "w")) == NULL)
    {
        char emsg [strlen(outfile)+6];
        sprintf(emsg, "fopen:%s", outfile);
        perror(emsg);
        return 1;
    }
    fprintf(fout, "P3\n#Mandelbrot\n%d %d\n255\n", w, h); 

    for (i=0; i < h; i++)
    {
        succ.img = ymin + i*dy;
        for (n=0; n < w; n++)
        {
            succ.real = xmin + n*dx;
            newsucc = succ;
            for (j=0; j < iter; j++)
            {
                newsucc = c_sum(c_mult(newsucc, newsucc), succ);
                if (c_abs(newsucc) > limit)
                {
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
            t ? ({write_number(color,fout);t=0;}) : fprintf(fout,"0\n0\n0\n");
        }
    }
    fclose(fout);
    return 0;
}

void
write_number (unsigned char *color, FILE *fout)
{
    fprintf(fout, "%d\n%d\n%d\n", color[0], color[1], color[2]);
}

double
c_abs (struct complex c)
{
    return sqrt(c.real*c.real + c.img*c.img);
}

struct complex
c_mult (struct complex cn1, struct complex cn2)
{
    struct complex m;
    m.real = cn1.real*cn2.real + (cn1.img*cn2.img)*(-1);
    m.img = cn1.real*cn2.img + cn1.img*cn2.real;
    return m;
}

struct complex
c_sum (struct complex cn1, struct complex cn2)
{
    struct complex sum;
    sum.real = cn1.real + cn2.real;
    sum.img = cn1.img + cn2.img;
    return sum;
}

