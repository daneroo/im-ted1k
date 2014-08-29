#!/bin/bash 
echo "This program detects and fixes tabs"
TAB=`perl -e 'print "\t"'`
#echo "This is a tab:|${TAB}| as in:"
#echo "a${TAB}b${TAB}c"
#echo "a${TAB}b${TAB}c"|od -a|head -1
echo "These python files have tabs:"
#  find . -type f -name \*.py | xargs -I ZZFILE grep -l "${TAB}" ZZFILE
for f in `find . -type f -name \*.py | xargs -I ZZFILE grep -l "${TAB}" ZZFILE`; do
    echo " $f has tabs"
    perl -e '($_ = join "",<>) =~ s/(\t)/        /g; print;' <$f >$f.notab
    perl -e '($_ = join "",<>) =~ s/(\t)/~~TABS~~/g; print;' <$f >$f.showtab
done
echo 
echo "Each of these has a .showtab, and a .notab where TABS have been replaced"
echo "To remove them:" 
echo "  find . -name \*.py.\*tab -exec rm {} \;"
echo
