%global branch master
%global candidate rc2

%global with_check 0

Name:           smoker
Version:        2.0
Release:        7.%{candidate}%{?dist}
Epoch:          1
Summary:        REST extension for Flask

Group:          Applications/System
License:        BSD
URL:            https://github.com/gooddata/smoker
Source0:        https://github.com/gooddata/smoker/archive/%{branch}.tar.gz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python2-devel python-setuptools-devel python-psutil python-simplejson python-argparse PyYAML
Requires:       python-flask-restful >= 1:0.3.1-5
Requires:       python-setproctitle
Obsoletes:      gdc-smoker


%description
Smoker (aka Smoke Testing Framework) is a framework for distributed execution
of Python modules, shell commands or external tools. It executes configured
plugins on request or periodically, unifies output and provide it via REST API
for it's command-line or other client.

%prep
%setup -q -n smoker-%{branch}

%build
%{__python} setup.py build

%install
%{__rm} -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

%if 0%{?with_check}
%check
%{__python} setup.py test
%endif #with_check

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{python_sitelib}/*.egg-info
%{python_sitelib}/smoker
/etc/rc.d/init.d/smokerd
/etc/smokerd/smokercli-example.yaml
/etc/smokerd/smokerd-example.yaml
/usr/bin/check_smoker_plugin.py
/usr/bin/smokercli.py
/usr/bin/smokerd.py
