# Graph properties
if (! (ARG3 eq "")) {
    set terminal pngcairo size 1600,900 enhanced font ',10'
    set output ARG3
}
else {
    set term qt size 1600,900
}
set title "Chapter sizes"
set grid front
set xlabel "Chapter"
set xtics rotate by 30 right
set ylabel "Length / words"
set nokey
set style fill solid
set boxwidth 1

# Data
set print $db
print system('cat -')
unset print

# Background
start = ARG1 + 0
end = ARG2 + 0
set style rectangle back linewidth 0 fillcolor "#FFFFCC" fillstyle solid noborder
set object 1 rect from start-0.5, graph 0 to end-0.5, graph 1

plot $db using 3:xtic(4) with boxes, \
     $db using 0:($3 + 100):(sprintf("%d",$3)) with labels
