#!/bin/bash
cat $1 | while read line
do
    for word in $line
    do
#      python3 create_case_rail.py -t $word
      echo "RUN CASE: $word"
	python3.5 create_case_rail.py -t $word

    done
done
