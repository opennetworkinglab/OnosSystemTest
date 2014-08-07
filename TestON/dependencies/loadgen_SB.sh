#!/bin/bash
'''
This is the southbound load generator to generator topology events for tests, such as scale-out and performance testing. 
Example command: ./loadgen_SB.sh startload "1.1.1.1:6633 2.2.2.2:6633" 100 4 100 300 11 - will have 100 switches RR connection to the list of controllers. There will be 4 dataplane ports per switch; switch connection rate (aggregated) is 100 switch/second; duration is 300 seconds; "11" is used as part of the dpid to distinguish switch generated from multiple instances of this generator. Switch disconnnect will use "127.0.0.1:10000" as its connection." 
'''

case "$1" in
	addsw)
		numsw=$2
		;;
	delsw)
		numsw=$2
        ;;
    startload)
		list_ctrl=$2;numsw=$3;numport=$4;rate=$5;duration=$6;prefix_dpid=$7
        sleeptimer=$(echo "scale=4; (1/$rate)"|bc)
        ;;
    chksw)
		numsw=$2
        ;;
    *)
        #echo "Enter action:"
        #echo "addsw number_switches - addsw 200"
        #echo "delsw number_switches - delsw 200"
        echo "startload list of controllers numsw numportPerSW rate(#/s) duration(s) dpid_prefix - startload "1.1.1.1 2.2.2.2 3.3.3.3" 100 4 10 300 11  #switches will be evenly spread to those controllers"
		echo "prefix_dpid is the first two octect of dpid in hex, such as "11", or "aa"."
		echo "This command will first add numb_of_switches to OVSDB; then generate the load as configured; when finished, delete all switches from OVSDB."
        #echo "chsw num_switches - chsw 200 #get all switches and their current controller connection"
        exit 1
esac

add-ovs () 
{
	for ((i=1;i<=$numsw;i++))
    	do      
    		str=$(printf '%014X' $i); dpid=$prefix_dpid$str
			echo "adding ovs switch s$i"
        	sudo ovs-vsctl add-br "s"$i
			sudo ovs-vsctl set bridge "s"$i other-config:datapath-id=$dpid
            
            #echo "adding $numport dataplane ports to switch s$i ... "
			for ((p=1; p<=$numport; p++))
				do
				echo "adding port $p to switch s$i ... "
				sudo ovs-vsctl add-port "s"$i "s"$i"p"$p
            done
	done
}

del-ovs () 
{
	for ((i=1;i<=$numsw;i++))
        do
                #echo "deleting ovs switch s$i"
                sudo ovs-vsctl del-br "s"$i 
        done
}

conn-ovs () 
{
	i=1
	while (($i<=$numsw)) 
	do 
		for ctrl_port in ${list_ctrl[@]}
		do
			if (($i!=0))
			then
				#ovsctrl="tcp:"$ctrl_port
				#echo  "s"$i
				sudo ovs-vsctl --no-wait --no-syslog set-controller "s"$i "tcp:"$ctrl_port & 
				let i+=1
				sleep $sleeptimer
			fi
		done
	done
}

disconn-ovs () 
{
	i=1
    while (($i<=$numsw)) 
    do
		ovsctrl="tcp:127.0.0.1:10000"
        #echo  "s"$i
        sudo ovs-vsctl --no-wait set-controller "s"$i $ovsctrl &
        let i+=1
        sleep $sleeptimer
    done
}

get-ovs ()
{
    i=$numsw
    while (($i>0)) 
    do
        echo "s"$i
		sudo ovs-vsctl get-controller "s"$i
        let i-=1
    done

}

loadsw ()
{
	echo "adding $numsw ovs switches..."
	add-ovs

	echo "starting to generate south bound load ...."
    	let "roundtime = numsw / rate"
	#let "iter = duration / roundtime / 2 "
    iter=1
	echo "Running load for $duration seconds..."
    start=$(date +%s )
	time while [[ $(( $(date +%s) - start )) -lt $duration ]]
    do
		#echo "start time is: $start"
		#echo "current time is: $(date +%s)"
  		#echo "diff is: $(($(date +%s) - $start ))"
		time conn-ovs; echo "Number of switches connected: $numsw. Events generated: $(( ($numport + 2) * $numsw )) - each switch added generates one switch event, one default port event, and $numport dataplane port events."
		time disconn-ovs; echo "Number of switches disconnected: $numsw. Events generated: $(( ($numport + 2) * $numsw )) - each switch added generates one switch event, one default port event, and $numport dataplane port events."
		let "iter = iter + 1"
	done
    echo "Iteration is: $iter"
	let "total = (( iter * numsw * (numport + 2))) "
	echo "************************** "
    echo "Total number of switches connected/disconnected: $(( iter * numsw * 2 )). Total events generated: $(( 2 * total)) - each switch added generates one switch event, one default port event, and $numport dataplane port events."
	echo "**************************"
	echo ""
	echo "deleting $numsw ovs switches ..."
	del-ovs
}

case "$1" in
    addsw)
        time add-ovs
        ;;
    delsw)
        time del-ovs
        ;;
    startload)
		echo $sleeptimer
        time loadsw
        ;;
    chksw)
        time get-ovs
        ;;
    #*)    
    #exit 1
esac




