%define	name tenshi
%define	version 0.10
%define	release %mkrel 0.4

Summary:	Tenshi log monitoring program
Name:		%{name}
Version:	%{version}
Release:	%{release}
Group:		Monitoring
License:	Public Domain
Url:		http://dev.inversepath.com/trac/tenshi/wiki/
Source0:	%{name}-%{version}.tar.gz
Source1:	tenshi.mandriva-init
Source2:	tenshi.mandriva-conf
Patch0:		tenshi-mdv.buildfix.diff
Requires:	perl
Buildroot:	%{_tmppath}/%{name}-%{version}

%description
tenshi is a log monitoring program, designed to watch one or more log
files for lines matching user defined regular expressions and report
on the matches. The regular expressions are assigned to queues which
have an alert interval and a list of mail recipients.

%prep
%setup -q
%patch0 -p1

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_initrddir}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}.d
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
mkdir -p %{buildroot}%{_mandir}/man8/
mkdir -p %{buildroot}/var/run/%{name}/

%makeinstall

rm -rf %{buildroot}%{_sysconfdir}/%{name}
install -m755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}
install -m755 %{SOURCE2} %{buildroot}%{_sysconfdir}/%{name}.conf
touch %{buildroot}/var/run/%{name}/%{name}.pid
mkdir -p %{buildroot}/var/log/
mkfifo %{buildroot}/var/log/tenshi.fifo

%pre
%_pre_useradd %{name} /dev/null /sbin/nologin

%post
%_post_service %{name}
[[ -e /var/log/tenshi.fifo ]] || mkfifo /var/log/tenshi.fifo
cat <<EOF
Please setup the Tenshi's facility in the syslog configuration file.
The default facility: 
EOF
%_post_syslogadd /var/log/tenshi.fifo -s s_sys
cat <<EOF

I use without a facilty and the Tenshi alert me all problem 
but it may flooding in admin's mailbox.
Make up your mind.

Best regards: Gergely Lonyai
EOF

%preun
%_preun_service %{name}
%_preun_syslogdel 
rm -f /var/log/tensi.fifo

%postun
%_postun_userdel %{name}

%files
%defattr(644,root,root,755)
%doc README INSTALL CREDITS LICENSE Changelog FAQ tenshi.conf
%attr(644,root,root) %config(noreplace) %{_sysconfdir}/%{name}.conf
%attr(755,root,root) %config(noreplace) %{_initrddir}/%{name}
%attr(755,root,root) %{_bindir}/%{name}
%{_mandir}/man8/%{name}.8*
%dir %attr(755,root,root) %{_sysconfdir}/%{name}.d
%dir %attr(755,tenshi,tenshi) /var/run/%{name}
%ghost %attr(600,tenshi,tenshi) /var/run/%{name}/%{name}.pid
%attr(755,root,root) /var/log/tenshi.fifo

%clean
rm -rf %{buildroot}

