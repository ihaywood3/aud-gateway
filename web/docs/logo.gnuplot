#set terminal epslatex size 3.5,2.62
#set output 'logo.tex'
set terminal eps enhanced size 1.25, 1 
set output 'logo.eps'
unset key
clear
unset xtics
unset ytics

set xrange [-8:8]
set yrange [-7:7]
set size ratio 1.0
unset zeroaxis
set border 0
set format xy ""

set style line 1 lt 1 lc rgb "black" lw 3

set object 1 ellipse center 0.0,0.0 size 4.5,2. angle 0. front fillstyle empty border -1 lw 4

plot [-8:8] 0.3 * sin(x*2.0)-2+(0.14*x)**2 ls 1, \
            0.3 * sin(x*2.0)-3+(0.14*x)**2 ls 1, \
            0.3 * sin(x*2.0)-4+(0.14*x)**2 ls 1, \
            0.3 * sin(x*2.)+2.0-(0.14*x)**2 ls 1, \
            0.3 * sin(x*2.0)+3-(0.14*x)**2 ls 1, \
            0.3 * sin(x*2.0)+4-(0.14*x)**2 ls 1
### set output
