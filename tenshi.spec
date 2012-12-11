%define	name tenshi
%define	version 0.12
%define	release %mkrel 0.2

Summary:	Tenshi log monitoring program
Name:		%{name}
Version:	%{version}
Release:	%{release}
Group:		Monitoring
License:	Public Domain
Url:		http://www.inversepath.com/tenshi.html
Source0:	http://dev.inversepath.com/download/%{name}/%{name}-%{version}.tar.gz
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
mkdir -p %{buildroot}/var/log/%{name}
mkfifo %{buildroot}/var/log/%{name}.fifo

%pre
%_pre_useradd %{name} /dev/null /sbin/nologin

%post
%_post_service %{name}
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
%_preun_service %{name}
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
%attr(755,root,root) %config(noreplace) %{_initrddir}/%{name}
%attr(755,root,root) %{_bindir}/%{name}
%{_mandir}/man8/%{name}.8*
%dir %attr(755,root,root) %{_sysconfdir}/%{name}.d
%dir %attr(755,tenshi,tenshi) /var/run/%{name}
%ghost %attr(600,tenshi,tenshi) /var/run/%{name}/%{name}.pid
%attr(644,root,tenshi) /var/log/%{name}.fifo

%clean
rm -rf %{buildroot}



%changelog
* Wed Nov 17 2010 Lonyai Gergely <aleph@mandriva.org> 0.12-0.2mdv2011.0
+ Revision: 598319
- Add rsyslog support.

* Fri Sep 17 2010 Lonyai Gergely <aleph@mandriva.org> 0.12-0.1mdv2011.0
+ Revision: 579175
- 0.12

* Mon Jul 20 2009 Lonyai Gergely <aleph@mandriva.org> 0.11-0.2mdv2010.0
+ Revision: 398064
- fix in config file and %%post

* Mon Jul 20 2009 Lonyai Gergely <aleph@mandriva.org> 0.11-0.1mdv2010.0
+ Revision: 398038
- update to 0.11

* Thu Jul 16 2009 Lonyai Gergely <aleph@mandriva.org> 0.10-0.5mdv2010.0
+ Revision: 396577
- fix release problem
- fix syslog settings

* Thu Jul 16 2009 Lonyai Gergely <aleph@mandriva.org> 0.10-0.4mdv2010.0
+ Revision: 396564
- fix the init script

* Thu Jul 16 2009 Lonyai Gergely <aleph@mandriva.org> 0.10-0.3mdv2010.0
+ Revision: 396543
- update the init script

* Wed Jul 15 2009 Lonyai Gergely <aleph@mandriva.org> 0.10-0.1mdv2010.0
+ Revision: 396205
- fix licence type
- fix group name
- initial version is 0.10
- create tenshi

