set term post eps 
set output 'execution_time.eps'

set tics scale 1,1 

set multiplot layout 3,1
#set xtic auto
#set ytic auto

set key left top
set title "Execution Time For Malleable System (2 VMs, Matrix Size = 5000)"
set xlabel "Number of the matrix in the input list" 
set ylabel "Cumulative Time"  

plot 'plot_malleable_2_5000_interference_time_priority.txt' using 1:2 title "Interference" with errorlines ls 2, 'plot_malleable_2_5000_variable_load_time_priority.txt' using 1:2 title "Variable Load" with errorlines ls 5

set key right bottom
set title "Efficiency for Malleable System (2 VMs, Matrix Size = 5000)"
set xlabel "Number of the matrix in the input list" 
set ylabel "Average load per node"  

plot 'plot_malleable_2_5000_interference_time_priority.txt' using 1:3 title "Interference" with errorlines ls 2, 'plot_malleable_2_5000_variable_load_time_priority.txt' using 1:3 title "Variable Load" with errorlines ls 5  

set key left top 
set title "Cluster Size for Malleable System (2 VMs, Matrix Size = 5000)"
set xlabel "Number of the matrix in the input list" 
set ylabel "Number of VMs"  

plot 'plot_malleable_2_5000_interference_time_priority.txt' using 1:4 title "Interference" with errorlines ls 2, 'plot_malleable_2_5000_variable_load_time_priority.txt' using 1:4 title "Variable Load" with errorlines ls 5  


