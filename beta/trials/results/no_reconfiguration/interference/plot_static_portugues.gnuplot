set encoding iso_8859_1
set terminal pngcairo
set output 'eficiencia.png'

#set multiplot layout 2,1

#set key left top
#set title "Tempo de Execução (2 VMs, Tamanho da Matriz = 5000)"
#set xlabel "Posição da Matriz na Lista de Entrada"
#set ylabel "Tempo Acumulado (segundos)"  

#plot 'plot_2_5000_interference.txt' using 1:2 title "Interferência" with errorlines ls 2 lc rgb 'black' , 'plot_2_5000_nointerference.txt' using 1:2 title "Execução Normal" with errorlines ls 5 lc rgb 'black' , 'plot_2_5000_variableload.txt' using 1:2 title "Carga Variável" with errorlines ls 1  lc rgb 'black' 

set key right bottom
set title "Eficiência (2 VMs, Tamanho da Matriz = 5000)"
set xlabel "Posição da Matriz na Lista de Entrada" 
set ylabel "Carga Média por Nó"  

plot 'plot_2_5000_interference.txt' using 1:3 title "Interferência" with errorlines ls 2 lc rgb 'black' , 'plot_2_5000_nointerference.txt' using 1:3 title "Execução Normal" with errorlines ls 5 lc rgb 'black' , 'plot_2_5000_variableload.txt' using 1:3 title "Carga Variável" with errorlines ls 1  lc rgb 'black' 


