FROM registry.centos.org/centos:6

COPY files/*.repo /etc/yum.repos.d
COPY files/polkit-0.96-11.el6_10.2.src.rpm /root
COPY files/01.copy.rpms.to.output_rpm.sh /root

RUN rm -f /etc/yum.repos.d/CentOS-* &&\
    yum update -y &&\
    yum install -y rpm-build vim-enhanced yum-utils &&\
    yum-builddep -y /root/polkit-0.96-11.el6_10.2.src.rpm &&\
    yum clean all &&\
    sed -i 's/^alias/#&/' /root/.bashrc &&\
    echo -e "\nalias vi='vim'" >> ~/.bashrc &&\
    echo -e "\nalias gospec='cd ~/rpmbuild/SPECS'" >> ~/.bashrc &&\
    echo -e "\nalias gobuild='cd ~/rpmbuild/BUILD'" >> ~/.bashrc &&\
    echo -e "\nalias gosource='cd ~/rpmbuild/SOURCES'" >> ~/.bashrc &&\
    rm -f /root/anaconda-ks.cfg 2> /dev/null &&\
    rm -f /root/install.log 2> /dev/null &&\
    rm -f /root/install.log.syslog 2> /dev/null &&\
    rm -rf /output_rpm/* 2> /dev/null &&\
    rpm -ivh /root/polkit-0.96-11.el6_10.2.src.rpm &&\
    rpmbuild -ba /root/rpmbuild/SPECS/polkit.spec

WORKDIR /root

CMD ["/bin/bash"]
