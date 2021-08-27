#!/usr/bin/env bash

PATH1=/home/conradb/git/NZ_noise_models/NI_stations/
PATH2=/home/conradb/git/NZ_noise_models/SI_stations/

while read line; do mkdir -p $PATH1$line; done < NI_NN_list.txt
while read line; do mkdir -p $PATH2$line; done < SI_NN_list.txt