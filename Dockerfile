FROM registry.centos.org/centos:6

ENV polkit_srpm polkit-0.96-11.el6_10.2.src.rpm

COPY files/bashrc /root/.bashrc
COPY files/*.repo /etc/yum.repos.d
COPY files/$polkit_srpm /root

RUN rm -f /etc/yum.repos.d/CentOS-* &&\
    yum update -y &&\
    yum install -y rpm-build vim-enhanced yum-utils &&\
    yum-builddep -y /root/$polkit_srpm &&\
    yum clean all &&\
    find /root/ -type f | egrep 'anaconda-ks.cfg|install.log|install.log.syslog' | xargs rm -f &&\
    mkdir /root/.bashrc.d

COPY files/bashrc-rpmbuild /root/.bashrc.d/rpmbuild

WORKDIR /root

CMD ["/bin/bash"]
