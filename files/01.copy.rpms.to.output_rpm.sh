#!/bin/bash

find /output_rpm/ -type f | grep '\.rpm$' | xargs rm -f
find /root/rpmbuild/RPMS/ -type f | grep '\.rpm$' | xargs cp -t /output_rpm/

# copy SRPM
#find /root/rpmbuild/SRPMS/ | grep '\.rpm$' | xargs cp -t /output_rpm/

echo -e "\ncontents of /output_rpm"
ls -lA /output_rpm | grep -v .gitignore
