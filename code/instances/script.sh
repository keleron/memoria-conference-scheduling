#!/bin/bash

for file in ./*; do
  if [ -d $file ]; then
    echo "no"
  else
    if [ "${file: -3}" == ".cs" ]; then #  this is the snag
      ./output $file;
    fi
  fi
done
