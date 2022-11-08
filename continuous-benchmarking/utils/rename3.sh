TIMESTAMP_FILE=$1
TIMESTAMP_TEXT="$2"

for f in *.zip
do
  unzip $f > /dev/null
  rm $f
  D=`echo $f | rev | cut -c5- | rev`
  #echo "old dir: $D"
  NEWD="cbmc.${TIMESTAMP_FILE}.logfiles"
  #echo "new dir: $NEWD"
  mv $D $NEWD
  zip -r ${NEWD}.zip $NEWD > /dev/null
  rm -rf $NEWD
done
for f in *.bz2
do
  bunzip2 $f 
  F=`echo $f | rev | cut -c5- | rev`
  SUFFIX=`echo $F | cut -c22-`
  NEWF="cbmc.${TIMESTAMP_FILE}.${SUFFIX}"
  #echo "new file: $NEWF"
  mv $F $NEWF
  sed -i.bak "s/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\} [0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\} UTC/${TIMESTAMP_TEXT}/g" $NEWF
  sed -i.bak "s/$3/$4/g" $NEWF
  bzip2 $NEWF
  rm *.bak
done
