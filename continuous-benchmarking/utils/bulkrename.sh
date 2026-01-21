for d in results-*
do
cd $d
#../../rename2.sh cbmc.2018-01-31 2018-11-07_0000 "2018-11-07 00:00:00" 8640288 8640288-minisat-enhanced 
../../rename2.sh cbmc.2018-11-06 2018-11-06_0001 "2018-11-06 00:00:00" 9494ebe92f6f98ddb7bdc9f32bcbb04adcf6e191 8640288-minisat-base
../../rename2.sh cbmc.2018-11-06 2018-11-06_0000 "2018-11-06 00:00:00" 9494ebe92f6f98ddb7bdc9f32bcbb04adcf6e191 8640288-minisat-base
cd ..
bin/table-generator $d/*.xml.bz2
for f in $d/*table.html; do cp $f ~/www/public/benchexec/$d/index.html; done
for f in $d/*diff.html; do cp $f ~/www/public/benchexec/$d/diff.html; done
cp $d/*.zip ~/www/public/benchexec/$d/
cp $d/*.xml.bz2 ~/www/public/benchexec/$d/
rm $d/*.html $d/*.csv
done
