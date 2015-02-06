Summary:	Log monitoring program
Name:		tenshi
Version:	0.15
Release:	2
Group:		Monitoring
License:	Public Domain
Url:		http://www.inversepath.com/tenshi.html
Source0:	http://dev.inversepath.com/download/%{name}/%{name}-%{version}.tar.gz
Source1:	tenshi.service
Source2:	tenshi.mandriva-conf
Patch0:		tenshi-0.14-buildfix.diff
Requires:	perl

%define debug_package %{nil}

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
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}.d
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
mkdir -p %{buildroot}%{_mandir}/man8/
mkdir -p %{buildroot}/var/run/%{name}/

%makeinstall

rm -rf %{buildroot}%{_sysconfdir}/%{name}
install -m0644 -D %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
install -m755 %{SOURCE2} %{buildroot}%{_sysconfdir}/%{name}.conf
touch %{buildroot}/var/run/%{name}/%{name}.pid
mkdir -p %{buildroot}/var/log/%{name}
mkfifo %{buildroot}/var/log/%{name}.fifo

sed "s:sysconfig:%{_sysconfdir}/sysconfig:" -i %{buildroot}%{_unitdir}/%{name}.service

%pre
%_pre_useradd %{name} /dev/null /sbin/nologin

%post
%systemd_post %{name}
if [ ! -n "`grep '/var/log/tenshi.fifo' %{_sysconfdir}/security/msec/perms.conf`" ] ; then
	echo "/var/log/tenshi.fifo	current.tenshi 640" >> \
		%{_sysconfdir}/security/msec/perms.conf
fi

if [ ! -n "`grep '# BEGIN: Automatically added by tenshi installation' /etc/syslog-ng.conf`" ] ; then
cat << EOF >> /etc/syslog-ng.conf
# BEGIN: Automatically added by tenshi installation
destination d_tenshi {
	pipe("/var/log/tenshi.fifo"
	group(tenshi)
	perm(0640)
	);
};
filter f_level_tenshi { level(debug..emerg); };
log { source(s_sys); filter(f_level_tenshi); destination(d_tenshi); };
# END
EOF

elif [ ! -n "`grep '# BEGIN: Automatically added by tenshi installation' %{_sysconfdir}/syslog.conf`" ] ; then
cat << EOF >> %{_sysconfdir}/syslog.conf
# BEGIN: Automatically added by tenshi installation
*.*					-/var/log/tenshi.fifo
# END
EOF

elif [ -d %{_sysconfdir}/rsyslog.d ] ; then
	if [ ! -e %{_sysconfdir}/rsyslog.d/tenshi.conf ] ; then
		cat << EOF >> %{_sysconfdir}/rsyslog.d/tenshi.conf
# Create by tenshi install
*.* |/var/log/tenshi.fifo
EOF
	fi

else
	echo "Not found your syslog daemon's config file."
	echo "Please setup with your hand."
fi

%preun
%systemd_preun %{name}
%_preun_syslogdel 

%postun
%_postun_userdel %{name}
if [ ! -e %{_sysconfdir}/rsyslog.d/tenshi.conf ] ; then
	rm -f %{_sysconfdir}/rsyslog.d/tenshi.conf
fi

%files
%defattr(644,root,root,755)
%doc README INSTALL CREDITS LICENSE Changelog FAQ tenshi.conf
%attr(644,root,root) %config(noreplace) %{_sysconfdir}/%{name}.conf
%attr(0644,root,root) %{_unitdir}/%{name}.service
%attr(755,root,root) %{_bindir}/%{name}
%{_mandir}/man8/%{name}.8*
%dir %attr(755,root,root) %{_sysconfdir}/%{name}.d
%dir %attr(755,tenshi,tenshi) /var/run/%{name}
%ghost %attr(600,tenshi,tenshi) /var/run/%{name}/%{name}.pid
%attr(644,root,tenshi) /var/log/%{name}.fifo
