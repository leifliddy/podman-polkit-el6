# podman-polkit-el6

Builds the **polkit-0.96-11.el6_10.2** rpms for Centos 6.

The SRPM includes the patch the resolves **RHSA-2022:0269**

**Fedora package install**
```
dnf install podman python3-podman python3-pydbus python3-termcolor
```

**non-interactive auto build**
```
# create podman image and run the container
./script-podman.py --auto
```

**interactive build**  
Useful if you need to modify the SRPM, troubleshoot an issue, test out the environment...etc
```
# create podman image and run the container
./script-podman.py

# then login to the container with:
podman exec -it clamav_builder_6 /bin/bash

# copy rpms to shared volume output_rpms/
./01.copy.rpms.to.output_rpm.sh

# logout of the container with 
Control+D or exit
```

**the RPM's will now be found under output_rpm/**
```
[leif.liddy@black podman-polkit-el6]$ ll output_rpm/
total 940
-rw-r--r--. 1 leif.liddy leif.liddy 165128 Feb  8 15:35 polkit-0.96-11.el6_10.2.x86_64.rpm
-rw-r--r--. 1 leif.liddy leif.liddy 475856 Feb  8 15:35 polkit-debuginfo-0.96-11.el6_10.2.x86_64.rpm
-rw-r--r--. 1 leif.liddy leif.liddy   7112 Feb  8 15:35 polkit-desktop-policy-0.96-11.el6_10.2.noarch.rpm
-rw-r--r--. 1 leif.liddy leif.liddy  28512 Feb  8 15:35 polkit-devel-0.96-11.el6_10.2.x86_64.rpm
-rw-r--r--. 1 leif.liddy leif.liddy 277564 Feb  8 15:35 polkit-docs-0.96-11.el6_10.2.x86_64.rpm
```
