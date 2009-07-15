%define	name tenshi
%define	version 0.10
%define	release %mkrel 0.1

Summary:	Tenshi log monitoring program
Name:		%{name}
Version:	%{version}
Release:	%{release}
Group:		Monitoring
License:	Public Domain
Url:		http://dev.inversepath.com/trac/tenshi/wiki/
Source0:	%{name}-%{version}.tar.gz
Source1:	tenshi.mandriva-init
Patch0:		tenshi-mdv.buildfix.diff
Requires:	perl
Buildroot:	%{_tmppath}/%{name}-buildroot

%description
tenshi is a log monitoring program, designed to watch one or more log
files for lines matching user defined regular expressions and report
on the matches. The regular expressions are assigned to queues which
have an alert interval and a list of mail recipients.

%prep
%setup
%patch0 -p1

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_initrddir}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
mkdir -p %{buildroot}%{_mandir}/man8/
mkdir -p %{buildroot}/var/run/%{name}/

%makeinstall
#make DESTDIR=%{buildroot} mandir=%{_mandir} install

install -m755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}
touch %{buildroot}%{_sysconfdir}/sysconfig/%{name}
touch %{buildroot}/var/run/%{name}/%{name}.pid

%pre
%_pre_useradd %{name} /dev/null /sbin/nologin

%post
%_preun_service %{name}

#--------------------------------------------------------------------------------
#  Take tenshi out of runlevels
#--------------------------------------------------------------------------------
%preun
%_preun_service %{name}

%postun
%_postun_userdel %{name}

%files
%defattr(644,root,root,755)
%doc README INSTALL CREDITS LICENSE Changelog FAQ tenshi.conf
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%attr(755,root,root) %config(noreplace) %{_initrddir}/%{name}
%attr(755,root,root) %{_bindir}/%{name}
%{_mandir}/man8/%{name}.8*
%dir %attr(775,tenshi,tenshi) /var/run/%{name}
%ghost %attr(600,tenshi,tenshi) /var/run/%{name}/%{name}.pid

%clean
rm -rf %{buildroot}

