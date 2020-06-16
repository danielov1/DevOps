for i in {1..254};
 do if ping -w 2 -q -c 1 10.0.2.$i> /dev/null ;  then 
printf " IP 10.0.2.$i is occupied\n" 10.0.2.$i ;
 fi ;
done;
