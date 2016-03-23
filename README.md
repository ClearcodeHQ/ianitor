[![Build Status](https://travis-ci.org/ClearcodeHQ/ianitor.svg?branch=master)](https://travis-ci.org/ClearcodeHQ/ianitor)
[![Coverage Status](https://img.shields.io/coveralls/ClearcodeHQ/ianitor.svg)](https://coveralls.io/r/ClearcodeHQ/ianitor)

# ianitor

**ianitor** is a doorkeeper for your services discovered using
[consul](https://www.consul.io/). It can automatically register new services
through consul API and manage TTL health checks.
 
It provides simple shell command that wraps process and can be simply used in
your existing process/service supervision tool like 
[supervisord](http://supervisord.org/), 
[circus](http://circus.readthedocs.org/en/0.11.1/),
[runit](http://smarden.org/runit/) etc.

## Consul/Python versions compatibility

**ianitor** is compatibile with Python 2.7, 3.3, 3.4, and 3.5 versions.
It is also tested against each latest patch version of every major/minor consul
release starting from 0.4.1 version.

For details of our test matrix see `travis.yml` file.

## Installation and usage

Simply install with pip:

    $ pip install ianitor
    
And you're ready to go with:

    $ ianitor appname -- ./yourapp --some-switch
    
You can check if service is registered diggin' into consul DNS service:

```console
$ dig @localhost -p 8600 appname.service.consul
; <<>> DiG 9.9.3-P1 <<>> @localhost -p 8600 appname.service.consul
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 25966
;; flags: qr aa rd; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0
;; WARNING: recursion requested but not available

;; QUESTION SECTION:
;appname.service.consul.		IN	A

;; ANSWER SECTION:
appname.service.consul.	0	IN	A	10.54.54.214

;; Query time: 44 msec
;; SERVER: 127.0.0.1#8600(127.0.0.1)
;; WHEN: Tue Oct 28 13:53:09 CET 2014
;; MSG SIZE  rcvd: 78
```

Full usage:

    usage: ianitor [-h] [--consul-agent hostname[:port]] [--ttl seconds]
                   [--heartbeat seconds] [--tags tag] [--id ID] [--port PORT] [-v]
                   service-name -- command [arguments]
    
    Doorkeeper for consul discovered services.
    
    positional arguments:
      service-name                    service name in consul cluster
    
    optional arguments:
      -h, --help                      show this help message and exit
      --consul-agent=hostname[:port]  set consul agent address
      --ttl=seconds                   set TTL of service in consul cluster
      --heartbeat=seconds             set process poll heartbeat (defaults to
                                      ttl/10)
      --tags=tag                      set service tags in consul cluster (can be
                                      used multiple times)
      --id=ID                         set service id - must be node unique
                                      (defaults to service name)
      --port=PORT                     set service port
      -v, --verbose                   enable logging to stdout (use multiple times
                                      to increase verbosity)


## How does ianitor work?

ianitor spawns process using python's `subprocess.Popen()` with command line
specified after `--` . It redirects its own stdin to child's stdin and
childs stdout/stderr to his own stdout/stderr.

This way ianitor does not interfere with logging of managed service if it
logs to stdout. Moreover ianitor does not log anything to make it easier to
plug it in your existing process supervision tool.

ianitor handles service registration in consul agent as well as keeping
registered service entry in consul in "healthy" state by continously requesting
it's [TTL health check endpoint](http://www.consul.io/docs/agent/checks.html).

## Example supervisord config

Assuming that you have some service under supervisord supervision:

```ini
[program:rabbitmq]
command=/usr/sbin/rabbitmq-server
priority=0

autostart=true
```

Simply wrap it with ianitor call:

```ini
[program:rabbitmq]
command=/usr/local/bin/ianitor rabbitmq -- /usr/sbin/rabbitmq-server
priority=0

autostart=true
```

## Licence

`ianitor`  is licensed under LGPL license, version 3.


## Contributing and reporting bugs

Source code is available at:
[ClearcodeHQ/ianitor](https://github.com/ClearcodeHQ/ianitor). Issue tracker
is located at [GitHub Issues](https://github.com/ClearcodeHQ/ianitor/issues).
Projects [PyPi page](https://pypi.python.org/pypi/ianitor).
