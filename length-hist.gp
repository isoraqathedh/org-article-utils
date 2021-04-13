# For stacked chart variant
firstcol=2
cumulated(i)=((i>firstcol)?column(i)+cumulated(i-1):(i==firstcol)?column(i):1/0)

# Output
if (! (ARG1 eq "")) {
    set terminal pngcairo size 1600,900 enhanced font ',10'
    set output ARG1
}
else {
    set term qt size 1600,900
}

# Data options
set datafile separator ","
set xdata time
set timefmt "%Y-%m-%d %H:%M:%S %Z"

# Graph properties
set title "Size of files over time per commit"
set grid
set format x "%Y-%m"
set xtics "2017-06-01", 2629746 * 3
set xlabel "Date"
set ylabel "Length / bytes"
set xrange [:time(0)]
set key left top

# Data
set print $db
print system('cat -')
unset print

# Plot
plot for [i=2:*] $db using 1:i with lines title columnhead
