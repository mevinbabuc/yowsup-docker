<<<<<<< HEAD
[yowsup](https://github.com/tgalal/yowsup) is a python library that implements WhatsApp's protocol. Through this docker image you are able to access yowsup's command line client and run different commands such as sending messages, creating groups, updating profile and many other things.

#Installation

```docker pull tgalal/yowsup```

#usage

Add ```--debug``` to any of the commands to get an insight on the actual protocol and see all incoming and outgoing data in your console.

yowsup will need access to a persistent storage to store generated keys data inside, used at registration and for login with e2e encryption enabled to work. Therefore you'll need to mount a host dir at /root/.yowsup in each docker run command.

##Registration

### Step 1 request code
```
docker run -v SOMEDIR:/root/.yowsup tgalal/yowsup registration --cc COUNTRYCODE --phone NUMBER --requestcode sms
```

or

```
docker run -v SOMEDIR:/root/.yowsup tgalal/yowsup registration --cc COUNTRYCODE --phone NUMBER --requestcode voice
```

note that the phone number must also begin with the specified country code

### Step 2 verify code

```
docker run -v SOMEDIR:/root/.yowsup tgalal/yowsup registration --cc COUNTRYCODE --phone NUMBER --register CODE
```

Save the returned password as you will need it for login

##Clients
### Command line client
	
```
docker run -v SOMEDIR:/root/.yowsup -it tgalal/yowsup demos --login PHONE:PASSWORD --yowsup
```

This will start yowsup shell, type /L to login

```
Yowsup Cli client
==================
Type /help for available commands

\[offline]: /L
```

### Echo client

This echoes back all received messages

```
docker run -v SOMEDIR:/root/.yowsup tgalal/yowsup demos --login PHONE:PASSWORD --echo
```

### One shot client

Login, send a message, exit


```
docker run -v SOMEDIR:/root/.yowsup tgalal/yowsup demos --login PHONE:PASSWORD --send CONTACT_PHONE MESSAGE
```

## E2E encryption
To use e2e encryption in any of the clients, pass --moxie in any of the commands. For example:

```
docker run -v SOMEDIR:/root/.yowsup -it tgalal/yowsup demos --login PHONE:PASSWORD --yowsup --moxie
```
=======
# Yowsup 2 [![Build Status](https://travis-ci.org/tgalal/yowsup.svg?branch=master)](https://travis-ci.org/tgalal/yowsup) [![Join the chat at https://gitter.im/tgalal/yowsup](https://badges.gitter.im/tgalal/yowsup.svg)](https://gitter.im/tgalal/yowsup?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

<a href="https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=Z9KKEUVYEY6BN" target="_blank"><img src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" /></a>

## Updates (December 14, 2015)
Yowsup v2.4.48 is out, See [release notes](https://github.com/tgalal/yowsup/releases/tag/v2.4.48)

==========================================================

## Yowsup opened WhatsApp service under platforms!

Yowsup is a python library that enables you build application which use WhatsApp service. Yowsup has been used to create an unofficial WhatsApp client Nokia N9 through the Wazapp project which was in use by 200K + users as well as another fully featured unofficial client for Blackberry 10

## Quickstart

 * **[yowsup's architecture](https://github.com/tgalal/yowsup/wiki/Architecture)**
 * **[Create a sample app](https://github.com/tgalal/yowsup/wiki/Sample-Application)**
 * **[yowsup-cli](https://github.com/tgalal/yowsup/wiki/yowsup-cli-2.0)**
 * **[Yowsup development, debugging, maintainance and sanity](https://github.com/tgalal/yowsup/wiki/Yowsup-development,-debugging,-maintainance-and-sanity)**

## Installation

 - Requires python2.6+, or python3.0 +
 - Required python packages: python-dateutil,
 - Required python packages for end-to-end encryption: protobuf, pycrypto, python-axolotl-curve25519
 - Required python packages for yowsup-cli: argparse, readline (or pyreadline for windows), pillow (for sending images)

Install using setup.py to pull all python dependencies, or using pip:

```
pip install yowsup2
```

### Linux

You need to have installed python headers (from probably python-dev package) and ncurses-dev, then run
```
python setup.py install
```
Because of a bug with python-dateutil package you might get permission error for some dateutil file called requires.txt when you use yowsup (see [this bug report](https://bugs.launchpad.net/dateutil/+bug/1243202)) to fix you'll need to chmod 644 that file.

### FreeBSD (*BSD)
You need to have installed: py27-pip-7.1.2(+), py27-sqlite3-2.7.11_7(+), then run
```
pip install yowsup2
```

### Mac
```
python setup.py install
```
Administrators privileges might be required, if so then run with 'sudo'

### Windows

 - Install [mingw](http://www.mingw.org/) compiler
 - Add mingw to your PATH
 - In PYTHONPATH\Lib\distutils create a file called distutils.cfg and add these lines:

```
[build]
compiler=mingw32
```
 - Install gcc: ```mingw-get.exe install gcc```
 - Install [zlib](http://www.zlib.net/)
 - ```python setup.py install```

If pycrypto fails to install with some "chmod error". You can install it separately using something like
```easy_install http://www.voidspace.org.uk/downloads/pycrypto26/pycrypto-2.6.win32-py2.7.exe```

or for python3 from:

 > [https://github.com/axper/python3-pycrypto-windows-installer](https://github.com/axper/python3-pycrypto-windows-installer)

and then rerun the install command again

# Special thanks

Special thanks to:

- [CODeRUS](https://github.com/CODeRUS)
- [mgp25](https://github.com/mgp25)
- [SikiFn](https://github.com/SikiFn)
- [0xTryCatch](https://github.com/0xTryCatch)
- [shirioko](https://github.com/shirioko)

and everyone else on the [WhatsAPI](https://github.com/mgp25/WhatsAPI-Official) project for their contributions to yowsup and the amazing effort they put into WhatsAPI, the PHP WhatsApp library

Special thanks goes to all other people who use and contribute to the library as well.

Please **[read this](https://github.com/tgalal/yowsup/wiki/Yowsup-development,-debugging,-maintainance-and-sanity)** if you'd like to contribute to yowsup 2.0

Thanks!


# License:

As of January 1, 2015 yowsup is licensed under the GPLv3+: http://www.gnu.org/licenses/gpl-3.0.html.
>>>>>>> 6ea1319ec897f60962c66e0391f9eeccb4e7ab70
