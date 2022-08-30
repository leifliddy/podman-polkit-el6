FROM registry.centos.org/centos:6

COPY files/*.repo /etc/yum.repos.d
COPY files/polkit-0.96-11.el6_10.2.src.rpm /root

RUN rm -f /etc/yum.repos.d/CentOS-* &&\
    yum update -y &&\
    yum install -y rpm-build vim-enhanced yum-utils &&\
    yum-builddep -y /root/polkit-0.96-11.el6_10.2.src.rpm &&\
    yum clean all &&\
    find /root/ -type f | egrep 'anaconda-ks.cfg|install.log|install.log.syslog' | xargs rm -f &&\
    sed -i '/^alias rm.*$/d' /root/.bashrc &&\
    sed -i 's/^alias/#&/' /root/.bashrc &&\
    echo -e "\nalias vi='vim'" >> ~/.bashrc &&\
    echo -e "\nalias gospec='cd ~/rpmbuild/SPECS'" >> ~/.bashrc &&\
    echo -e "\nalias gobuild='cd ~/rpmbuild/BUILD'" >> ~/.bashrc &&\
    echo -e "\nalias gosource='cd ~/rpmbuild/SOURCES'" >> ~/.bashrc

WORKDIR /root

CMD ["/bin/bash"]
