#!/bin/bash
#
# Usage: checkalllitmus.sh
#
# Runs all .litmus tests, placing the output in .litmus.out files.

failed=0
for i in *.litmus
do
	herd7 -c11 $i > $i.out 2>&1
	ret=$?
	if test "$ret" -ne 0
	then
		failed=1
	fi
done
exit $failed
