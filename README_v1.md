## Installing

The easiest way to install all the dependencies is to run:

``` bash
python -m pip install -r requirements.txt
```

### Linux

On Debian/Ubuntu run:

``` console
sudo apt install libssl-dev python3-dev
```

On Alpine Linux run:

``` console
sudo apk add openssl-dev python3-dev bsd-compat-headers libffi-dev
```

### Windows

On Windows the easiest way to install OpenSSL is to use
[Chocolatey](https://chocolatey.org/).

``` console
choco install openssl
```

or use [Scoop](https://scoop.sh/)

``` console
scoop install main/openssl
```

You will need to set some environment variables to link against OpenSSL:

``` console
$Env:INCLUDE = "C:\Progra~1\OpenSSL\include"
$Env:LIB = "C:\Progra~1\OpenSSL\lib"
```
