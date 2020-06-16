#!/bin/bash
read -p "please enter a path : " var
cd $var
files=(*)
count=${#files[@]}
for (( i=0 ; i < count ;i++ )); do
    for (( j=i+1 ; j < count ; j++ )); do
        if diff -q "${files[i]}" "${files[j]}"  >/dev/null ; then
            echo "${files[i]} and ${files[j]} are the same"
        fi
    done
done
