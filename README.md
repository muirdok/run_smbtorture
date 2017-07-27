# run_smbtorture
Preconditions:
1. Installed ansible: http://docs.ansible.com/ansible/latest/intro_installation.html#latest-releases-via-apt-ubuntu
2. Python3 
3. Configured vmvars.yml to run smbtorture
4. Configured settings.ini to post results into testrails
5. Configure hosts file with target ip (ssh binded as well to root)
6. Builded smbtorture

 ansible-playbook run_smbtorture.yml --extra-vars "publish=true WORKSPACE=/home/user/runsuite"

where is:
"publish" 	could be true\false to post results or not
"WORKSPACE"	path to diresctory


HOW TO Build smbtorture:

apt-get install acl attr autoconf bison build-essential \
  debhelper dnsutils docbook-xml docbook-xsl flex gdb krb5-user \
  libacl1-dev libaio-dev libattr1-dev libblkid-dev libbsd-dev \
  libcap-dev libcups2-dev libgnutls-dev libjson-perl \
  libldap2-dev libncurses5-dev libpam0g-dev libparse-yapp-perl \
  libpopt-dev libreadline-dev perl perl-modules pkg-config \
  python-all-dev python-dev python-dnspython python-crypto \
  xsltproc zlib1g-dev
./configure --enable-developer --without-ad-dc
make smbtorture

