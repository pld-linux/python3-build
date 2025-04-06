# Conditional build:
%bcond_without	doc		# API documentation
%bcond_without	tests		# unit tests
%bcond_with	bootstrap	# bootsrapping without build and install installed

%if %{with bootstrap}
%undefine	with_doc
%undefine	with_tests
%endif

# docs need furo, furo needs nodejs :(
%ifarch x32
%undefine	with_doc
%endif

%define		pyproject_hooks_version		1.2.0
%define		flit_core_version		3.10.1
%define		installer_version		0.7.0

%define		module	build
Summary:	A simple, correct Python build frontend
Name:		python3-%{module}
Version:	1.2.2
Release:	2
License:	MIT
Group:		Libraries/Python
# https://pypi.org/simple/build/
Source0:	https://files.pythonhosted.org/packages/source/b/build/build-%{version}.tar.gz
# Source0-md5:	f80cc64db8e7fd8f8403a5e8a0562d4d
Source1:	https://files.pythonhosted.org/packages/source/p/pyproject_hooks/pyproject_hooks-%{pyproject_hooks_version}.tar.gz
# Source1-md5:	ed3dd1b984339e83e35f676d7169c192
Source2:	https://files.pythonhosted.org/packages/source/f/flit-core/flit_core-%{flit_core_version}.tar.gz
# Source2-md5:	a3381dd58e23e9826c5199b1f70318b0
Source3:	https://files.pythonhosted.org/packages/source/i/installer/installer-%{installer_version}.tar.gz
# Source3-md5:	d961d1105c9270049528b1167ed021bc
Patch0:		flit-core-PEP639.patch
Patch1:		post1.patch
Patch2:		non-py313-or-network-tests.patch
URL:		https://pypi.org/project/build/
%if %{without bootstrap}
BuildRequires:	python3-build
BuildRequires:	python3-installer
BuildRequires:	python3-flit_core
%endif
BuildRequires:	python3-modules >= 1:3.2
%if %{with tests}
BuildRequires:	python3-filelock
BuildRequires:	python3-pytest-mock
BuildRequires:	python3-pytest-rerunfailures
BuildRequires:	python3-tomli
BuildRequires:	python3-virtualenv
%endif
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 2.044
%if %{with doc}
BuildRequires:	python3-furo
BuildRequires:	python3-sphinx_argparse_cli
BuildRequires:	python3-sphinx_autodoc_typehints
BuildRequires:	sphinx-pdg-3
%endif
Requires:	python3-modules >= 1:3.2
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
A simple, correct Python build frontend.

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
%patch -P 0 -p1
%patch -P 1 -p1
%patch -P 2 -p1

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
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTEST_PLUGINS=rerunfailures,pytest_mock,check \
%{__python3} -m pytest tests
%endif

%if %{with doc}
cd docs
sphinx-build-3 -b html -d _build/doctrees   . _build/html
cd ..
rm -rf docs/_build/html/_sources
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
%doc docs/_build/html/*
%endif
