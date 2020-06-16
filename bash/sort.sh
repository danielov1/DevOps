#!/bin/bash

funcA () {
    ls -ltr
}

funcB () {
    ls -lt
}

while ! [[ $chioce =~ ^(1|2)$ ]]
do
read -p "please enter 1 for ascending or 2 for decsending: " choice
if [ $choice == 1 ];then
funcA
else
if [ $choice == 2 ];then
functB
fi
fi
done
