#!/bin/bash

find /output_rpm/ | egrep -v '^/output_rpm/$|\.gitignore' | xargs rm -rf
rpm -ivh /root/polkit-0.96-11.el6_10.2.src.rpm
rpmbuild -ba /root/rpmbuild/SPECS/polkit.spec

# copy RPMs
find /root/rpmbuild/RPMS/ -type f | grep '\.rpm$' | xargs cp -t /output_rpm/

# copy SRPM
find /root/rpmbuild/SRPMS/ | grep '\.rpm$' | xargs cp -t /output_rpm/

echo -e "\ncontents of /output_rpm"
ls -lA /output_rpm | grep -v .gitignore
