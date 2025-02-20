# Quic Botnet Project

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

## Usage

First run python .\remote_shell.py and press "h" to get the help menu.
Press "l" to get the list of configured bots.

### Running in local environment
Please run the commands below in different terminals:
```
python .\remote_shell.py
python .\coordination.py
python bot.py -name bot2 -addr 127.0.0.1 -timeout 3600 -localhost true
```

### Running in a network of Docker containers
`docker-compose build` (may take a few minutes the first time)  
`docker-compose up -d`
Enter attacker's terminal and run:

`./remote_shell.py -cord_addr 10.0.3.5`

### Running in a real network
Please create the necessary ssl certificates and place them inside cert folder.
Use `python .\remote_shell.py --help` to find what you need to place as arguments.