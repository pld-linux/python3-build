#
# Conditional build:
%bcond_without	doc		# API documentation
%bcond_without	tests		# unit tests
%bcond_with	bootstrap	# bootstrapping without build and install installed

%if %{with bootstrap}
%undefine	with_doc
%undefine	with_tests
%endif

%define		pyproject_hooks_version		1.2.0
%define		flit_core_version		3.11.0
%define		installer_version		0.7.0

%define		module	build
Summary:	A simple, correct Python build frontend
Summary(pl.UTF-8):	Prosty, poprawny frontend do budowania pakietów Pythona
Name:		python3-%{module}
Version:	1.3.0
Release:	1
License:	MIT
Group:		Libraries/Python
# https://pypi.org/simple/build/
Source0:	https://files.pythonhosted.org/packages/source/b/build/build-%{version}.tar.gz
# Source0-md5:	48f7fbc11051430eab3c1abe216bed7a
Source1:	https://files.pythonhosted.org/packages/source/p/pyproject_hooks/pyproject_hooks-%{pyproject_hooks_version}.tar.gz
# Source1-md5:	ed3dd1b984339e83e35f676d7169c192
Source2:	https://files.pythonhosted.org/packages/source/f/flit-core/flit_core-%{flit_core_version}.tar.gz
# Source2-md5:	6d677b1acef1769c4c7156c7508e0dbd
Source3:	https://files.pythonhosted.org/packages/source/i/installer/installer-%{installer_version}.tar.gz
# Source3-md5:	d961d1105c9270049528b1167ed021bc
URL:		https://pypi.org/project/build/
%if %{without bootstrap}
BuildRequires:	python3-build
BuildRequires:	python3-installer
BuildRequires:	python3-flit_core >= 3.11
%endif
BuildRequires:	python3-modules >= 1:3.9
%if %{with tests}
BuildRequires:	python3-filelock >= 3
BuildRequires:	python3-packaging >= 19.1
BuildRequires:	python3-pyproject_hooks
BuildRequires:	python3-pytest >= 6.2.4
BuildRequires:	python3-pytest-mock >= 2
BuildRequires:	python3-pytest-rerunfailures >= 9.1
BuildRequires:	python3-setuptools >= 1:67.8.0
BuildRequires:	python3-setuptools_scm >= 6
%if "%{_ver_lt %{py3_ver} 3.11}" == "1"
BuildRequires:	python3-tomli >= 1.1.0
%endif
BuildRequires:	python3-virtualenv >= 20.17
BuildRequires:	python3-wheel >= 0.36.0
%endif
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 2.044
%if %{with doc}
BuildRequires:	python3-furo >= 2023.08.17
BuildRequires:	python3-sphinx_argparse_cli >= 1.5
BuildRequires:	python3-sphinx_autodoc_typehints >= 1.10
BuildRequires:	python3-sphinx_issues >= 3.0.0
BuildRequires:	sphinx-pdg-3 >= 7.0
%endif
%if %{with bootstrap}
Provides:	python3-flit_core = %{flit_core_version}
Provides:	python3-pyproject_hooks = %{pyproject_hooks_version}
Obsoletes:	python3-flit_core <= %{flit_core_version}
Obsoletes:	python3-pyproject_hooks <= %{pyproject_hooks_version}
%endif
Requires:	python3-modules >= 1:3.9
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
A simple, correct Python build frontend.

%description -l pl.UTF-8
Prosty, poprawny frontend do budowania pakietów Pythona.

%package apidocs
Summary:	API documentation for Python %{module} module
Summary(pl.UTF-8):	Dokumentacja API modułu Pythona %{module}
Group:		Documentation

%description apidocs
API documentation for Python %{module} module.

%description apidocs -l pl.UTF-8
Dokumentacja API modułu Pythona %{module}.

%prep
%setup -q %{?with_bootstrap:-a1 -a2 -a3} -n %{module}-%{version}

%build
%if %{with bootstrap}
export PYTHONPATH=$(pwd)/src:$(pwd)/pyproject_hooks-%{pyproject_hooks_version}/src:$(pwd)/flit_core-%{flit_core_version}:$(pwd)/installer-%{installer_version}/src
%py3_build_pyproject --skip-dependency-check

cd pyproject_hooks-%{pyproject_hooks_version}
%py3_build_pyproject --skip-dependency-check

cd ../flit_core-%{flit_core_version}
%py3_build_pyproject --skip-dependency-check
cd ..
%else
%py3_build_pyproject
%endif

%if %{with tests}
# test_check_dependencies fails as of 1.3.0+flit_core 3.12.0
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTEST_PLUGINS=rerunfailures,pytest_mock \
PYTHONPATH=$(pwd)/src \
%{__python3} -m pytest tests -m 'not network and not pypy3323bug' -k 'not test_check_dependencies'
%endif

%if %{with doc}
PYTHONPATH=$(pwd)/src \
sphinx-build-3 -b html -d docs/_build/doctrees docs docs/_build/html
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with bootstrap}
export PYTHONPATH=$(pwd)/src:$(pwd)/pyproject_hooks-%{pyproject_hooks_version}/src:$(pwd)/flit_core-%{flit_core_version}:$(pwd)/installer-%{installer_version}/src
cd pyproject_hooks-%{pyproject_hooks_version}
%py3_install_pyproject

cd ../flit_core-%{flit_core_version}
%py3_install_pyproject
cd ..
%endif

%py3_install_pyproject

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc CHANGELOG.rst
%attr(755,root,root) %{_bindir}/pyproject-build
%{py3_sitescriptdir}/%{module}
%{py3_sitescriptdir}/%{module}-%{version}*.dist-info
%if %{with bootstrap}
%{py3_sitescriptdir}/flit_core
%{py3_sitescriptdir}/flit_core-%{flit_core_version}.dist-info
%{py3_sitescriptdir}/pyproject_hooks
%{py3_sitescriptdir}/pyproject_hooks-%{pyproject_hooks_version}.dist-info
%endif

%if %{with doc}
%files apidocs
%defattr(644,root,root,755)
%doc docs/_build/html/{_static,*.html,*.js}
%endif
