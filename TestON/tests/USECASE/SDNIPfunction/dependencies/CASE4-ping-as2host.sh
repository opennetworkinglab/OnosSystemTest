#!/bin/bash


#all the address in this for loop should work

# ping test between as2 and as3
for ((i=0;i<10;i++)); do

        #echo '------from 3.0.0.x to 4.0.1.'$j'------'

	for ((j=0; j<10; ++j )) ; do
		echo '3.0.'$i'.1 -> 4.0.'$j'.1'
    		ping -c 1 -w 1 -I 3.0.$i.1 4.0.$j.1 | grep 'from 4.0.'$j'.1'

	done

done
for ((i=0;i<10;i++)); do

        #echo '------from 3.0.0.x to 5.0.1.'$j'------'

        for ((j=0; j<10; ++j )) ; do
                echo '3.0.'$i'.1 -> 5.0.'$j'.1'
                ping -c 1 -w 1 -I 3.0.$i.1 5.0.$j.1 | grep 'from 5.0.'$j'.1'

        done

done

# ping test between as2 and as4
for ((i=1;i<2;i++)); do
       for ((prefix=101; prefix<=200; ++prefix)) ; do
               for ((j=0; j<10; ++j )) ; do
                       echo '3.0.0.'$i' - > '$prefix'.0.'$j'.1'
                       ping -c 1 -w 1 -I 3.0.0.$i $prefix.0.$j.1 | grep 'from '$prefix'.0.'$j'.1'

                done
        done

done

