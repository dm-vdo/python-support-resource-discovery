%define repo_name architectures
%define repo_branch main

%define name python3-%{repo_name}
%define version 1.1.3
%define unmangled_version 1.1.3
%define release 1

Summary: %{name}
Name: %{name}
Version: %{version}
Release: %{release}
URL: https://gitlab.cee.redhat.com/vdo/open-sourcing/python/support/%{repo_name}
Source0: %{url}/-/archive/%{repo_branch}/%{repo_name}-%{repo_branch}.tar.gz
License: UNKNOWN
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch

# Build dependencies
BuildRequires: python3
BuildRequires: python3-pyyaml
BuildRequires: python-setuptools

# Runtime dependencies
Requires: python3-defaults
Requires: python3-factory

%description
UNKNOWN

%prep
%setup -n %{repo_name}-%{repo_branch}

%build
python3 setup.py build

%install
python3 setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
