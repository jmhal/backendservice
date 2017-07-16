set encoding iso_8859_1
set terminal pngcairo size 750,452
set output 'eficiencia.png'

#set tics scale 1,1 

#set multiplot layout 3,1

#set key left top
#set title "Tempo de Execução Componente Maleável (2 VMs, Tamanho da Matriz = 5000)"
#set xlabel "Posição da Matriz na Lista de Entrada" 
#set ylabel "Tempo Acumulado (segundos)"  

#plot 'plot_malleable_2_5000_interference_time_priority.txt' using 1:2 title "Interferência" with errorlines ls 2 lc rgb 'black', 'plot_malleable_2_5000_variable_load_time_priority.txt' using 1:2 title "Carga Variável" with errorlines ls 5 lc rgb 'black'

set key right bottom
set title "Eficiência para Componente Maleável (2 VMs, Tamanho da Matriz = 5000)"
set xlabel "Posição da Matriz na Lista de Entrada" 
set ylabel "Carga Média por Nó"

plot 'plot_malleable_2_5000_interference_time_priority.txt' using 1:3 title "Interferência" with errorlines ls 2 lc rgb 'black', 'plot_malleable_2_5000_variable_load_time_priority.txt' using 1:3 title "Carga Variável" with errorlines ls 5 lc rgb 'black'  

#set key left top 
#set title "Conjunto de Recursos para Componente Maleável (2 VMs, Tamanho da Matriz = 5000)"
#set xlabel "Posição da Matriz na Lista de Entrada" 
#set ylabel "Quantidade de Máquinas Virtuais"  

#plot 'plot_malleable_2_5000_interference_time_priority.txt' using 1:4 title "Interferência" with errorlines ls 2 lc rgb 'black', 'plot_malleable_2_5000_variable_load_time_priority.txt' using 1:4 title "Carga Variável" with errorlines ls 5 lc rgb 'black'  


