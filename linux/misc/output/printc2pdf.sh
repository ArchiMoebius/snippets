
for f in `find ../ -name \*.c`; do enscript --pretty-print --color --fancy-header $f -o - | ps2pdf - $f.pdf ;mv $f.pdf ./;done;
for f in `find ../ -name \*.h`; do enscript --pretty-print --color --fancy-header $f -o - | ps2pdf - $f.pdf ;mv $f.pdf ./;done;
