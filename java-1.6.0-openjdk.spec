# If gcjbootstrap is 1 IcedTea is bootstrapped against
# java-1.5.0-gcj-devel.  If gcjbootstrap is 0 IcedTea is built against
# java-1.6.0-openjdk-devel.
%define gcjbootstrap 0

%define runtests 0

%define icedteaver 1.2
%define icedteasnapshot %{nil}
%define openjdkver b11
%define openjdkdate 10_jul_2008

%define genurl http://cvs.fedoraproject.org/viewcvs/devel/java-1.6.0-openjdk/

%define openjdkurlbase http://www.java.net/download/openjdk/jdk6/promoted/
%define openjdkurl %{openjdkurlbase}%{openjdkver}/
%define fedorazip  openjdk-6-src-%{openjdkver}-%{openjdkdate}-dfsg.tar.bz2

%define mauvedate 2008-03-11

%define multilib_arches ppc64 sparc64 x86_64

%define jit_arches %{ix86} x86_64

%ifarch %{ix86}
%define archbuild i586
%define archinstall i386
%endif
%ifarch x86_64
%define archbuild amd64
%define archinstall amd64
%endif
%ifnarch %{jit_arches}
%define archbuild %{_arch}
%define archinstall %{_arch}
%endif

# Reduce build time from 27 hours to 12 hours by only running test
# suites on JIT architectures.
%ifnarch %{jit_arches}
%define runtests 0
%endif

%define buildoutputdir openjdk/control/build/linux-%{archbuild}

%if %{gcjbootstrap}
%define icedteaopt --with-java=%{_jvmdir}/java-gcj/bin/java --with-ecj=%{_jvmdir}/java-gcj/bin/javac --with-javah=%{_jvmdir}/java-gcj/bin/javah --with-jar=%{_jvmdir}/java-gcj/bin/jar --with-rmic=%{_jvmdir}/java-gcj/bin/rmic --with-libgcj-jar=%{_jvmdir}/jre-gcj/lib/rt.jar
%define gcc_version 4.3
%else
%define icedteaopt --with-openjdk
%define gcc_version %{nil}
%endif

# Convert an absolute path to a relative path.  Each symbolic link is
# specified relative to the directory in which it is installed so that
# it will resolve properly within chrooted installations.
%define script 'use File::Spec; print File::Spec->abs2rel($ARGV[0], $ARGV[1])'
%define abs2rel %{__perl} -e %{script}

# Hard-code libdir on 64-bit architectures to make the 64-bit JDK
# simply be another alternative.
%ifarch %{multilib_arches}
%define syslibdir       %{_prefix}/lib64
%define _libdir         %{_prefix}/lib
%define archname        %{name}.%{_arch}
%define localpolicy     jce_%{javaver}_%{origin}_local_policy.%{_arch}
%define uspolicy        jce_%{javaver}_%{origin}_us_export_policy.%{_arch}
%define javaplugin      libjavaplugin.so.%{_arch}
%else
%define syslibdir       %{_libdir}
%define archname        %{name}
%define localpolicy     jce_%{javaver}_%{origin}_local_policy
%define uspolicy        jce_%{javaver}_%{origin}_us_export_policy
%define javaplugin      libjavaplugin.so
%endif

# Standard JPackage naming and versioning defines.
%define origin          openjdk
%define priority        16000
%define javaver         1.6.0
%define buildver        0

# Standard JPackage directories and symbolic links.
# Make 64-bit JDKs just another alternative on 64-bit architectures.
%ifarch %{multilib_arches}
%define sdklnk          java-%{javaver}-%{origin}.%{_arch}
%define jrelnk          jre-%{javaver}-%{origin}.%{_arch}
%define sdkdir          %{name}-%{version}.%{_arch}
%else
%define sdklnk          java-%{javaver}-%{origin}
%define jrelnk          jre-%{javaver}-%{origin}
%define sdkdir          %{name}-%{version}
%endif
%define jredir          %{sdkdir}/jre
%define sdkbindir       %{_jvmdir}/%{sdklnk}/bin
%define jrebindir       %{_jvmdir}/%{jrelnk}/bin
%ifarch %{multilib_arches}
%define jvmjardir       %{_jvmjardir}/%{name}-%{version}.%{_arch}
%else
%define jvmjardir       %{_jvmjardir}/%{name}-%{version}
%endif

# Prevent brp-java-repack-jars from being run.
%define __jar_repack 0

Name:    java-%{javaver}-%{origin}
Version: %{javaver}.%{buildver}
Release: %mkrel 0.16.%{openjdkver}.1
# java-1.5.0-ibm from jpackage.org set Epoch to 1 for unknown reasons,
# and this change was brought into RHEL-4.  java-1.5.0-ibm packages
# also included the epoch in their virtual provides.  This created a
# situation where in-the-wild java-1.5.0-ibm packages provided "java =
# 1:1.5.0".  In RPM terms, "1.6.0 < 1:1.5.0" since 1.6.0 is
# interpreted as 0:1.6.0.  So the "java >= 1.6.0" requirement would be
# satisfied by the 1:1.5.0 packages.  Thus we need to set the epoch in
# JDK package >= 1.6.0 to 1, and packages referring to JDK virtual
# provides >= 1.6.0 must specify the epoch, "java >= 1:1.6.0".
# ... but that doesn't apply to Mandriva.
Epoch:   0
Summary: OpenJDK Runtime Environment
Group:   Development/Java

License:  GPLv2 with exceptions
URL:      http://icedtea.classpath.org/
#Source0:  %{url}download/source/icedtea6-%{icedteaver}%{icedteasnapshot}.tar.gz
# hg clone http://icedtea.classpath.org/hg/icedtea6
# rm -rf icedtea6/.hg
# tar cjf icedtea6.tar.bz2 icedtea6
Source0:  %{url}download/source/icedtea6.tar.bz2
Source1:  %{fedorazip}
Source3:  %{genurl}generate-fedora-zip.sh
Source4:  README.src
Source5:  README.plugin
Source6:  mauve-%{mauvedate}.tar.gz
Source7:  mauve_tests
Source10: generate-dfsg-zip.sh
# FIXME: This patch needs to be fixed. optflags argument
# -mtune=generic is being ignored because it breaks several graphical
# applications.
# (wallluck): Fixed to patch configure.ac, not configure
Patch0:   java-1.6.0-openjdk-optflags.patch
# (walluck): Avoid crash when ht support is enabled
# Non-Fedora patches:
Patch3:   java-1.6.0-openjdk-no-ht-support.patch
# (walluck): Work around a kernel issues with long argument lists
Patch4:   java-1.6.0-openjdk-agent-allfiles.patch
# (walluck): Correctly use g++ and dynamic linking
Patch5:   java-1.6.0-openjdk-link-cpp.patch
# (Anssi 05/2008) Better desktop entry, @JAVAWSBINDIR@ needs replacing
Patch6:   icedtea6-1.2-javaws-desktop.patch
# (Anssi 07/2008) Fixes build (without static libstdc++):
#Patch8:   java-1.6.0-openjdk-link-cpp2.patch
# (Nl)    Do not show policytool on KDE menu ( KDE menu cleaning task )
Patch9:   icedtea6-1.2-policytool-desktop.patch
# (walluck): Fix icedtea-shark-build.patch
Patch10:   icedtea6-shark-build.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

BuildRequires: alsa-lib-devel
BuildRequires: cups-devel
BuildRequires: desktop-file-utils
BuildRequires: ungif-devel
BuildRequires: lesstif-devel
BuildRequires: libxi-devel
BuildRequires: libxp-devel
BuildRequires: libxt-devel
BuildRequires: libxtst-devel
BuildRequires: jpeg-devel
BuildRequires: png-devel
BuildRequires: rhino
BuildRequires: wget
BuildRequires: xalan-j2
BuildRequires: xerces-j2
BuildRequires: ant
BuildRequires: libxinerama-devel
BuildRequires: zip
%if %{gcjbootstrap}
BuildRequires: java-1.5.0-gcj-devel
%else
BuildRequires: java-1.6.0-openjdk-devel
%endif
# Mauve build requirements.
BuildRequires: x11-server-xvfb
BuildRequires: x11-font-type1
BuildRequires: x11-font-misc
BuildRequires: freetype2-devel >= 2.3.0
BuildRequires: fontconfig
BuildRequires: eclipse-ecj
# Java Access Bridge for GNOME build requirements.
Requires:      java-access-bridge
BuildRequires: java-access-bridge
# IcedTeaPlugin build requirements.
BuildRequires: glib2-devel
BuildRequires: gtk2-devel
BuildRequires: xulrunner-devel-unstable
# Zero-assembler build requirement.
%ifnarch %{jit_arches}
BuildRequires: libffi-devel
%endif

# Require /etc/pki/tls/certs/ca-bundle.crt instead of generating
# cacerts.
Requires: rootcerts
# Require jpackage-utils for ant.
Requires: jpackage-utils >= 1.7.3-1jpp.3
# Require zoneinfo data provided by tzdata-java subpackage.
Requires: tzdata-java
# Post requires alternatives to install tool alternatives.
Requires(post):   update-alternatives
# Postun requires alternatives to uninstall tool alternatives.
Requires(postun): update-alternatives
# Post requires update-desktop-database to update desktop database
# for jnlp files.
Requires(post):   desktop-file-utils
# Postun requires update-desktop-database to update desktop database
# for jnlp files.
Requires(postun): desktop-file-utils

# java-1.6.0-openjdk replaces java-1.7.0-icedtea.
Provides: java-1.7.0-icedtea = 0:1.7.0.0-24.726.2
Obsoletes: java-1.7.0-icedtea < 0:1.7.0.0-24.726.2

# Standard JPackage base provides.
Provides: jre-%{javaver}-%{origin} = %{epoch}:%{version}-%{release}
Provides: jre-%{origin} = %{epoch}:%{version}-%{release}
Provides: jre-%{javaver} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver} = %{epoch}:%{version}-%{release}
Provides: jre = %{javaver}
Provides: java-%{origin} = %{epoch}:%{version}-%{release}
Provides: java = %{epoch}:%{javaver}
# Standard JPackage extensions provides.
Provides: jndi = %{epoch}:%{version}
Provides: jndi-ldap = %{epoch}:%{version}
Provides: jndi-cos = %{epoch}:%{version}
Provides: jndi-rmi = %{epoch}:%{version}
Provides: jndi-dns = %{epoch}:%{version}
Provides: jaas = %{epoch}:%{version}
Provides: jsse = %{epoch}:%{version}
Provides: jce = %{epoch}:%{version}
Provides: jdbc-stdext = 3.0
Provides: java-sasl = %{epoch}:%{version}

%description
The OpenJDK runtime environment.

%package devel
Summary: OpenJDK Development Environment
Group:   Development/Java

# Require base package.
Requires:         %{name} = %{epoch}:%{version}-%{release}
# Post requires alternatives to install tool alternatives.
Requires(post):   update-alternatives
# Postun requires alternatives to uninstall tool alternatives.
Requires(postun): update-alternatives

# java-1.6.0-openjdk-devel replaces java-1.7.0-icedtea-devel.
Provides: java-1.7.0-icedtea-devel = 0:1.7.0.0-24.726.2
Obsoletes: java-1.7.0-icedtea-devel < 0:1.7.0.0-24.726.2

# Standard JPackage devel provides.
Provides: java-sdk-%{javaver}-%{origin} = %{epoch}:%{version}
Provides: java-sdk-%{javaver} = %{epoch}:%{version}
Provides: java-sdk-%{origin} = %{epoch}:%{version}
Provides: java-sdk = %{epoch}:%{javaver}
Provides: java-%{javaver}-devel = %{epoch}:%{version}
Provides: java-devel-%{origin} = %{epoch}:%{version}
Provides: java-devel = %{epoch}:%{javaver}

%description devel
The OpenJDK development tools.

%package demo
Summary: OpenJDK Demos
Group:   Development/Java

Requires: %{name} = %{epoch}:%{version}-%{release}

# java-1.6.0-openjdk-demo replaces java-1.7.0-icedtea-demo.
Provides: java-1.7.0-icedtea-demo = 0:1.7.0.0-24.726.2
Obsoletes: java-1.7.0-icedtea-demo < 0:1.7.0.0-24.726.2

%description demo
The OpenJDK demos.

%package src
Summary: OpenJDK Source Bundle
Group:   Development/Java

Requires: %{name} = %{epoch}:%{version}-%{release}

# java-1.6.0-openjdk-src replaces java-1.7.0-icedtea-src.
Provides: java-1.7.0-icedtea-src = 0:1.7.0.0-24.726.2
Obsoletes: java-1.7.0-icedtea-src < 0:1.7.0.0-24.726.2

%description src
The OpenJDK source bundle.

%package javadoc
Summary: OpenJDK API Documentation
Group:   Development/Java

# Post requires alternatives to install javadoc alternative.
Requires(post):   update-alternatives
# Postun requires alternatives to uninstall javadoc alternative.
Requires(postun): update-alternatives

# java-1.6.0-openjdk-javadoc replaces java-1.7.0-icedtea-javadoc.
Provides: java-1.7.0-icedtea-javadoc = 0:1.7.0.0-24.726.2
Obsoletes: java-1.7.0-icedtea-javadoc < 0:1.7.0.0-24.726.2

# Standard JPackage javadoc provides.
Provides: java-javadoc = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-javadoc = %{epoch}:%{version}-%{release}

%description javadoc
The OpenJDK API documentation.

%package plugin
Summary: OpenJDK Web Browser Plugin
Group:   Development/Java

Requires: %{name} = %{epoch}:%{version}-%{release}
Requires: %{syslibdir}/mozilla/plugins
# Post requires alternatives to install plugin alternative.
Requires(post):   update-alternatives
# Postun requires alternatives to uninstall plugin alternative.
Requires(postun): update-alternatives

# java-1.6.0-openjdk-plugin replaces java-1.7.0-icedtea-plugin.
Provides: java-1.7.0-icedtea-plugin = 0:1.7.0.0-24.726.2
Obsoletes: java-1.7.0-icedtea-plugin < 0:1.7.0.0-24.726.2

# Standard JPackage plugin provides.
Provides: java-plugin = %{javaver}
Provides: java-%{javaver}-plugin = %{epoch}:%{version}

%description plugin
The OpenJDK web browser plugin.

%prep
#%%setup -q -n icedtea6-%{icedteaver}
#%%setup -q -n icedtea6-%{icedteaver} -T -D -a 1
#%%setup -q -n icedtea6-%{icedteaver} -T -D -a 6
%setup -q -n icedtea6
%setup -q -n icedtea6 -T -D -a 1
%setup -q -n icedtea6 -T -D -a 6
%{_bindir}/autoreconf -i -v -f
%patch0
%patch3
%patch4
%patch5
%patch6 -p1
#%patch8 -p1
%patch9 -p0
%patch10
cp %{SOURCE4} .
cp %{SOURCE5} .
cp %{SOURCE7} .
%{_bindir}/find . -type f -name "*.sh" -o -type f -name "*.cgi" | %{_bindir}/xargs %{__chmod} 0755

%build
# Build IcedTea and OpenJDK.
# (Anssi 07/2008) do not hardcode /usr/bin, to allow using ccache et al:
export ALT_COMPILER_PATH=
export CFLAGS="%{optflags} -fno-tree-vrp"
%{configure2_5x} %{icedteaopt} --with-openjdk-src-zip=%{SOURCE1} --enable-liveconnect
%if %{gcjbootstrap}
make stamps/patch-ecj.stamp
%endif
make stamps/patch.stamp
make STATIC_CXX=false

touch mauve-%{mauvedate}/mauve_output
pushd %{buildoutputdir}/j2sdk-image/jre/lib
  %{__ln_s}f %{_javadir}/accessibility.properties accessibility.properties
  %{__ln_s}f %{_javadir}/gnome-java-bridge.jar ext/gnome-java-bridge.jar
popd
%if %{runtests}
# Run jtreg test suite.
{
  echo ====================JTREG TESTING========================
  export DISPLAY=:20
  Xvfb :20 -screen 0 1x1x24 -ac&
  echo $! > Xvfb.pid
  make jtregcheck -k | tee jtreg_output
  kill -9 `cat Xvfb.pid`
  unset DISPLAY
  rm -f Xvfb.pid
  echo ====================JTREG TESTING END====================
} || :

# Run Mauve test suite.
{
  pushd mauve-%{mauvedate}
    %{configure2_5x}
    make
    echo ====================MAUVE TESTING========================
    export DISPLAY=:20
    Xvfb :20 -screen 0 1x1x24 -ac&
    echo $! > Xvfb.pid
    $JAVA_HOME/bin/java Harness -vm $JAVA_HOME/bin/java \
      -file %{SOURCE7} -timeout 30000 2>&1 | tee mauve_output
    kill -9 `cat Xvfb.pid`
    unset DISPLAY
    rm -f Xvfb.pid
    echo ====================MAUVE TESTING END====================
  popd
} || :
%endif

%install
rm -rf $RPM_BUILD_ROOT

pushd %{buildoutputdir}/j2sdk-image

  # Install main files.
  install -d -m 755 $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}
  cp -a bin include lib src.zip $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}
  install -d -m 755 $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}
  cp -a jre/bin jre/lib $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}

  # Install cacerts symlink.
  rm -f $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/security/cacerts
  pushd $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/security
    RELATIVE=$(%{abs2rel} %{_sysconfdir}/pki/java \
      %{_jvmdir}/%{jredir}/lib/security)
    ln -sf $RELATIVE/cacerts .
  popd

  # Install extension symlinks.
  install -d -m 755 $RPM_BUILD_ROOT%{jvmjardir}
  pushd $RPM_BUILD_ROOT%{jvmjardir}
    RELATIVE=$(%{abs2rel} %{_jvmdir}/%{jredir}/lib %{jvmjardir})
    ln -sf $RELATIVE/jsse.jar jsse-%{version}.jar
    ln -sf $RELATIVE/jce.jar jce-%{version}.jar
    ln -sf $RELATIVE/rt.jar jndi-%{version}.jar
    ln -sf $RELATIVE/rt.jar jndi-ldap-%{version}.jar
    ln -sf $RELATIVE/rt.jar jndi-cos-%{version}.jar
    ln -sf $RELATIVE/rt.jar jndi-rmi-%{version}.jar
    ln -sf $RELATIVE/rt.jar jaas-%{version}.jar
    ln -sf $RELATIVE/rt.jar jdbc-stdext-%{version}.jar
    ln -sf jdbc-stdext-%{version}.jar jdbc-stdext-3.0.jar
    ln -sf $RELATIVE/rt.jar sasl-%{version}.jar
    for jar in *-%{version}.jar
    do
      if [ x%{version} != x%{javaver} ]
      then
        ln -sf $jar $(echo $jar | sed "s|-%{version}.jar|-%{javaver}.jar|g")
      fi
      ln -sf $jar $(echo $jar | sed "s|-%{version}.jar|.jar|g")
    done
  popd

  # Install JCE policy symlinks.
  install -d -m 755 $RPM_BUILD_ROOT%{_jvmprivdir}/%{archname}/jce/vanilla
  for file in local_policy.jar US_export_policy.jar
  do
    mv -f $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/security/$file \
      $RPM_BUILD_ROOT%{_jvmprivdir}/%{archname}/jce/vanilla
    # Touch files for ghosts.
    touch $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/security/$file
  done

  # Install versionless symlinks.
  pushd $RPM_BUILD_ROOT%{_jvmdir}
    ln -sf %{jredir} %{jrelnk}
    ln -sf %{sdkdir} %{sdklnk}
  popd

  pushd $RPM_BUILD_ROOT%{_jvmjardir}
    ln -sf %{sdkdir} %{jrelnk}
    ln -sf %{sdkdir} %{sdklnk}
  popd

  # Remove javaws man page.
  rm -f man/man1/javaws.1

  # Install man pages.
  install -d -m 755 $RPM_BUILD_ROOT%{_mandir}/man1
  for manpage in man/man1/*
  do
    # Convert man pages to UTF8 encoding.
    iconv -f ISO_8859-1 -t UTF8 $manpage -o $manpage.tmp
    mv -f $manpage.tmp $manpage
    install -m 644 -p $manpage $RPM_BUILD_ROOT%{_mandir}/man1/$(basename \
      $manpage .1)-%{name}.1
  done

  # Install demos and samples.
  cp -a demo $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}
  mkdir -p sample/rmi
  # XXX: (walluck): fix -ba --short-circuit
  test -f bin/sample.cgi && mv bin/java-rmi.cgi sample/rmi
  cp -a sample $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}

popd

# Install Javadoc documentation.
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}
cp -a %{buildoutputdir}/docs $RPM_BUILD_ROOT%{_javadocdir}/%{name}

# Install icons and menu entries.
for s in 16 24 32 48 ; do
  install -D -p -m 644 \
    openjdk/jdk/src/solaris/classes/sun/awt/X11/java-icon${s}.png \
    $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${s}x${s}/apps/java.png
done

# Install desktop files.
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/{applications,pixmaps}
cp javaws.png $RPM_BUILD_ROOT%{_datadir}/pixmaps
# (Anssi 07/2008) Mandriva patch:
sed -i 's,@JAVAWSBINDIR@,%{jrebindir},' javaws.desktop
desktop-file-install \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications javaws.desktop
for e in jconsole policytool ; do
    desktop-file-install --vendor="" --mode=644 \
        --dir=$RPM_BUILD_ROOT%{_datadir}/applications $e.desktop
done

# Find JRE directories.
find $RPM_BUILD_ROOT%{_jvmdir}/%{jredir} -type d \
  | grep -v jre/lib/security \
  | sed 's|'$RPM_BUILD_ROOT'|%dir |' \
  > %{name}.files
# Find JRE files.
find $RPM_BUILD_ROOT%{_jvmdir}/%{jredir} -type f -o -type l \
  | grep -v jre/lib/security \
  | grep -v gcjwebplugin.so \
  | grep -v IcedTeaPlugin.so \
  | sed 's|'$RPM_BUILD_ROOT'||' \
  >> %{name}.files
# Find demo directories.
find $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/demo \
  $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/sample -type d \
  | sed 's|'$RPM_BUILD_ROOT'|%dir |' \
  > %{name}-demo.files

# FIXME: remove SONAME entries from demo DSOs.  See
# https://bugzilla.redhat.com/show_bug.cgi?id=436497

# Find non-documentation demo files.
find $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/demo \
  $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/sample \
  -type f -o -type l | sort \
  | grep -v README \
  | sed 's|'$RPM_BUILD_ROOT'||' \
  >> %{name}-demo.files
# Find documentation demo files.
find $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/demo \
  $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/sample \
  -type f -o -type l | sort \
  | grep README \
  | sed 's|'$RPM_BUILD_ROOT'||' \
  | sed 's|^|%doc |' \
  >> %{name}-demo.files

# (Anssi 05/2008) for update-alternatives:
install -d -m755 %{buildroot}%{_libdir}/mozilla/plugins

%clean
rm -rf $RPM_BUILD_ROOT

# FIXME: identical binaries are copied, not linked. This needs to be
# fixed upstream.
%post
ext=%{_extension}
update-alternatives\
  --install %{_bindir}/java java %{jrebindir}/java %{priority} \
  --slave %{_jvmdir}/jre jre %{_jvmdir}/%{jrelnk} \
  --slave %{_jvmjardir}/jre jre_exports %{_jvmjardir}/%{jrelnk} \
  --slave %{_bindir}/javaws javaws %{jrebindir}/javaws \
  --slave %{_bindir}/keytool keytool %{jrebindir}/keytool \
  --slave %{_bindir}/orbd orbd %{jrebindir}/orbd \
  --slave %{_bindir}/pack200 pack200 %{jrebindir}/pack200 \
  --slave %{_bindir}/policytool policytool %{jrebindir}/policytool \
  --slave %{_bindir}/rmid rmid %{jrebindir}/rmid \
  --slave %{_bindir}/rmiregistry rmiregistry %{jrebindir}/rmiregistry \
  --slave %{_bindir}/servertool servertool %{jrebindir}/servertool \
  --slave %{_bindir}/tnameserv tnameserv %{jrebindir}/tnameserv \
  --slave %{_bindir}/unpack200 unpack200 %{jrebindir}/unpack200 \
  --slave %{_mandir}/man1/java.1$ext java.1$ext \
  %{_mandir}/man1/java-%{name}.1$ext \
  --slave %{_mandir}/man1/keytool.1$ext keytool.1$ext \
  %{_mandir}/man1/keytool-%{name}.1$ext \
  --slave %{_mandir}/man1/orbd.1$ext orbd.1$ext \
  %{_mandir}/man1/orbd-%{name}.1$ext \
  --slave %{_mandir}/man1/pack200.1$ext pack200.1$ext \
  %{_mandir}/man1/pack200-%{name}.1$ext \
  --slave %{_mandir}/man1/policytool.1$ext policytool.1$ext \
  %{_mandir}/man1/policytool-%{name}.1$ext \
  --slave %{_mandir}/man1/rmid.1$ext rmid.1$ext \
  %{_mandir}/man1/rmid-%{name}.1$ext \
  --slave %{_mandir}/man1/rmiregistry.1$ext rmiregistry.1$ext \
  %{_mandir}/man1/rmiregistry-%{name}.1$ext \
  --slave %{_mandir}/man1/servertool.1$ext servertool.1$ext \
  %{_mandir}/man1/servertool-%{name}.1$ext \
  --slave %{_mandir}/man1/tnameserv.1$ext tnameserv.1$ext \
  %{_mandir}/man1/tnameserv-%{name}.1$ext \
  --slave %{_mandir}/man1/unpack200.1$ext unpack200.1$ext \
  %{_mandir}/man1/unpack200-%{name}.1$ext

update-alternatives\
  --install %{_jvmdir}/jre-%{origin} \
  jre_%{origin} %{_jvmdir}/%{jrelnk} %{priority} \
  --slave %{_jvmjardir}/jre-%{origin} \
  jre_%{origin}_exports %{_jvmjardir}/%{jrelnk}

update-alternatives\
  --install %{_jvmdir}/jre-%{javaver} \
  jre_%{javaver} %{_jvmdir}/%{jrelnk} %{priority} \
  --slave %{_jvmjardir}/jre-%{javaver} \
  jre_%{javaver}_exports %{_jvmjardir}/%{jrelnk}

update-alternatives\
  --install \
  %{_jvmdir}/%{jrelnk}/lib/security/local_policy.jar \
  %{localpolicy} \
  %{_jvmprivdir}/%{archname}/jce/vanilla/local_policy.jar \
  %{priority} \
  --slave \
  %{_jvmdir}/%{jrelnk}/lib/security/US_export_policy.jar \
  %{uspolicy} \
  %{_jvmprivdir}/%{archname}/jce/vanilla/US_export_policy.jar

# Update for jnlp handling.
%if %mdkversion < 200900
%update_desktop_database
%update_icon_cache hicolor
%update_menus
%endif

exit 0

%postun
if ! [ -e %{jrebindir}/java ]
then
  update-alternatives --remove java %{jrebindir}/java
  update-alternatives --remove jre_%{origin} %{_jvmdir}/%{jrelnk}
  update-alternatives --remove jre_%{javaver} %{_jvmdir}/%{jrelnk}
  update-alternatives --remove \
    %{localpolicy} \
    %{_jvmprivdir}/%{archname}/jce/vanilla/local_policy.jar
fi

# Update for jnlp handling.
%if %mdkversion < 200900
%clean_desktop_database
%clean_icon_cache hicolor
%clean_menus
%endif

exit 0

%post devel
ext=%{_extension}
update-alternatives\
  --install %{_bindir}/javac javac %{sdkbindir}/javac %{priority} \
  --slave %{_jvmdir}/java java_sdk %{_jvmdir}/%{sdklnk} \
  --slave %{_jvmjardir}/java java_sdk_exports %{_jvmjardir}/%{sdklnk} \
  --slave %{_bindir}/appletviewer appletviewer %{sdkbindir}/appletviewer \
  --slave %{_bindir}/apt apt %{sdkbindir}/apt \
  --slave %{_bindir}/extcheck extcheck %{sdkbindir}/extcheck \
  --slave %{_bindir}/jar jar %{sdkbindir}/jar \
  --slave %{_bindir}/jarsigner jarsigner %{sdkbindir}/jarsigner \
  --slave %{_bindir}/javadoc javadoc %{sdkbindir}/javadoc \
  --slave %{_bindir}/javah javah %{sdkbindir}/javah \
  --slave %{_bindir}/javap javap %{sdkbindir}/javap \
  --slave %{_bindir}/jconsole jconsole %{sdkbindir}/jconsole \
  --slave %{_bindir}/jdb jdb %{sdkbindir}/jdb \
  --slave %{_bindir}/jhat jhat %{sdkbindir}/jhat \
  --slave %{_bindir}/jinfo jinfo %{sdkbindir}/jinfo \
  --slave %{_bindir}/jmap jmap %{sdkbindir}/jmap \
  --slave %{_bindir}/jps jps %{sdkbindir}/jps \
  --slave %{_bindir}/jrunscript jrunscript %{sdkbindir}/jrunscript \
  --slave %{_bindir}/jsadebugd jsadebugd %{sdkbindir}/jsadebugd \
  --slave %{_bindir}/jstack jstack %{sdkbindir}/jstack \
  --slave %{_bindir}/jstat jstat %{sdkbindir}/jstat \
  --slave %{_bindir}/jstatd jstatd %{sdkbindir}/jstatd \
  --slave %{_bindir}/native2ascii native2ascii %{sdkbindir}/native2ascii \
  --slave %{_bindir}/rmic rmic %{sdkbindir}/rmic \
  --slave %{_bindir}/schemagen schemagen %{sdkbindir}/schemagen \
  --slave %{_bindir}/serialver serialver %{sdkbindir}/serialver \
  --slave %{_bindir}/wsgen wsgen %{sdkbindir}/wsgen \
  --slave %{_bindir}/wsimport wsimport %{sdkbindir}/wsimport \
  --slave %{_bindir}/xjc xjc %{sdkbindir}/xjc \
  --slave %{_mandir}/man1/appletviewer.1$ext appletviewer.1$ext \
  %{_mandir}/man1/appletviewer-%{name}.1$ext \
  --slave %{_mandir}/man1/apt.1$ext apt.1$ext \
  %{_mandir}/man1/apt-%{name}.1$ext \
  --slave %{_mandir}/man1/extcheck.1$ext extcheck.1$ext \
  %{_mandir}/man1/extcheck-%{name}.1$ext \
  --slave %{_mandir}/man1/jar.1$ext jar.1$ext \
  %{_mandir}/man1/jar-%{name}.1$ext \
  --slave %{_mandir}/man1/jarsigner.1$ext jarsigner.1$ext \
  %{_mandir}/man1/jarsigner-%{name}.1$ext \
  --slave %{_mandir}/man1/javac.1$ext javac.1$ext \
  %{_mandir}/man1/javac-%{name}.1$ext \
  --slave %{_mandir}/man1/javadoc.1$ext javadoc.1$ext \
  %{_mandir}/man1/javadoc-%{name}.1$ext \
  --slave %{_mandir}/man1/javah.1$ext javah.1$ext \
  %{_mandir}/man1/javah-%{name}.1$ext \
  --slave %{_mandir}/man1/javap.1$ext javap.1$ext \
  %{_mandir}/man1/javap-%{name}.1$ext \
  --slave %{_mandir}/man1/jconsole.1$ext jconsole.1$ext \
  %{_mandir}/man1/jconsole-%{name}.1$ext \
  --slave %{_mandir}/man1/jdb.1$ext jdb.1$ext \
  %{_mandir}/man1/jdb-%{name}.1$ext \
  --slave %{_mandir}/man1/jhat.1$ext jhat.1$ext \
  %{_mandir}/man1/jhat-%{name}.1$ext \
  --slave %{_mandir}/man1/jinfo.1$ext jinfo.1$ext \
  %{_mandir}/man1/jinfo-%{name}.1$ext \
  --slave %{_mandir}/man1/jmap.1$ext jmap.1$ext \
  %{_mandir}/man1/jmap-%{name}.1$ext \
  --slave %{_mandir}/man1/jps.1$ext jps.1$ext \
  %{_mandir}/man1/jps-%{name}.1$ext \
  --slave %{_mandir}/man1/jrunscript.1$ext jrunscript.1$ext \
  %{_mandir}/man1/jrunscript-%{name}.1$ext \
  --slave %{_mandir}/man1/jsadebugd.1$ext jsadebugd.1$ext \
  %{_mandir}/man1/jsadebugd-%{name}.1$ext \
  --slave %{_mandir}/man1/jstack.1$ext jstack.1$ext \
  %{_mandir}/man1/jstack-%{name}.1$ext \
  --slave %{_mandir}/man1/jstat.1$ext jstat.1$ext \
  %{_mandir}/man1/jstat-%{name}.1$ext \
  --slave %{_mandir}/man1/jstatd.1$ext jstatd.1$ext \
  %{_mandir}/man1/jstatd-%{name}.1$ext \
  --slave %{_mandir}/man1/native2ascii.1$ext native2ascii.1$ext \
  %{_mandir}/man1/native2ascii-%{name}.1$ext \
  --slave %{_mandir}/man1/rmic.1$ext rmic.1$ext \
  %{_mandir}/man1/rmic-%{name}.1$ext \
  --slave %{_mandir}/man1/schemagen.1$ext schemagen.1$ext \
  %{_mandir}/man1/schemagen-%{name}.1$ext \
  --slave %{_mandir}/man1/serialver.1$ext serialver.1$ext \
  %{_mandir}/man1/serialver-%{name}.1$ext \
  --slave %{_mandir}/man1/wsgen.1$ext wsgen.1$ext \
  %{_mandir}/man1/wsgen-%{name}.1$ext \
  --slave %{_mandir}/man1/wsimport.1$ext wsimport.1$ext \
  %{_mandir}/man1/wsimport-%{name}.1$ext \
  --slave %{_mandir}/man1/xjc.1$ext xjc.1$ext \
  %{_mandir}/man1/xjc-%{name}.1$ext

update-alternatives\
  --install %{_jvmdir}/java-%{origin} \
  java_sdk_%{origin} %{_jvmdir}/%{sdklnk} %{priority} \
  --slave %{_jvmjardir}/java-%{origin} \
  java_sdk_%{origin}_exports %{_jvmjardir}/%{sdklnk}

update-alternatives\
  --install %{_jvmdir}/java-%{javaver} \
  java_sdk_%{javaver} %{_jvmdir}/%{sdklnk} %{priority} \
  --slave %{_jvmjardir}/java-%{javaver} \
  java_sdk_%{javaver}_exports %{_jvmjardir}/%{sdklnk}

%if %mdkversion < 200900
%update_menus
%endif
exit 0

%postun devel
if ! [ -e %{sdkbindir}/javac ]
then
  update-alternatives --remove javac %{sdkbindir}/javac
  update-alternatives --remove java_sdk_%{origin} %{_jvmdir}/%{sdklnk}
  update-alternatives --remove java_sdk_%{javaver} %{_jvmdir}/%{sdklnk}
fi

%if %mdkversion < 200900
%clean_menus
%endif
exit 0

%post javadoc
update-alternatives\
  --install %{_javadocdir}/java javadocdir %{_javadocdir}/%{name}/api \
  %{priority}

exit 0

%postun javadoc
if [ $1 -eq 0 ]
then
  update-alternatives --remove javadocdir %{_javadocdir}/%{name}/api
fi

exit 0

%post plugin
%if 0
update-alternatives\
  --install %{syslibdir}/mozilla/plugins/libjavaplugin.so %{javaplugin} \
  %{_jvmdir}/%{jrelnk}/lib/%{archinstall}/gcjwebplugin.so %{priority}
%else
update-alternatives\
  --install %{syslibdir}/mozilla/plugins/libjavaplugin.so %{javaplugin} \
  %{_jvmdir}/%{jrelnk}/lib/%{archinstall}/IcedTeaPlugin.so %{priority}
%endif
exit 0

%postun plugin
%if 0
if ! [ -e %{_jvmdir}/%{jrelnk}/lib/%{archinstall}/gcjwebplugin.so ]
then
  update-alternatives --remove %{javaplugin} \
    %{_jvmdir}/%{jrelnk}/lib/%{archinstall}/gcjwebplugin.so
fi
%else
if ! [ -e %{_jvmdir}/%{jrelnk}/lib/%{archinstall}/IcedTeaPlugin.so ]
then
  update-alternatives --remove %{javaplugin} \
    %{_jvmdir}/%{jrelnk}/lib/%{archinstall}/IcedTeaPlugin.so
fi
%endif
exit 0

%files -f %{name}.files
%defattr(-,root,root,-)
%doc %{buildoutputdir}/j2sdk-image/jre/ASSEMBLY_EXCEPTION
%doc %{buildoutputdir}/j2sdk-image/jre/LICENSE
%doc %{buildoutputdir}/j2sdk-image/jre/README.html
%doc %{buildoutputdir}/j2sdk-image/jre/THIRD_PARTY_README
# FIXME: The TRADEMARK file should be in j2sdk-image.
%doc openjdk/TRADEMARK
%doc AUTHORS
%doc COPYING
%doc ChangeLog
%doc NEWS
%doc README
%dir %{_jvmdir}/%{sdkdir}
%{_jvmdir}/%{jrelnk}
%{_jvmjardir}/%{jrelnk}
%{_jvmprivdir}/*
%{jvmjardir}
%dir %{_jvmdir}/%{jredir}/lib/security
# FIXME: These should be replaced by symlinks into /etc.
%config(noreplace) %{_jvmdir}/%{jredir}/lib/security/cacerts
%config(noreplace) %{_jvmdir}/%{jredir}/lib/security/java.policy
%config(noreplace) %{_jvmdir}/%{jredir}/lib/security/java.security
%ghost %{_jvmdir}/%{jredir}/lib/security/local_policy.jar
%ghost %{_jvmdir}/%{jredir}/lib/security/US_export_policy.jar
%{_datadir}/applications/*policytool.desktop
%{_datadir}/icons/hicolor/*x*/apps/java.png
%{_mandir}/man1/java-%{name}.1*
%{_mandir}/man1/keytool-%{name}.1*
%{_mandir}/man1/orbd-%{name}.1*
%{_mandir}/man1/pack200-%{name}.1*
%{_mandir}/man1/policytool-%{name}.1*
%{_mandir}/man1/rmid-%{name}.1*
%{_mandir}/man1/rmiregistry-%{name}.1*
%{_mandir}/man1/servertool-%{name}.1*
%{_mandir}/man1/tnameserv-%{name}.1*
%{_mandir}/man1/unpack200-%{name}.1*
%{_datadir}/pixmaps/javaws.png
%{_datadir}/applications/javaws.desktop

%files devel
%defattr(-,root,root,-)
%doc %{buildoutputdir}/j2sdk-image/ASSEMBLY_EXCEPTION
%doc %{buildoutputdir}/j2sdk-image/LICENSE
%doc %{buildoutputdir}/j2sdk-image/README.html
%doc %{buildoutputdir}/j2sdk-image/THIRD_PARTY_README
# FIXME: The TRADEMARK file should be in j2sdk-image.
%doc openjdk/TRADEMARK
%dir %{_jvmdir}/%{sdkdir}/bin
%dir %{_jvmdir}/%{sdkdir}/include
%dir %{_jvmdir}/%{sdkdir}/lib
%{_jvmdir}/%{sdkdir}/bin/*
%{_jvmdir}/%{sdkdir}/include/*
%{_jvmdir}/%{sdkdir}/lib/*
%{_jvmdir}/%{sdklnk}
%{_jvmjardir}/%{sdklnk}
%{_datadir}/applications/*jconsole.desktop
%{_mandir}/man1/appletviewer-%{name}.1*
%{_mandir}/man1/apt-%{name}.1*
%{_mandir}/man1/extcheck-%{name}.1*
%{_mandir}/man1/idlj-%{name}.1*
%{_mandir}/man1/jar-%{name}.1*
%{_mandir}/man1/jarsigner-%{name}.1*
%{_mandir}/man1/javac-%{name}.1*
%{_mandir}/man1/javadoc-%{name}.1*
%{_mandir}/man1/javah-%{name}.1*
%{_mandir}/man1/javap-%{name}.1*
%{_mandir}/man1/jconsole-%{name}.1*
%{_mandir}/man1/jdb-%{name}.1*
%{_mandir}/man1/jhat-%{name}.1*
%{_mandir}/man1/jinfo-%{name}.1*
%{_mandir}/man1/jmap-%{name}.1*
%{_mandir}/man1/jps-%{name}.1*
%{_mandir}/man1/jrunscript-%{name}.1*
%{_mandir}/man1/jsadebugd-%{name}.1*
%{_mandir}/man1/jstack-%{name}.1*
%{_mandir}/man1/jstat-%{name}.1*
%{_mandir}/man1/jstatd-%{name}.1*
%{_mandir}/man1/native2ascii-%{name}.1*
%{_mandir}/man1/rmic-%{name}.1*
%{_mandir}/man1/schemagen-%{name}.1*
%{_mandir}/man1/serialver-%{name}.1*
%{_mandir}/man1/wsgen-%{name}.1*
%{_mandir}/man1/wsimport-%{name}.1*
%{_mandir}/man1/xjc-%{name}.1*

%files demo -f %{name}-demo.files
%defattr(-,root,root,-)

%files src
%defattr(-,root,root,-)
%doc README.src
%{_jvmdir}/%{sdkdir}/src.zip
%if %{runtests}
# FIXME: put these in a separate testresults subpackage.
%doc mauve_tests
%doc mauve-%{mauvedate}/mauve_output
%doc jtreg_output
%endif

%files javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/%{name}

%files plugin
%defattr(-,root,root,-)
%doc README.plugin
%dir %{_libdir}/mozilla
%dir %{_libdir}/mozilla/plugins
%if 0
%{_jvmdir}/%{jredir}/lib/%{archinstall}/gcjwebplugin.so
%else
%{_jvmdir}/%{jredir}/lib/%{archinstall}/IcedTeaPlugin.so
%endif
