set encoding iso_8859_1
set terminal pngcairo size 750,452
set output 'tempo.png'

set key left top
set title "Tempo de Execução Componente Maleável (2 VMs, Tamanho da Matriz = 5000)"
set xlabel "Posição da Matriz na Lista de Entrada" 
set ylabel "Tempo Acumulado (segundos)"  

plot 'time.txt' using 1:2 title "Interferência" with errorlines ls 2 lc rgb 'black',

# plot 'plot_malleable_2_5000_interference_time_priority.txt' using 1:2 title "Interferência" with errorlines ls 2 lc rgb 'black', 'plot_malleable_2_5000_variable_load_time_priority.txt' using 1:2 title "Carga Variável" with errorlines ls 1 lc rgb 'black'


