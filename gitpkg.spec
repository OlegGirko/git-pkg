# 
# Do NOT Edit the Auto-generated Part!
# Generated by: spectacle version 0.27
# 

Name:       gitpkg

# >> macros
# Magic
%{!?python3_sitelib: %global python3_sitelib %(%{__python3} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python3_sitearch: %global python3_sitearch %(%{__python3} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%define obs_libdir /usr/lib
# << macros

Summary:    Helps manage packaging in git
Version:    0.1.4
Release:    1
Group:      Development
License:    GPLv2
BuildArch:  noarch
Source0:    gitpkg-%{version}.tar.gz
Source100:  gitpkg.yaml
Patch1:     0001-Add-url-parameter-to-allow-gitpkg-service-to-use-rep.patch
Patch2:     0002-Remove-shebang-in-BlockDumper-Python-module.patch
Patch3:     0003-Make-code-Python-3-compatible.patch
Patch4:     0004-Use-https-protocol-instead-of-git-one.patch
Requires:   git
Requires:   pristine-tar
Requires:   python3-yaml
Requires:   grep
Requires:   coreutils
Requires:   findutils
BuildRequires:  python3-devel

%description
Allows the packaging to be maintained in a discrete git tree in the same git repo as the source

%package -n obs-service-gitpkg
Summary:    An OBS source service: Uses gitpkg to retrieve source
Group:      Development
Requires:   %{name} = %{version}-%{release}
Requires:   gitpkg

%description -n obs-service-gitpkg
Uses gitpkg to retrieve source

%prep
%setup -q -n src
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

# >> setup
# << setup

%build
# >> build pre
# << build pre


PYTHON=%{__python3} make %{?jobs:-j%jobs}

# >> build post
# << build post

%install
rm -rf %{buildroot}
# >> install pre
# << install pre
PYTHON=%{__python3} %make_install

# >> install post
# << install post

%files
%defattr(-,root,root,-)
%{_bindir}/git-pkg
%{_bindir}/gp_release
%{_bindir}/gp_setup
%{_bindir}/gp_mkpkg
%dir %{_datadir}/gitpkg/
%{_datadir}/gitpkg/gp_common
%{python3_sitelib}/*
# >> files
# << files

%files -n obs-service-gitpkg
%defattr(-,root,root,-)
%dir %{obs_libdir}/obs/
%dir %{obs_libdir}/obs/service/
%{obs_libdir}/obs/service/gitpkg
%{obs_libdir}/obs/service/gitpkg.service
# >> files obs-service-gitpkg
# << files obs-service-gitpkg
