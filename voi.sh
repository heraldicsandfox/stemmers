#!/bin/sh
arr=(krovetz lovins nostemmer paicehusk porter porter2 sstemmer trunc4 trunc5 lemmatized)
N=$1
T=$2
let "i = ( $3 / 10 ) % 10"
let "j = $3 % 10"
ulimit -v unlimited
if [ $i -le $j ]; then
echo vois/voi-$N-$T-${arr[$i]}-${arr[$j]}.voi
if [ ! -f vois/voi-$N-$T-${arr[$i]}-${arr[$j]}.voi ]; then
    for filea in states/$N-${arr[$i]}-$T-*.gz
    do
        for fileb in states/$N-${arr[$j]}-$T-*.gz
        do
            java VariationOfInformation $T $filea $fileb >> vois/voi-$N-$T-${arr[$i]}-${arr[$j]}.voi
        done
    done
fi
fi
