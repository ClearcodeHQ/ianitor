[![WTFPL](http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-4.png)](http://www.wtfpl.net/)

# ianitor

**ianitor** is a doorkeeper for your services discovered using
[consul](https://www.consul.io/). It can automatically register new services
through consul API and manage TTL health checks.
 
It provides simple shell command that wraps process and can be simply used in
your existing process/service supervision tool like 
[supervisord](http://supervisord.org/), 
[circus](http://circus.readthedocs.org/en/0.11.1/),
[runit](http://smarden.org/runit/) etc.


## Installation and usage

Simply install with pip:

    pip install ianitor
    
And you're ready to go with:

    ianitor - yourapp --some-switch
    
## Licence

This code is under [WTFPL](https://en.wikipedia.org/wiki/WTFPL).
Just do what the fuck you want with it.