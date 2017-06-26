set term post eps
set output 'execution_time.eps'

set multiplot layout 2,1
set key right outside

set title "Execution Time (6 VMs, Matrix Size = 5000)"
set xlabel "Number of the matrix in the input list" 
set ylabel "Cumulative Time (seconds)"  

plot 'plot_6_5000_interference.txt' using 1:2 title "Interference" with errorlines ls 3, \
     'plot_6_5000_nointerference.txt' using 1:2 title "No Interference" with errorlines ls 5  

set title "Efficiency (6 VMs, Matrix Size = 5000)"
set xlabel "Number of the matrix in the input list" 
set ylabel "Average load per node"  

plot 'plot_6_5000_interference.txt' using 1:3 title "Interference" with errorlines ls 3, \
     'plot_6_5000_nointerference.txt' using 1:3 title "No Interference" with errorlines ls 5  


