%define debug_package %{nil}
%define product_family ClearOS
%define variant_titlecase Server
%define variant_lowercase server
%define release_name Final
%define base_release_version 7
%define full_release_version 7
%define dist_release_version 7
%define clearos_release_version 7.2.0
%define upstream_rel 7.2
%define product_vendor clear
%define clearos_rel 2.3
%define centos_rel 2.1511
#% define beta Beta
%define dist .v%{dist_release_version}

Name:           clearos-release
Version:        %{base_release_version}
Release:        %{clearos_rel}%{?dist}
Summary:        %{product_family} release file
Group:          System Environment/Base
License:        GPLv2
Provides:       clearos-release = %{version}-%{release}
Provides:       clearos-release(upstream) = %{upstream_rel}
Obsoletes:      redhat-release-as redhat-release-es redhat-release-ws redhat-release-de
Obsoletes:      centos-release
Provides:       clearos-release-jws = 1.1
Provides:       centos-release = %{version}-%{centos_rel}.el%{dist_release_version}.centos.2.7
Provides:       centos-release(upstream) = %{upstream_rel}
Provides:       redhat-release = %{upstream_rel}
Provides:       system-release = %{upstream_rel}
Provides:       system-release(releasever) = %{base_release_version}
Source:         %{name}-%{version}.tar.gz
Source100: clearos.repo
Source101: clearos-centos.repo
Source102: clearos-epel.repo
Source103: centos-unverified.repo
Source104: epel-unverified.repo
# No idea why zfs is needed - no docs, no tracker.  Remove in future release - #7151.
Source105: clearos-zfs.repo
# TODO: FIXME: Need to hack /etc/yum.conf, so add requirement.  Kludge.
Requires(post):       yum

%post
# TODO: hacking yum.conf file
if [ -n "`grep ^distroverpkg= /etc/yum.conf 2>/dev/null`" ]; then
    sed -i -e '/^distroverpkg=.*/d' /etc/yum.conf
fi
if [ -n "`grep ^bugtracker_url= /etc/yum.conf 2>/dev/null`" ]; then
    sed -i -e '/^bugtracker_url=.*/d' /etc/yum.conf
fi

exit 0

%description
%{product_family} release files

%prep
%setup -q

%build
echo OK

%install
rm -rf %{buildroot}

# create /etc
mkdir -p %{buildroot}/etc

# create /etc/system-release and /etc/redhat-release
echo "%{product_family} release %{clearos_release_version} (%{release_name}) " > %{buildroot}/etc/clearos-release
ln -s clearos-release %{buildroot}/etc/system-release
ln -s clearos-release %{buildroot}/etc/redhat-release
ln -s clearos-release %{buildroot}/etc/centos-release

# create /etc/os-release
cat << EOF >>%{buildroot}/etc/os-release
NAME="%{product_family}"
VERSION="%{full_release_version} (%{release_name})"
ID="clearos"
ID_LIKE="rhel fedora"
VERSION_ID="%{full_release_version}"
PRETTY_NAME="%{product_family} %{full_release_version} (%{release_name})"
ANSI_COLOR="0;31"
CPE_NAME="cpe:/o:clearos:clearos:7"
HOME_URL="https://www.clearos.com/"
BUG_REPORT_URL="https://tracker.clearos.com/"

EOF

# write cpe to /etc/system/release-cpe
echo "cpe:/o:clearos:clearos:7" > %{buildroot}/etc/system-release-cpe

# create /etc/issue and /etc/issue.net
echo '\S' > %{buildroot}/etc/issue
echo 'Kernel \r on an \m' >> %{buildroot}/etc/issue
cp %{buildroot}/etc/issue %{buildroot}/etc/issue.net
echo >> %{buildroot}/etc/issue

# copy GPG keys
mkdir -p -m 755 %{buildroot}/etc/pki/rpm-gpg
for file in RPM-GPG-KEY* ; do
    install -m 644 $file %{buildroot}/etc/pki/rpm-gpg
done

# copy yum repos
mkdir -p -m 755 %{buildroot}/etc/yum.repos.d
install -m 644 %{SOURCE100} %{buildroot}/etc/yum.repos.d
install -m 644 %{SOURCE101} %{buildroot}/etc/yum.repos.d
install -m 644 %{SOURCE102} %{buildroot}/etc/yum.repos.d
install -m 644 %{SOURCE103} %{buildroot}/etc/yum.repos.d
install -m 644 %{SOURCE104} %{buildroot}/etc/yum.repos.d
install -m 644 %{SOURCE105} %{buildroot}/etc/yum.repos.d

# copy systemd presets
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system-preset/
for file in *.preset ; do
    install -m 0644 $file %{buildroot}%{_prefix}/lib/systemd/system-preset/
done

# set up the dist tag macros
install -d -m 755 %{buildroot}/etc/rpm
cat >> %{buildroot}/etc/rpm/macros.dist << EOF
# dist macros.

%%clearos_ver %{base_release_version}
%%clearos %{base_release_version}
%%centos_ver %{base_release_version}
%%centos %{base_release_version}
%%rhel %{base_release_version}
%%dist %dist
%%el%{base_release_version} 1
EOF

# use unbranded datadir
mkdir -p -m 755 %{buildroot}/%{_datadir}/clearos-release
ln -s clearos-release %{buildroot}/%{_datadir}/redhat-release
install -m 644 EULA %{buildroot}/%{_datadir}/clearos-release

# use unbranded docdir
mkdir -p -m 755 %{buildroot}/%{_docdir}/clearos-release
ln -s clearos-release %{buildroot}/%{_docdir}/redhat-release
install -m 644 GPL %{buildroot}/%{_docdir}/clearos-release
install -m 644 Contributors %{buildroot}/%{_docdir}/clearos-release

%clean
rm -rf %{buildroot}

%files
%defattr(0644,root,root,0755)
/etc/redhat-release
/etc/system-release
/etc/centos-release
/etc/clearos-release
%config(noreplace) /etc/os-release
%config /etc/system-release-cpe
%config(noreplace) /etc/issue
%config(noreplace) /etc/issue.net
/etc/pki/rpm-gpg/
%config(noreplace) /etc/yum.repos.d/*
/etc/rpm/macros.dist
%{_docdir}/redhat-release
%{_docdir}/clearos-release/*
%{_datadir}/redhat-release
%{_datadir}/clearos-release/*
%{_prefix}/lib/systemd/system-preset/*
