#!/bin/bash

seeds=(8355 3717 5877 2829 2339 9845 233 4263 2618 9965 1624 5707 2842 130 252 9914 8323 9375 4363 2499 2877 5989 1850 5917 7847)

for file in ./instances/*; do
  if [ -d $file ]; then
    echo "no"
  else
    if [ "${file: -3}" == ".cs" ]; then #  this is the snag
      for seed in "${seeds[@]}"; do
        ./instances/output $file -seed $seed;
      done 
    fi
  fi
done
