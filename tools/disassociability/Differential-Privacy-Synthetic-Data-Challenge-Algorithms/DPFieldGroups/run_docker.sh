#!/bin/bash

# arguments: 
# $1 <input folder> 
# $2 <output folder> 
# $3 <data file> 
# $4 <specs file> 
# $5 <output file> 
# $6 <epsilon> 
# $7 [delta limit]
docker build -t gardn999_nistdp3 ./solution

if [ $# = 6 ] || [ $# = 7 ]
then
docker run -v $1:/input -v $2:/output gardn999_nistdp3 /input/$3 /input/$4 /output/$5 $6
elif [ $# = 4 ]
then
docker run -v $1:/input -v $2:/output gardn999_nistdp3 /input/$3 /input/$4 /output/8_0.csv 8.0
docker run -v $1:/input -v $2:/output gardn999_nistdp3 /input/$3 /input/$4 /output/1_0.csv 1.0
docker run -v $1:/input -v $2:/output gardn999_nistdp3 /input/$3 /input/$4 /output/0_3.csv 0.3
else
docker run -v $1:/input -v $2:/output gardn999_nistdp3
fi