# Some parts of OpenJDK use -O0, which is mutually exclusive with
# _FORTIFY_SOURCE
%define _fortify_cflags %nil

%define with_systemtap	1
%ifarch %arm %mips 
%define with_systemtap 0
%endif

%if %mandriva_branch == Cooker
%define with_systemtap		1
%else
%define with_systemtap		0
%define subrel			1
%endif

# If gcjbootstrap is 1 IcedTea is bootstrapped against
# java-1.5.0-gcj-devel.  If gcjbootstrap is 0 IcedTea is built against
# java-1.6.0-openjdk-devel.
%bcond_with			gcjbootstrap

%define icedteaver		1.12.3
%define icedteasnapshot		%{nil}
%define openjdkver		b27
%define openjdkdate		26_oct_2012
%define mauvedate		2008-10-22

# cabral (fhimpe) we already use java-acess-bridge in Mandriva
# define accessmajorver		1.23
# define accessminorver		0
# define accessver		%{accessmajorver}.%{accessminorver}
# define accessurl		http://ftp.gnome.org/pub/GNOME/sources/java-access-bridge/

%define multilib_arches		ppc64 sparc64 x86_64
%define jit_arches		%{ix86} x86_64 sparcv9 sparc64

%define systemtapopt		--disable-systemtap
%ifarch %{jit_arches}
  %define runtests		0
  %define build_docs		1
  %define with_fastjar		0
  %if %{with_systemtap}
    %define systemtapopt	--enable-systemtap
  %endif
%else
  %define runtests		0
  %define build_docs		0
  %define with_fastjar		1
%endif

%define buildoutputdir		openjdk.build

%if %{with gcjbootstrap}
  %define icedteaopt		%{systemtapopt}
%else
  %ifarch %{jit_arches}
    %define icedteaopt		--disable-bootstrap --with-jdk-home=/usr/lib/jvm/java-openjdk %{systemtapopt}
  %else
    %define icedteaopt		--disable-bootstrap --with-jdk-home=/usr/lib/jvm/java-openjdk
  %endif
%endif

# Convert an absolute path to a relative path.  Each symbolic link is
# specified relative to the directory in which it is installed so that
# it will resolve properly within chrooted installations.
%define script			'use File::Spec; print File::Spec->abs2rel($ARGV[0], $ARGV[1])'
%define abs2rel			%{__perl} -e %{script}

# Hard-code libdir on 64-bit architectures to make the 64-bit JDK
# simply be another alternative.
%ifarch %{multilib_arches}
  %define syslibdir		%{_prefix}/lib64
  %define _libdir		%{_prefix}/lib
  %define archname		%{name}.%{_arch}
%else
  %define syslibdir		%{_libdir}
  %define archname		%{name}
%endif

# Standard JPackage naming and versioning defines.
%define origin			openjdk
%define priority		16000
%define javaver			1.6.0
%define buildver		0

# Standard JPackage directories and symbolic links.
# Make 64-bit JDKs just another alternative on 64-bit architectures.
%ifarch %{multilib_arches}
  %define sdklnk		java-%{javaver}-%{origin}.%{_arch}
  %define jrelnk		jre-%{javaver}-%{origin}.%{_arch}
  %define sdkdir		%{name}-%{version}.%{_arch}
%else
  %define sdklnk		java-%{javaver}-%{origin}
  %define jrelnk		jre-%{javaver}-%{origin}
  %define sdkdir		%{name}-%{version}
%endif
%define jredir			%{sdkdir}/jre
%define sdkbindir		%{_jvmdir}/%{sdklnk}/bin
%define jrebindir		%{_jvmdir}/%{jrelnk}/bin
%ifarch %{multilib_arches}
  %define jvmjardir		%{_jvmjardir}/%{name}-%{version}.%{_arch}
%else
  %define jvmjardir		%{_jvmjardir}/%{name}-%{version}
%endif

%ifarch %{jit_arches}
  %if %{with_systemtap}
# Where to install systemtap tapset (links)
# We would like these to be in a package specific subdir,
# but currently systemtap doesn't support that, so we have to
# use the root tapset dir for now. To distinquish between 64
# and 32 bit architectures we place the tapsets under the arch
# specific dir (note that systemtap will only pickup the tapset
# for the primary arch for now). Systemtap uses the machine name
# aka build_cpu as architecture specific directory name.
#%#define tapsetdir /usr/share/systemtap/tapset/%{sdkdir}
    %define tapsetdir		%{_datadir}/systemtap/tapset/%{_build_cpu}
  %endif
%endif 

# Prevent brp-java-repack-jars from being run.
%define __jar_repack		0

Name:		java-%{javaver}-%{origin}
Version:	%{javaver}.%{buildver}
Release:	29.%openjdkver
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
Epoch:		0
Summary:	OpenJDK Runtime Environment
Group:		Development/Java

License:	GPLv2 with exceptions
URL:		http://icedtea.classpath.org/
Source0:	http://icedtea.classpath.org/download/source/icedtea6-%{icedteaver}%{icedteasnapshot}.tar.gz
# OpenJDK source with non-distributable bits removed, see generate-mdv-tarball.sh
Source1:	openjdk-6-src-%{openjdkver}-%{openjdkdate}-mdv.tar.xz
# (fhimpe) Disabled: we use system java-access-bridge in Mandriva
#Source2:	%{accessurl}%{accessmajorver}/java-access-bridge-%{accessver}.tar.gz
Source3:	generate-mdv-tarball.sh
Source4:	README.src
Source5:	mauve-%{mauvedate}.tar.gz
Source6:	mauve_tests
Source8:	http://icedtea.classpath.org/download/drops/jaxp144_04.zip
Source9:	http://icedtea.classpath.org/download/drops/jdk6-jaf-b20.zip
Source10:	http://icedtea.classpath.org/download/drops/jdk6-jaxws2_1_6-2011_06_13.zip
Source100:	%name.rpmlintrc
Patch1:		java-1.6.0-openjdk-accessible-toolkit.patch
Patch2:		java-1.6.0-openjdk-fontpath.patch
Patch3:		icedtea6-no-libXp.patch

BuildRequires:	pkgconfig(alsa)

BuildRequires:	ant-nodeps
BuildRequires:	cups-devel
BuildRequires:	desktop-file-utils
%if %{with_fastjar}
BuildRequires:	fastjar
%endif
BuildRequires:	ungif-devel
BuildRequires:	lesstif-devel
# BuildRequires: %{mklibname xorg-x11-devel}
BuildRequires:	x11-proto-devel
BuildRequires:	libxi-devel
BuildRequires:	libxt-devel
BuildRequires:	libxtst-devel
BuildRequires:	jpeg-devel
BuildRequires:	png-devel
BuildRequires:	xalan-j2
BuildRequires:	xerces-j2
BuildRequires:	ant
BuildRequires:	libxinerama-devel
BuildRequires:	libxrender-devel
BuildRequires:	rhino
BuildRequires:	wget
BuildRequires:	zip
BuildRequires:	automake

%ifarch %{jit_arches}
  %if %{with_systemtap}
BuildRequires:	systemtap
  %endif
%endif

%if %{with gcjbootstrap}
BuildRequires:	java-1.5.0-gcj-devel
%else
BuildRequires:	java-1.6.0-openjdk-devel
# We can't build with 1.7.0, but it tends to be the default
# if both are installed
BuildConflicts:	java-1.7.0-openjdk-devel
%endif
# Mauve build requirements.
BuildRequires:	x11-server-xvfb
BuildRequires:	x11-font-type1
BuildRequires:	x11-font-misc
BuildRequires:	pkgconfig(freetype2)
BuildRequires:	fontconfig
BuildRequires:	eclipse-ecj
# Java Access Bridge for GNOME build requirements.
Requires:	java-access-bridge
%if %{without gcjbootstrap}
BuildRequires:	java-access-bridge
%endif
# PulseAudio build requirements.
BuildRequires:	pulseaudio-devel >= 0.9.11
BuildRequires:	pulseaudio >= 0.9.11
# Zero-assembler build requirement.
%ifnarch %{jit_arches}
BuildRequires:	libffi-devel
%endif
# Require /etc/pki/java/cacerts.
Requires:	rootcerts-java
Requires:	rhino
# Require jpackage-utils for ant.
Requires:	jpackage-utils >= 1.7.3-1jpp.2
# Require zoneinfo data provided by tzdata-java subpackage.
Requires:	tzdata-java
# Post requires alternatives to install tool alternatives.
Requires(post):	update-alternatives
# Postun requires alternatives to uninstall tool alternatives.
Requires(postun): update-alternatives
# java-1.6.0-openjdk replaces java-1.7.0-icedtea.
Provides:	java-1.7.0-icedtea = 0:1.7.0.0-24.726.2
Obsoletes:	java-1.7.0-icedtea < 0:1.7.0.0-24.726.2

# FIXME fonts-ttf-dejavu-lgc is the default, but currently is not directly
# available in Mandriva
Requires:	fonts-ttf-dejavu

# Standard JPackage base provides.
Provides:	jre-%{javaver}-%{origin} = %{epoch}:%{version}-%{release}
Provides:	jre-%{origin} = %{epoch}:%{version}-%{release}
Provides:	jre-%{javaver} = %{epoch}:%{version}-%{release}
Provides:	java-%{javaver} = %{epoch}:%{version}-%{release}
Provides:	jre = %{javaver}
Provides:	java-%{origin} = %{epoch}:%{version}-%{release}
Provides:	java = %{epoch}:%{javaver}
# Standard JPackage extensions provides.
Provides:	jndi = %{epoch}:%{version}
Provides:	jndi-ldap = %{epoch}:%{version}
Provides:	jndi-cos = %{epoch}:%{version}
Provides:	jndi-rmi = %{epoch}:%{version}
Provides:	jndi-dns = %{epoch}:%{version}
Provides:	jaas = %{epoch}:%{version}
Provides:	jsse = %{epoch}:%{version}
Provides:	jce = %{epoch}:%{version}
Provides:	jdbc-stdext = 3.0
Provides:	java-sasl = %{epoch}:%{version}
Provides:	java-fonts = %{epoch}:%{version}

%description
The OpenJDK runtime environment.

%package	devel
Summary:	OpenJDK Development Environment
Group:		Development/Java

# Require base package.
Requires:         %{name} = %{epoch}:%{version}-%{release}
# Post requires alternatives to install tool alternatives.
Requires(post):	update-alternatives
# Postun requires alternatives to uninstall tool alternatives.
Requires(postun): update-alternatives

# java-1.6.0-openjdk-devel replaces java-1.7.0-icedtea-devel.
Provides:	java-1.7.0-icedtea-devel = 0:1.7.0.0-24.726.2
Obsoletes:	java-1.7.0-icedtea-devel < 0:1.7.0.0-24.726.2

# Standard JPackage devel provides.
Provides:	java-sdk-%{javaver}-%{origin} = %{epoch}:%{version}
Provides:	java-sdk-%{javaver} = %{epoch}:%{version}
Provides:	java-sdk-%{origin} = %{epoch}:%{version}
Provides:	java-sdk = %{epoch}:%{javaver}
Provides:	java-%{javaver}-devel = %{epoch}:%{version}
Provides:	java-devel-%{origin} = %{epoch}:%{version}
Provides:	java-devel = %{epoch}:%{javaver}
%if !%{build_docs}
Provides:	java-javadoc = %{epoch}:%{javaver}
%endif

%description	devel
The OpenJDK development tools.

%package	demo
Summary:	OpenJDK Demos
Group:		Development/Java

Requires:	%{name} = %{epoch}:%{version}-%{release}

# java-1.6.0-openjdk-demo replaces java-1.7.0-icedtea-demo.
Provides: java-1.7.0-icedtea-demo = 0:1.7.0.0-24.726.2
Obsoletes: java-1.7.0-icedtea-demo < 0:1.7.0.0-24.726.2

%description	demo
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

%if %{build_docs}
%package javadoc
Summary: OpenJDK API Documentation
Group:   Development/Java
BuildArch: noarch

# Post requires alternatives to install javadoc alternative.
Requires(post):   update-alternatives
# Postun requires alternatives to uninstall javadoc alternative.
Requires(postun): update-alternatives

# java-1.6.0-openjdk-javadoc replaces java-1.7.0-icedtea-javadoc.
Provides:	java-1.7.0-icedtea-javadoc = 0:1.7.0.0-24.726.2
Obsoletes:	java-1.7.0-icedtea-javadoc < 0:1.7.0.0-24.726.2

# Standard JPackage javadoc provides.
Provides:	java-javadoc = %{epoch}:%{version}-%{release}
Provides:	java-%{javaver}-javadoc = %{epoch}:%{version}-%{release}

%description	javadoc
The OpenJDK API documentation.
%endif

%prep
%setup -q -n icedtea6-%{icedteaver}
%setup -q -n icedtea6-%{icedteaver} -T -D -a 5
cp %{SOURCE4} .
cp %{SOURCE6} .

%patch3 -p1 -b .libXp~

# (oe) instead of a patch
perl -pi -e "s|libxul-unstable|libxul|g" configure*

%{_bindir}/find . -type f -name "*.sh" -o -type f -name "*.cgi" | %{_bindir}/xargs %{__chmod} 0755
%{_bindir}/autoreconf -i -v -f
./autogen.sh

%build
%ifarch sparc64 alpha
  export ARCH_DATA_MODEL=64
%endif
%ifarch alpha
  export CFLAGS="$CFLAGS -mieee"
%endif
# Build IcedTea and OpenJDK.
# (Anssi 07/2008) do not hardcode /usr/bin, to allow using ccache et al:
export ALT_COMPILER_PATH=

%{configure2_5x}					\
	%{icedteaopt}					\
	--with-openjdk-src-zip=%{SOURCE1}		\
	--with-pkgversion=mandriva-%{release}-%{_arch}	\
	--enable-pulse-java				\
	--with-jaf-drop-zip=%{SOURCE9}			\
	--with-jaxp-drop-zip=%{SOURCE8}			\
	--with-jaxws-drop-zip=%{SOURCE10}		\
	--with-javah=%{_bindir}/javah			\
%if %{with_fastjar}
	--with-jar=%{_bindir}/fastjar			\
	--with-alt-jar=%{_bindir}/fastjar		\
%endif
%if !%{build_docs}
        --disable-docs                                  \
%endif
	--with-abs-install-dir=%{_jvmdir}/%{sdkdir}

# When using a different hotspot (see hotspot.map):
#	--with-hotspot-build=hs24			\
#	--with-hotspot-src-zip=%{SOURCE7}		\

%if %{with gcjbootstrap}
make stamps/patch-ecj.stamp
%endif

make patch
patch -l -p0 -b -z .p1~ < %{PATCH1}
patch -l -p1 -b -z .p2~ < %{PATCH2}

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
  make jtregcheck -k
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
      -file %{SOURCE6} -timeout 30000 2>&1 | tee mauve_output
    kill -9 `cat Xvfb.pid`
    unset DISPLAY
    rm -f Xvfb.pid
    echo ====================MAUVE TESTING END====================
  popd
} || :
%endif

%install
pushd %{buildoutputdir}/j2sdk-image

  # Install main files.
  install -d -m 755 %{buildroot}%{_jvmdir}/%{sdkdir}
  cp -a bin include lib src.zip %{buildroot}%{_jvmdir}/%{sdkdir}
  install -d -m 755 %{buildroot}%{_jvmdir}/%{jredir}
  cp -a jre/bin jre/lib %{buildroot}%{_jvmdir}/%{jredir}

%ifarch %{jit_arches}
  %if %{with_systemtap}
    # Install systemtap support files.
    cp -a tapset %{buildroot}%{_jvmdir}/%{sdkdir}
    install -d -m 755 %{buildroot}%{tapsetdir}
    pushd %{buildroot}%{tapsetdir}
      RELATIVE=$(%{abs2rel} %{_jvmdir}/%{sdkdir}/tapset %{tapsetdir})
      ln -sf $RELATIVE/*.stp .
    popd
  %endif
%endif

  # Install cacerts symlink.
  rm -f %{buildroot}%{_jvmdir}/%{jredir}/lib/security/cacerts
  pushd %{buildroot}%{_jvmdir}/%{jredir}/lib/security
    RELATIVE=$(%{abs2rel} %{_sysconfdir}/pki/java \
      %{_jvmdir}/%{jredir}/lib/security)
    ln -sf $RELATIVE/cacerts .
  popd

  # Install extension symlinks.
  install -d -m 755 %{buildroot}%{jvmjardir}
  pushd %{buildroot}%{jvmjardir}
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
  install -d -m 755 %{buildroot}%{_jvmprivdir}/%{archname}/jce/vanilla

  # Install versionless symlinks.
  pushd %{buildroot}%{_jvmdir}
    ln -sf %{jredir} %{jrelnk}
    ln -sf %{sdkdir} %{sdklnk}
  popd

  pushd %{buildroot}%{_jvmjardir}
    ln -sf %{sdkdir} %{jrelnk}
    ln -sf %{sdkdir} %{sdklnk}
  popd

  # Install man pages.
  install -d -m 755 %{buildroot}%{_mandir}/man1
  for manpage in man/man1/*
  do
    # Convert man pages to UTF8 encoding.
    iconv -f ISO_8859-1 -t UTF8 $manpage -o $manpage.tmp
    mv -f $manpage.tmp $manpage
    install -m 644 -p $manpage %{buildroot}%{_mandir}/man1/$(basename \
      $manpage .1)-%{name}.1
  done

  # Install demos and samples.
  cp -a demo %{buildroot}%{_jvmdir}/%{sdkdir}
  mkdir -p sample/rmi
  # XXX: (walluck): fix -ba --short-circuit
  test -f bin/sample.cgi && mv bin/java-rmi.cgi sample/rmi
  cp -a sample %{buildroot}%{_jvmdir}/%{sdkdir}

popd

# Install Javadoc documentation.
%if %{build_docs}
install -d -m 755 %{buildroot}%{_javadocdir}
cp -a %{buildoutputdir}/docs %{buildroot}%{_javadocdir}/%{name}
%endif

# Install icons and menu entries.
for s in 16 24 32 48 ; do
  install -D -p -m 644 \
    openjdk/jdk/src/solaris/classes/sun/awt/X11/java-icon${s}.png \
    %{buildroot}%{_datadir}/icons/hicolor/${s}x${s}/apps/java.png
done

# Install desktop files.
install -d -m 755 %{buildroot}%{_datadir}/applications
perl -pi -e 's|(Categories=Development;)(Monitor;Java;)|$1System;$2|'	\
    jconsole.desktop
for e in jconsole policytool ; do
    desktop-file-install --vendor="" --mode=644 \
        --dir=%{buildroot}%{_datadir}/applications $e.desktop
done

# Find JRE directories.
find %{buildroot}%{_jvmdir}/%{jredir} -type d \
  | grep -v jre/lib/security \
  | sed 's|'%{buildroot}'|%dir |' \
  > %{name}.files
# Find JRE files.
find %{buildroot}%{_jvmdir}/%{jredir} -type f -o -type l \
  | grep -v jre/lib/security \
  | grep -v IcedTeaPlugin.so \
  | sed 's|'%{buildroot}'||' \
  >> %{name}.files
# Find demo directories.
find %{buildroot}%{_jvmdir}/%{sdkdir}/demo \
  %{buildroot}%{_jvmdir}/%{sdkdir}/sample -type d \
  | sed 's|'%{buildroot}'|%dir |' \
  > %{name}-demo.files

# FIXME: remove SONAME entries from demo DSOs.  See
# https://bugzilla.redhat.com/show_bug.cgi?id=436497

# Find non-documentation demo files.
find %{buildroot}%{_jvmdir}/%{sdkdir}/demo \
  %{buildroot}%{_jvmdir}/%{sdkdir}/sample \
  -type f -o -type l | sort \
  | grep -v README \
  | sed 's|'%{buildroot}'||' \
  >> %{name}-demo.files
# Find documentation demo files.
find %{buildroot}%{_jvmdir}/%{sdkdir}/demo \
  %{buildroot}%{_jvmdir}/%{sdkdir}/sample \
  -type f -o -type l | sort \
  | grep README \
  | sed 's|'%{buildroot}'||' \
  | sed 's|^|%doc |' \
  >> %{name}-demo.files

cp -fa %{buildroot}%{_jvmdir}/%{jredir}/lib/fontconfig.properties{.src,}

# Let's save a lot of space... And shut up rpmlint while at it!
pushd %buildroot%_jvmdir
for i in bin/* lib/*; do
	[ -e jre/$i ] && [ "`sha1sum $i |cut -d' ' -f1`" = "`sha1sum jre/$i |cut -d' ' -f1`" ] && ln -f $i jre/$i
done
popd

%post
ext=%{_extension}
update-alternatives\
  --install %{_bindir}/java java %{jrebindir}/java %{priority} \
  --slave %{_jvmdir}/jre jre %{_jvmdir}/%{jrelnk} \
  --slave %{_jvmjardir}/jre jre_exports %{_jvmjardir}/%{jrelnk} \
  --slave %{_bindir}/keytool keytool %{jrebindir}/keytool \
  --slave %{_bindir}/orbd orbd %{jrebindir}/orbd \
  --slave %{_bindir}/pack200 pack200 %{jrebindir}/pack200 \
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

exit 0

%postun
if [ $1 -eq 0 ]
then
  update-alternatives --remove java %{jrebindir}/java
  update-alternatives --remove jre_%{origin} %{_jvmdir}/%{jrelnk}
  update-alternatives --remove jre_%{javaver} %{_jvmdir}/%{jrelnk}
fi

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
  --slave %{_bindir}/policytool policytool %{sdkbindir}/policytool \
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
  --slave %{_mandir}/man1/policytool.1$ext policytool.1$ext \
  %{_mandir}/man1/policytool-%{name}.1$ext \
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

exit 0

%postun devel
if [ $1 -eq 0 ]
then
  update-alternatives --remove javac %{sdkbindir}/javac
  update-alternatives --remove java_sdk_%{origin} %{_jvmdir}/%{sdklnk}
  update-alternatives --remove java_sdk_%{javaver} %{_jvmdir}/%{sdklnk}
fi

exit 0

%if %{build_docs}
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
%endif

%files -f %{name}.files
%defattr(-,root,root,-)
%doc %{buildoutputdir}/j2sdk-image/jre/ASSEMBLY_EXCEPTION
%doc %{buildoutputdir}/j2sdk-image/jre/LICENSE
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
%{_jvmdir}/%{jredir}/lib/security/cacerts
# FIXME: These should be replaced by symlinks into /etc.
%config(noreplace) %{_jvmdir}/%{jredir}/lib/security/java.policy
%config(noreplace) %{_jvmdir}/%{jredir}/lib/security/java.security
%config(noreplace) %{_jvmdir}/%{jredir}/lib/security/java.security.old
%config(noreplace) %{_jvmdir}/%{jredir}/lib/security/nss.cfg
%{_datadir}/icons/hicolor/*x*/apps/java.png
%{_mandir}/man1/java-%{name}.1*
%{_mandir}/man1/keytool-%{name}.1*
%{_mandir}/man1/orbd-%{name}.1*
%{_mandir}/man1/pack200-%{name}.1*
%{_mandir}/man1/rmid-%{name}.1*
%{_mandir}/man1/rmiregistry-%{name}.1*
%{_mandir}/man1/servertool-%{name}.1*
%{_mandir}/man1/tnameserv-%{name}.1*
%{_mandir}/man1/unpack200-%{name}.1*
# FIXME: This should be %config
%{_jvmdir}/%{jredir}/lib/fontconfig.properties

%files devel
%defattr(-,root,root,-)
%doc %{buildoutputdir}/j2sdk-image/ASSEMBLY_EXCEPTION
%doc %{buildoutputdir}/j2sdk-image/LICENSE
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
%{_datadir}/applications/*policytool.desktop
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
%{_mandir}/man1/policytool-%{name}.1*
%{_mandir}/man1/rmic-%{name}.1*
%{_mandir}/man1/schemagen-%{name}.1*
%{_mandir}/man1/serialver-%{name}.1*
%{_mandir}/man1/wsgen-%{name}.1*
%{_mandir}/man1/wsimport-%{name}.1*
%{_mandir}/man1/xjc-%{name}.1*
%ifarch %{jit_arches}
  %if %{with_systemtap}
    %dir %{_jvmdir}/%{sdkdir}/tapset
    %{_jvmdir}/%{sdkdir}/tapset/*
    %dir %{tapsetdir}
    %{tapsetdir}/*.stp
  %endif
%endif

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
%doc test/jtreg-summary.log
%endif

%if %{build_docs}
%files javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/%{name}
%endif


%changelog
* Thu Jun 14 2012 Bernhard Rosenkraenzer <bero@bero.eu> 0:1.6.0.0-26.b24mdv2012.0
+ Revision: 805735
- Update to icedtea6 1.11.3, openjdk b24

* Fri Feb 17 2012 Oden Eriksson <oeriksson@mandriva.com> 0:1.6.0.0-26.b22
+ Revision: 775961
- icedtea6-1.10.6

* Sun Feb 12 2012 Oden Eriksson <oeriksson@mandriva.com> 0:1.6.0.0-25.b22
+ Revision: 773464
- disable rpmlint
- fix rpm5 packaging issues
- rebuild

* Wed Nov 09 2011 Oden Eriksson <oeriksson@mandriva.com> 0:1.6.0.0-24.b22
+ Revision: 729304
- icedtea6-1.10.4

  + Paulo Andrade <pcpa@mandriva.com.br>
    - Convert gcjbootstrap define build option to rpmbuild command line option.

* Sun Oct 02 2011 Oden Eriksson <oeriksson@mandriva.com> 0:1.6.0.0-23.b22
+ Revision: 702448
- duh, was in the midddle of dinner... automake, not aclocal
- some moron removed th deps on aclocal somewhere (rpm-build?)
- attempt to relink against libpng15.so.15

  + Paulo Andrade <pcpa@mandriva.com.br>
    - Provide java-javadoc when not generating documentation
    - Correct check for build_docs macro in wrong scriptlet
    - Customize to build on armv7l with an existing armv5te java-1.6.0-openjdk

* Tue Jul 26 2011 Paulo Andrade <pcpa@mandriva.com.br> 0:1.6.0.0-22.b22
+ Revision: 691677
- Update to icedtea 1.10.3

* Fri Jun 17 2011 Oden Eriksson <oeriksson@mandriva.com> 0:1.6.0.0-21.b22
+ Revision: 685825
- icedtea6 1.10.2

* Thu Jun 16 2011 Oden Eriksson <oeriksson@mandriva.com> 0:1.6.0.0-20.b22
+ Revision: 685495
- use the same release for backports, makes it a lot easier

* Wed Jun 15 2011 Oden Eriksson <oeriksson@mandriva.com> 0:1.6.0.0-19.b22
+ Revision: 685412
- fix deps (for backports/updates)
- corrrect the backport/updates release string

* Wed May 25 2011 Paulo Andrade <pcpa@mandriva.com.br> 0:1.6.0.0-18.b22
+ Revision: 678905
- Update to icedtea 1.10.1 and openjdk b22

* Tue May 24 2011 Paulo Andrade <pcpa@mandriva.com.br> 0:1.6.0.0-17.b20
+ Revision: 678015
- Rework package to rebuild in cooker

* Sun Mar 13 2011 Paulo Andrade <pcpa@mandriva.com.br> 0:1.6.0.0-16.b20
+ Revision: 644445
- Rebuild with systemtap support enabled

  + Funda Wang <fwang@mandriva.org>
    - rebuild to obsolete old packages

* Wed Feb 16 2011 Paulo Andrade <pcpa@mandriva.com.br> 0:1.6.0.0-14.b20
+ Revision: 638056
- Update to openjdk b20 and icedtead 1.9.7
  * Security updates
  - S6878713, CVE-2010-4469: Hotspot backward jsr heap corruption
  - S6907662, CVE-2010-4465: Swing timer-based security manager bypass
  - S6994263, CVE-2010-4472: Untrusted code allowed to replace DSIG/C14N implemntation
  - S6981922, CVE-2010-4448: DNS cache poisoning by untrusted applets
  - S6983554, CVE-2010-4450: Launcher incorrect processing of empty library pathentries
  - S6985453, CVE-2010-4471: Java2D font-related system property leak
  - S6927050, CVE-2010-4470: JAXP untrusted component state manipulation
  - RH677332, CVE-2011-0706: Multiple signers privilege escalation
  * Bug fixes
  - RH676659: Pass -export-dynamic flag to linker using -Wl, as option in gcc 4.6+is broken
  - Fix latent JAXP bug caused by missing import
- Update to icedtea 1.8.6 with security updates:
 * RH672262, CVE-2011-0025: IcedTea jarfile signature verification bypass
 * S4421494, CVE-2010-4476: infinite loop while parsing double literal

* Tue Jan 18 2011 Paulo Andrade <pcpa@mandriva.com.br> 0:1.6.0.0-12.b18
+ Revision: 631635
- * Security updates
  - RH663680, CVE-2010-4351: IcedTea JNLP SecurityManager bypass
  * Backports
  - S6438179, RH569121: XToolkit.isTraySupported() result has nothing to do with the system tray
  - S4356282: RFE: JDK should support OpenType/CFF fonts
  - S6954424, RH525870: Support OpenType/CFF fonts in JDK 7
  - S6795356, PR590: Leak caused by javax.swing.UIDefaults.ProxyLazyValue.acc
  - S6967436, RH597227: lines longer than 2^15 can fill window.
  - S6967433: dashed lines broken when using scaling transforms.
  - S6976265: No STROKE_CONTROL
  - S6967434, PR450, RH530642: Round joins/caps of scaled up lines have poor quality.
  * Fixes:
  - S7003777, RH647674: JTextPane produces incorrect content after parsing the html text

* Wed Nov 24 2010 Paulo Andrade <pcpa@mandriva.com.br> 0:1.6.0.0-11.b18mdv2011.0
+ Revision: 600880
- Update to icedtea 1.8.3

* Fri Oct 29 2010 Paulo Andrade <pcpa@mandriva.com.br> 0:1.6.0.0-10.b18mdv2011.0
+ Revision: 590306
- Correct a memory and a mutex leak
- Update to icedtea 1.8.2

* Thu Oct 14 2010 Oden Eriksson <oeriksson@mandriva.com> 0:1.6.0.0-9.b18mdv2011.0
+ Revision: 585595
- keep it backportable for security updates

* Thu Sep 02 2010 Thierry Vignaud <tv@mandriva.org> 0:1.6.0.0-8.b18mdv2011.0
+ Revision: 575205
- let the doc subpackage be noarch

* Sat Jul 31 2010 Paulo Andrade <pcpa@mandriva.com.br> 0:1.6.0.0-7.b18mdv2011.0
+ Revision: 563827
- Update to icedtea 1.8.1.

* Tue May 18 2010 Paulo Andrade <pcpa@mandriva.com.br> 0:1.6.0.0-6.b18mdv2010.1
+ Revision: 545063
- Don't explicitly link to xulrunner allowing chromium-browser to use openjdk

* Fri May 07 2010 Paulo Andrade <pcpa@mandriva.com.br> 0:1.6.0.0-5.b18mdv2010.1
+ Revision: 543083
+ rebuild (emptylog)

* Mon Apr 26 2010 Oden Eriksson <oeriksson@mandriva.com> 0:1.6.0.0-4.b18mdv2010.1
+ Revision: 538943
- 2009.0 and up does not have xulrunner-devel-unstable
- really prepare for main/testing
- prepare for main/testing

* Tue Apr 20 2010 Paulo Andrade <pcpa@mandriva.com.br> 0:1.6.0.0-3.b18mdv2010.1
+ Revision: 537258
- Correct an off by one misallocation that may cause random behavior

* Fri Apr 16 2010 Oden Eriksson <oeriksson@mandriva.com> 0:1.6.0.0-2.b18mdv2010.1
+ Revision: 535395
- fix backport release as 2010.0 was named java-1.6.0-openjdk-1.6.0.0-0.20.b16.

* Thu Apr 15 2010 Paulo Andrade <pcpa@mandriva.com.br> 0:1.6.0.0-1.b18mdv2010.1
+ Revision: 535169
- Restore generate-fedora-zip.sh to actually match fedora version
- Update to icedtea6-1.8

  + Oden Eriksson <oeriksson@mandriva.com>
    - added backporting magic for updates

* Fri Feb 26 2010 Oden Eriksson <oeriksson@mandriva.com> 0:1.6.0.0-0.20.b17.2mdv2010.1
+ Revision: 511884
- fix borked deps (duh!)
- rebuild

* Tue Feb 09 2010 Paulo Andrade <pcpa@mandriva.com.br> 0:1.6.0.0-0.20.b17.1mdv2010.1
+ Revision: 503395
- Make systemtap support conditional, and default to disabled.
- Update to icedtea 1.7 and openjdk b17

* Mon Feb 01 2010 Funda Wang <fwang@mandriva.org> 0:1.6.0.0-0.20.b16.14mdv2010.1
+ Revision: 498972
- merge mandriva-fontpath patch for CJK fonts, and fedora's own font patch

* Tue Jan 19 2010 Paulo Andrade <pcpa@mandriva.com.br> 0:1.6.0.0-0.20.b16.13mdv2010.1
+ Revision: 493933
- Patch plugin code to work with firefox 3.6.0

  + Oden Eriksson <oeriksson@mandriva.com>
    - fix libxul pkg-config discovery conditionally
    - support libjpeg v8 too (conditionally)
    - rebuilt against libjpeg v8

  + Tomasz Pawel Gajc <tpg@mandriva.org>
    - rebuild for new xulrunner (OJI interface has been obsoleted in xulrunner, NPAPI is standard now)

* Fri Oct 30 2009 Paulo Andrade <pcpa@mandriva.com.br> 0:1.6.0.0-0.20.b16.11mdv2010.1
+ Revision: 460213
- Correct installation of fontconfig.properties file (#55005)

* Tue Oct 27 2009 Frederic Crozat <fcrozat@mandriva.com> 0:1.6.0.0-0.20.b16.10mdv2010.0
+ Revision: 459521
- Force rebuild

  + Paulo Andrade <pcpa@mandriva.com.br>
    - Correct loop at 100%% cpu in ix86 when loading some java plugins in firefox.

* Wed Oct 14 2009 Rafael da Veiga Cabral <cabral@mandriva.com> 0:1.6.0.0-0.20.b16.8mdv2010.0
+ Revision: 457302
- removes Fedora changes required to link with their x11-proto-devel
- add x11-proto-devel-header.patc (changes shmproto.h to XShm.h)
- change version of x11-proto-devel buildrequire
  (7.4 does not holds required headers)
- add x11-proto-devel build require (shmproto.h)
- update hotspot.tar.gz (fedora)
- add java-1.6.0-openjdk-x11.patch
- add new icedtea6-1.6
- removed patches due the new icedtea:
  java-1.6.0-openjdk-netxandplugin.patch
  java-1.6.0-openjdk-securitypatches.patch
  java-1.6.0-openjdk-no-ht-support.patch
  java-1.6.0-openjdk-agent-allfiles.patch
  java-1.6.0-openjdk-link-cpp.patch
  icedtea-ignore-unrecognized-options.patch
  icedtea-sparc-trapsfix.patch
- rebzipping openjdk source without openjdk dir
  (needed to build)
- should solve both #53803 and #53809
- some clean up on spec to keep it fedora like

* Wed Oct 07 2009 Thierry Vignaud <tv@mandriva.org> 0:1.6.0.0-0.20.b16.7mdv2010.0
+ Revision: 455482
- move huge changelog in devel package

* Tue Sep 29 2009 Christophe Fergeau <cfergeau@mandriva.com> 0:1.6.0.0-0.20.b16.6mdv2010.0
+ Revision: 450806
- use more accurate Requires (since we dlopen the lib name)
- add explicit Requires: on libjpeg7 since it's dlopened
- make sure we use libjpeg7 and not libjpeg62

  + Nicolas Lécureuil <nlecureuil@mandriva.com>
    - Rebuild for libjepg7

* Mon Aug 24 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 0:1.6.0.0-0.20.b16.4mdv2010.0
+ Revision: 420218
- rebuild for new xulrunner

* Sat Aug 15 2009 Oden Eriksson <oeriksson@mandriva.com> 0:1.6.0.0-0.20.b16.3mdv2010.0
+ Revision: 416527
- rebuilt against libjpeg v7

* Fri Aug 14 2009 Rafael da Veiga Cabral <cabral@mandriva.com> 0:1.6.0.0-0.20.b16.2mdv2010.0
+ Revision: 416396
- added java-1.6.0-openjdk-netxandplugin.patch and java-1.6.0-openjdk-securitypatches.patch to
  fix security issues: (CVE-2009-0217, CVE-2009-2475, CVE-2009-2476, CVE-2009-2625, CVE-2009-2670,
  CVE-2009-2671, CVE-2009-2673, CVE-2009-2674, CVE-2009-2675, CVE-2009-2689, CVE-2009-2690 and
  CVE-2009-1896)

* Tue Jun 09 2009 Rafael da Veiga Cabral <cabral@mandriva.com> 0:1.6.0.0-0.20.b16.1mdv2010.0
+ Revision: 384362
- Build 16 embeddeds a new 1.18 lcms with security fixes for CVE-2009-0581,
  CVE-2009-0723, CVE-2009-0733 and for CVE-2009-0793, so this release disable
  java-1.6.0-openjdk-lcms.patch
- java-1.6.0-openjdk-securitypatches.patch and java-1.6.0-openjdk-pulsejava.patch
  were merged upstream and a further check was done to make sure fixes were there
- java-1.6.0-openjdk-set-cookie-handling.patch were merged upstream
- added a fixed icedtea-ignore-unrecognized-options.patch
- icedtea-sparc-trapsfix.patch fixes icedtea-sparc-trapsfix.patch
- fix-icedtea-shark-build.patch fixes icedtea-shark-build.patch
- java-1.6.0-openjdk-link-cpp.patch rediffed
- java-1.6.0-openjdk-sparc-fixes.patch rediffed
- openjdk-6-src-b16-24_apr_2009-fedora.tar.gz source code was ripped from
  fc 11 and changed to a bzip2 archive
- According Joe Darcy from SUN the other non security bugs fixed in this build are:
   - 6761791: Crash in the FontManager code due to use of JNIEnv saved by
   another thread
   - 6512707: "incompatible types" after (unrelated) annotation processing
   - 6632696: Writing to closed output files (writeBytes) leaks native memory
   (unix)
   - 6788196: (porting) Bounds checks in io_util.c rely on undefined behaviour
   - 6791458: FileInputStream/RandomAccessFile.read leaks memory if invoked
   on closed stream with len > 8k
   - 6792066: src/share/native/java/io/io_util.c clean-ups
   - 6819886: System.getProperty("os.name") reports Vista on Windows 7
   - 6821031: Upgrade OpenJDK's LittleCMS version to 1.18
   - 6800572: Removing elements from views of NavigableMap implementations
   does not always work correctly.
   - 6801020: Concurrent Semaphore release may cause some require thread not
   signaled
   - 6806019: 38 JCK api/javax_sound/midi/ tests fails starting from jdk7 b46
   - 6803402: Race condition in AbstractQueuedSynchronizer
   - 6793757: Fix formatting of copyright notices in Gervill
   - 6794201: remove unused sources
   - 6808724: UninitializedDisplayModeChangeTest/DisplayModeChanger.java has
   wrong legal notice
   - 6821030: Merge OpenJDK Gervill with upstream sources, Q1CY2009
   - 6823445: Gervill SoftChannel/ResetAllControllers jtreg test fails after
   portamento fix from last merge
   - 6823446: Gervill SoftLowFrequencyOscillator fails when freq is set to 0
   cent or 8.1758 Hz.
   - 6824976: Fix NAWK assignment in shell script
   jdk/make/java/java/genlocales.gmk
   - 6828183: testcase from SSR09_01 into jdk6-open hangs

* Fri May 22 2009 Funda Wang <fwang@mandriva.org> 0:1.6.0.0-0.19.b14.4mdv2010.0
+ Revision: 378633
- use our own CJK fonts path

* Wed Apr 15 2009 Oden Eriksson <oeriksson@mandriva.com> 0:1.6.0.0-0.19.b14.3mdv2009.1
+ Revision: 367368
- rebuild
- make it backport to 2009.0

* Tue Apr 14 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 0:1.6.0.0-0.19.b14.2mdv2009.1
+ Revision: 366854
- Patch105: prevents endlessly waiting for cookies (mdvbz #49908)

* Sun Apr 12 2009 Frederik Himpe <fhimpe@mandriva.org> 0:1.6.0.0-0.19.b14.1mdv2009.1
+ Revision: 366452
- Sync with Fedora's 1.6.0-19.b14:
  * Add patches fixing security vulnerabilities in lcms (CVE-2009-0581,
  CVE-2009-0723, CVE-2009-0733)  and pulseaudio output(CVE-2009-0794)
  * Add OpenJDK patch fixing these security bugs according to Ubuntu
    changelog:
    - 6522586: Enforce limits on Font creation.
    - 6536193: flaw in UTF8XmlOutput.
    - 6610888: Potential use of cleared of incorrect acc in JMX Monitor.
    - 6610896: JMX Monitor handles thread groups incorrectly.
    - 6630639: lightweight HttpServer leaks file descriptors on no-data
      connections.
    - 6632886: Font.createFont can be persuaded to leak temporary files.
    - 6636360: compiler/6595044/Main.java test fails with 64bit java on
      solaris-sparcv9 with SIGSEGV.
    - 6652463: MediaSize constructors allow to redefine the mapping of
      standard MediaSizeName values.
    - 6652929: Font.createFont(int,File) trusts File.getPath.
    - 6656633: getNotificationInfo methods static mutable (findbugs).
    - 6658158: Mutable statics in SAAJ (findbugs).
    - 6658163: txw2.DatatypeWriter.BUILDIN is a mutable static (findbugs).
    - 6691246: Thread context class loader can be set using JMX remote
      ClientNotifForwarded.
    - 6717680: LdapCtx does not close the connection if initialization fails.
    - 6721651: Security problem with out-of-the-box management.
    - 6737315: LDAP serialized data vulnerability.
    - 6792554: Java JAR Pack200 header checks are insufficent.
    - 6804996: JWS PNG Decoding Integer Overflow [V-flrhat2ln8].
    - 6804997: JWS GIF Decoding Heap Corruption [V-r687oxuocp].
    - 6804998: JRE GIF Decoding Heap Corruption [V-y6g5jlm8e1].
  * Update icedtea from hg snapshot to release 1.4.1
  * Update visualvm and netbeans profiler releases
  * Update makefile patch to remove parts integrated upstream
  * Add some archs supported by hotspot
- Extract hotspot tarball by hand, because the configure script would not do
  this because some other sources or patches already created the hotspot
  directory
- Renumber patches and sources to correspond with Fedora's numbering

* Wed Dec 17 2008 David Walluck <walluck@mandriva.org> 0:1.6.0.0-0.18.b14.1mdv2009.1
+ Revision: 315308
- rediff patches
- add hotspot.tar.gz
- b14

* Sat Nov 15 2008 David Walluck <walluck@mandriva.org> 0:1.6.0.0-0.17.b13.1mdv2009.1
+ Revision: 303481
- set pkgversion to include release info
- make visualvm support optional
- spec cleanup
- fix Release
- b13

* Sun Aug 10 2008 David Walluck <walluck@mandriva.org> 0:1.6.0.0-0.16.b11.4mdv2009.0
+ Revision: 270163
- install mozilla plugin into syslibdir

  + Anssi Hannula <anssi@mandriva.org>
    - restore lost cacerts changes (fixes broken cacerts symlink)

* Thu Aug 07 2008 David Walluck <walluck@mandriva.org> 0:1.6.0.0-0.16.b11.1mdv2009.0
+ Revision: 266632
- fix IcedTeaPlugin build requirements
- fix Release
- remove BuildRequires: firefox-devel
- remove openjdk-do-not-redefine-bcopy-bcmp-bzero.patch as it is part of icedtea6 now
- rediff icedtea6-1.2-policytool-desktop.patch
- fix xulrunner-devel-unstable BuildRequires
- update to b11

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild early 2009.0 package (before pixel changes)

  + Per Øyvind Karlsen <peroyvind@mandriva.org>
    - drop P8, static linking can be disabled with STATIC_CXX=false in stead..

  + Nicolas Lécureuil <nlecureuil@mandriva.com>
    - Do no show policytool on KDE menu

  + Anssi Hannula <anssi@mandriva.org>
    - icedtea6 1.2, with openjdk6 b09
    - sync with fedora 1.6.0.0-0.16.b09
    - add do-not-redefine-bcopy-bcmp-bzero.patch and link-cpp2.patch
      (replacing $STATIC_CXX) to fix build issues
    - drop now unneeded -fno-tre-vrp compiler flag
    - drop now unneeded JAVACMD hacks
    - set ALT_COMPILER_PATH="" to avoid calling /usr/bin/gcc explicitely
      (for ccache et al)
    - use rootcerts-java for cacerts file
    - drop jhat.patch, fixed in icedtea6 patchset (also update
      generate-dfsg-zip.sh accordingly and regenerate dfsg archive)

  + Pixel <pixel@mandriva.com>
    - rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas

* Mon May 12 2008 Anssi Hannula <anssi@mandriva.org> 0:1.6.0.0-0.10.b09.2mdv2009.0
+ Revision: 206456
- do not buildrequire mercurial, not used for build
- obsolete java-1.7.0-icedtea for now, as development has shifted to
  this package
- add a comment regarding epoch 0
- own mozilla plugin dir for alternatives
- make the javaws desktop entry a bit better
- call update_menus for -devel package as well
- use macros for menus and icons
- fix missing spaces in postun scripts
- fix postun alternative checks for policy compliance

* Fri May 09 2008 David Walluck <walluck@mandriva.org> 0:1.6.0.0-0.10.b09.1mdv2009.0
+ Revision: 204844
- generate dfsg tarball (with sane permissions)
- don't set vendor on menus
- fix argument list too long
- fix C++ linking
- BuildRequires: zip
- remove BuildRequires: X11-devel
- import java-1.6.0-openjdk


* Mon Apr 28 2008 Lillian Angel <langel@redhat.com> - 1:1.6.0.0-0.10.b09
- Copied javaws.desktop and javaws.png to appropriate place.

* Mon Apr 28 2008 Joshua Sumali <jsumali@redhat.com> - 1:1.6.0.0-0.10.b09
- Added javaws menu entry.
- Resolves: rhbz#443851

* Mon Apr 28 2008 Lillian Angel <langel@redhat.com> - 1:1.6.0.0-0.10.b09
- Updated release.
- Updated icedteasnapshot.
- Added jconsole and policy menu entries.
- Removed all jhat references.
- Resolves: rhbz#435235
- Resolves: rhbz#417501
- Resolves: rhbz#437418
- Resolves: rhbz#443360
- Resolves: rhbz#304031

* Thu Apr 18 2008 Lillian Angel <langel@redhat.com> - 1:1.6.0.0-0.9.b09
- Updated icedteaver.
- Updated icedteasnapshot. 
- Updated openjdkver.
- Updated openjdkdate.
- Updated release.
- Resolves: rhbz#442602
- Resolves: rhbz#442514
- Resolves: rhbz#441437
- Resolves: rhbz#375541

* Thu Apr 17 2008 Lillian Angel <langel@redhat.com> - 1:1.6.0.0-0.9.b08
- Added javaws to /usr/bin.
- Resolves: rhbz#437929

* Mon Apr 08 2008 Lillian Angel <langel@redhat.com> - 1:1.6.0.0-0.8.b08
- Updated sources.
- Updated icedteaver.

* Mon Apr 07 2008 Dennis Gilmore <dennis@ausil.us> - 1:1.6.0.0-0.8.b08
- enable building for all arches using zero where there is not a native port

* Mon Mar 31 2008 Lillian Angel <langel@redhat.com> - 1:1.6.0.0-0.7.b08
- Updated icedteasnapshot. Includes sources needed to build xmlgraphics-commons.
- Updated release.
- Resolves: rhbz#439676

* Fri Mar 28 2008 Lillian Angel <langel@redhat.com> - 1:1.6.0.0-0.6.b08
- Updated icedteasnapshot to fix ppc failure.

* Thu Mar 27 2008 Lillian Angel <langel@redhat.com> - 1:1.6.0.0-0.6.b08
- Removed iconv of THIRD_PARTY_README.

* Thu Mar 27 2008 Lillian Angel <langel@redhat.com> - 1:1.6.0.0-0.6.b08
- Updated icedteasnapshot.
- Updated openjdkver and openjdkdate.
- Removed java-1.6.0-openjdk-trademark.patch.
- Updated generate-fedora-zip.sh.
- Resolves: rhbz#438421

* Thu Mar 20 2008 Lillian Angel <langel@redhat.com> - 1:1.6.0.0-0.5.b06
- Updated icedteasnapshot.
- Updated java-1.6.0-openjdk-optflags.patch.

* Mon Mar 17 2008 Lillian Angel <langel@redhat.com> - 1:1.6.0.0-0.5.b06
- Updated icedteasnapshot.
- Updated Release.
- Added new patch: java-1.6.0-openjdk-optflags.patch
- Resolves: rhbz#437331

* Mon Mar 17 2008 Lillian Angel <langel@redhat.com> - 1:1.6.0.0-0.5.b06
- Added version for freetype-devel requirement.
- Resolves: rhbz#437782

* Fri Mar 14 2008 Lillian Angel <langel@redhat.com> - 1:1.6.0.0-0.4.b06
- Fixed Provides and Obsoletes for all sub-packages. Should have specified
java-1.7.0-icedtea < 1.7.0.0-0.999 instead of 1.7.0-0.999.
- Resolves: rhbz#437492

* Wed Mar 12 2008 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:1.6.0.0-0.4.b06
- Add FIXME about versionless SONAMEs.

* Wed Mar 12 2008 Lillian Angel <langel@redhat.com> - 1:1.6.0.0-0.3.b06
- Updated release.
- Updated mauvedate to 2008-03-11.
- Updated accessmajorver to 1.22.
- Updated accessminorver to 0.

* Tue Mar 11 2008 Lillian Angel <langel@redhat.com> - 1:1.6.0.0-0.2.b06
- Updated snapshot.
- Changed icedteaopt to use --with-openjdk instead of --with-icedtea.

* Tue Mar 11 2008 Lillian Angel <langel@redhat.com> - 1:1.6.0.0-0.2.b06
- Added Provides and Obsoletes for all subpackages. All sub-packages 
replaces java-1.7.0-icedtea.
- Updated Release.
- Changed BuildRequires from java-1.7.0-icedtea to java-1.6.0-openjdk.
- Added TRADEMARK file to docs.

* Tue Mar 11 2008 Lillian Angel <langel@redhat.com> - 1:1.6.0.0-0.2.b06
- Added Provides and Obsoletes. This package replaces java-1.7.0-icedtea.

* Fri Feb 15 2008 Lillian Angel <langel@redhat.com> - 1:1.6.0.0-0.1.b06
- Adapted for java-1.6.0-openjdk.

* Wed Feb 13 2008 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.25.b24
- Added libffi requirement for ppc/64.

* Wed Feb 13 2008 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.25.b24
- Updated icedteaver to 1.6.
- Updated release.

* Mon Feb 11 2008 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.24.b24
- Added libjpeg-6b as a requirement.
- Resolves rhbz#432181

* Mon Jan 28 2008 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.24.b24
- Kill Xvfb after it completes mauve tests.

* Mon Jan 21 2008 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.24.b24
- Remove cgibindir macro.
- Remove icedtearelease.
- Remove binfmt_misc support.
- Remove .snapshot from changelog lines wider than 80 columns.

* Tue Jan 08 2008 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.23.b24.snapshot
- Added xorg-x11-fonts-misc as a build requirement for Mauve.
- Updated mauve_tests.

* Mon Jan 07 2008 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.23.b24.snapshot
- Updated Mauve's build requirements.
- Excluding Mauve tests that try to access the network.
- Added Xvfb functionality to mauve tests to avoid display-related failures.
- Resolves rhbz#427614

* Thu Jan 03 2008 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.23.b24.snapshot
- Added mercurial as a Build Requirement.
- Fixed archbuild/archinstall if-block.

* Thu Jan 03 2008 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.23.b24.snapshot
- Removed BuildRequirement firefox-devel
- Added BuildRequirement gecko-devel
- Resolves rhbz#427350

* Fri Dec 28 2007 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.23.b24.snapshot
- Updated icedtea source.
- Resolves rhbz#426142

* Thu Dec 13 2007 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.23.b24.snapshot
- Updated icedteaver.
- Updated Release.
- Updated buildoutputdir.
- Removed openjdkdate.
- Updated openjdkver.
- Updated openjdkzip and fedorazip.
- Added Requires: jpackage-utils.
- Removed java-1.7.0-makefile.patch.
- Updated patch list.
- Resolves rhbz#411941
- Resolves rhbz#399221
- Resolves rhbz#318621

* Thu Dec  6 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.22.b23
- Clear bootstrap mode on ppc and ppc64.

* Wed Dec  5 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.21.b23
- Update icedteasnapshot.

* Fri Nov 30 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.21.b23
- Update icedteasnapshot.
- Remove ExclusiveArch.
- Assume i386.
- Add support for ppc and ppc64.
- Bootstrap on ppc and ppc64.

* Thu Nov 15 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.20.b23
- Add giflib-devel build requirement.

* Thu Nov 15 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.20.b23
- Add libjpeg-devel and libpng-devel build requirements.

* Thu Nov 15 2007 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.20.b23.snapshot
- Added gcjbootstrap.
- Updated openjdkver and openjdkdate to new b23 release.
- Updated Release.
- Added gcjbootstrap checks in.
- Resolves: rhbz#333721

* Mon Oct 15 2007 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.19.b21.snapshot
- Updated release.

* Fri Oct 12 2007 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.18.b21.snapshot
- Updated release.

* Fri Oct 12 2007 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.17.b21.snapshot
- Added jhat patch back in.

* Thu Oct 11 2007 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.17.b21.snapshot
- Update icedtearelease.
- Update icedteasnapshot.
- Update openjdkver.
- Update openjdkdate.
- Updated genurl.
- Removed unneeded patches.
- Removed gcjbootstrap.
- Removed icedteaopt.
- Removed all gcj related checks.
- Resolves: rhbz#317041 
- Resolves: rhbz#314211 
- Resolves: rhbz#314141 
- Resolves: rhbz#301691

* Mon Oct 1 2007 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.16.b19.snapshot
- Listed mauve_output as a doc file instead of a source.
- Added mauve_tests to the src files as doc.

* Fri Sep 28 2007 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.16.b19.snapshot
- Fixed testing. Output is stored in a file and passes/debug info is not shown.

* Thu Sep 27 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.16.b19
- Apply patch to use system tzdata.
- Require tzdata-java.
- Fix mauve shell fragment.

* Thu Sep 27 2007 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.15.b19.snapshot
- Removed jtreg setup line.

* Wed Sep 26 2007 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.15.b19.snapshot
- Removed jtreg.  Does not adhere to Fedora guidelines.

* Tue Sep 25 2007 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.15.b19.snapshot
- Fixed running of Xvfb so it does not terminate after a successful
  test.
- Fixed mauve and jtreg test runs to not break the build when an error
  is thrown

* Mon Sep 24 2007 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.15.b19.snapshot
- Added JTreg zip as source
- Run JTreg tests after build for smoke testing.
- Added Xvfb as build requirement.

* Wed Sep 12 2007 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.15.b19.snapshot
- Added Mauve tarball as source.
- Added mauve_tests as source.
- Run Mauve after build for regression testing.

* Thu Sep  7 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.15.b18
- Do not require openssl for build.
- Require openssl.
- Set gcjbootstrap to 0.
- Remove generate-cacerts.pl.
- Update icedtearelease.
- Update icedteasnapshot.
- Update openjdkver.
- Update openjdkdate.

* Wed Sep  5 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.15.b18
- Rename javadoc master alternative javadocdir.
- Resolves: rhbz#269901

* Wed Sep  5 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.15.b18
- Remove epoch in plugin provides.
- Bump release number.
- Resolves: rhbz#274001

* Mon Aug 27 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.14.b18
- Include idlj man page in files list.

* Mon Aug 27 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.14.b18
- Add documentation for plugin and src subpackages.
- Fix plugin alternative on x86_64.
- Add java-1.7.0-icedtea-win32.patch.
- Rename modzip.sh generate-fedora-zip.sh.
- Keep patches in main directory.
- Namespace patches.
- Add java-1.7.0-icedtea-win32.patch, README.plugin and README.src.
- Bump release number.

* Mon Aug 27 2007 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.13.b18.snapshot
- Added line to run modzip.sh to remove specific files from the openjdk zip.
- Defined new openjdk zip created by modzip.sh as newopenjdkzip.
- Added line to patch the IcedTea Makefile. No need to download openjdk zip.
- Updated genurl.
- Updated icedteasnapshot.

* Fri Aug 24 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.13.b18
- Remove RMI CGI script and subpackage.
- Fix Java Access Bridge for GNOME URL.

* Thu Aug 23 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.12.b18
- Fully qualify Java Access Bridge for GNOME and generate-cacerts
  source paths.
- Fix plugin post alternatives invocation.
- Include IcedTea documentation.
- Update icedteasnapshot.

* Tue Aug 21 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.11.b18
- Revert change to configure macro.

* Mon Aug 20 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.11.b18
- Fix rpmlint errors.

* Mon Aug 20 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.11.b18
- Add missing development alternatives.
- Bump accessver to 1.19.2.
- Bump icedteaver.
- Set icedteasnapshot.
- Define icedtearelease.
- Bump openjdkver.
- Bump openjdkdate.
- Bump release number.
- Add plugin build requirements and subpackage.

* Tue Jul 31 2007 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.10.b16.1.2
- Bump icedteaver.
- Updated icedteasnapshot.
- Updated release to include icedteaver.

* Wed Jul 25 2007 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.9.b16
- Updated icedteasnapshot.
- Bump openjdkver.
- Bump openjdkdate.
- Bump release number.

* Wed Jul 18 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.8.b15
- Only build rmi subpackage on non-x86_64 architectures.

* Wed Jul 18 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.8.b15
- Bump icedteaver.
- Update icedteasnapshot.

* Fri Jul 13 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.8.b15
- Add rmi subpackage.
- Remove name-version javadoc directory.

* Fri Jul 13 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.8.b15
- Set man extension to .gz in base and devel post sections.

* Thu Jul 12 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.7.b15
- Clear icedteasnapshot.
- Bump release number.

* Wed Jul 11 2007 Lillian Angel <langel@redhat.com> - 1.7.0.0-0.6.b15
- Updated icedteasnapshot.
- Bump openjdkver.
- Bump openjdkdate.
- Bump release number.

* Thu Jul  5 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.5.b14
- Define icedteasnapshot.

* Wed Jul  4 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.4.b14
- Prevent jar repacking.

* Wed Jul  4 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.4.b14
- Include generate-cacerts.pl.
- Generate and install cacerts file.

* Tue Jul  3 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.4.b14
- Add javadoc subpackage.
- Add Java Access Bridge for GNOME.
- Add support for executable JAR files.
- Bump alternatives priority to 17000.

* Thu Jun 28 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.4.b14
- Add support for executable jar files.
- Bump icedteaver.
- Bump openjdkver.
- Bump openjdkdate.
- Bump release number.

* Tue Jun 19 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.3.b13
- Import IcedTea 1.1.
- Bump icedteaver.
- Bump openjdkver.
- Bump openjdkdate.
- Bump release number.
- Use --with-openjdk-src-zip.

* Tue Jun 12 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.7.0.0-0.2.b12
- Initial build.
