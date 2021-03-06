set term post eps
set output 'execution_time.eps'

set multiplot layout 2,1

set key left top
set title "Execution Time (2 VMs, Matrix Size = 5000)"
set xlabel "Number of the matrix in the input list" 
set ylabel "Cumulative Time (seconds)"  

plot 'plot_2_5000_interference.txt' using 1:2 title "Interference" with errorlines ls 2, 'plot_2_5000_nointerference.txt' using 1:2 title "Normal Execution" with errorlines ls 5, 'plot_2_5000_variableload.txt' using 1:2 title "Variable Load" with errorlines ls 1  

set key right bottom
set title "Efficiency (2 VMs, Matrix Size = 5000)"
set xlabel "Number of the matrix in the input list" 
set ylabel "Average load per node"  

plot 'plot_2_5000_interference.txt' using 1:3 title "Interference" with errorlines ls 2, 'plot_2_5000_nointerference.txt' using 1:3 title "Normal Execution" with errorlines ls 5, 'plot_2_5000_variableload.txt' using 1:3 title "Variable Load" with errorlines ls 1  


