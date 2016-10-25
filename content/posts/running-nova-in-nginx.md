Title: Running OpenStack Compute APIs in nginx and uWSGI
Date: 2016-10-25 10:00
Category: OpenStack

In this article I will explain how run the [OpenStack Compute
(nova)](https://www.openstack.org/software/releases/liberty/components/nova)
APis behind [nginx](http://nginx.org/), instead of using the
[Eventlet](http://eventlet.net/doc/modules/wsgi.html) builtin WSGI server. This
is a setup we have been using at [IFCA](https://grid.ifca.es/) since long after
using plain Eventlet and [Apache](https://apache.org/) +
[mod_wsgi](https://modwsgi.readthedocs.io/).

Unlike other HTTP servers like Apache, nginx does not have direct WSGI support.
However, it can act as an application gateway, as it offers a number of
built-in interfaces to pass the incoming requests to other HTTP servers,
lightweight application servers and web frameworks. One of those is uWSGI, and
that is what we are going to use to actually run the OpenStack APIs.
[uWSGI](https://uwsgi-docs.readthedocs.org) is one of the most common
application servers implementing the WSGI protocol (but not only) and, as you
probably already know, the OpenStack Compute APIs are WSGI applications

This basic setup will run uWSGI and nginx in the same server, but you can
easily decouple them so that you can deploy several API nodes and use all the
advanced HTTP features of nginx (such as load balancing or SSL termination),
thus horizontally scaling your controller quite easily.

### Preparation

I assume that you have the OpenStack Compute APIs already configured and
running on a server, so lets focus on installing the required extra packages:

    :::bash
    apt-get install nginx
    apt-get install uwsgi-core uwsgi-emperor

Since we are going to run the API using uWSGI, we must stop (and disable) the
`nova-api` service:

	:::bash
	service nova-api stop
	echo manual > /etc/init/SERVICE.override

### Configure uWSGI

As we said, the nova APIs are WSGI applications, but we need some helper
scripts that can be handled by uWSGI. Let's create the
`/usr/lib/cgi-bin/nova-uwsgi/nova.wsgi` file with the following contents:

    :::python
	import os

	import eventlet
	from paste import deploy

	from oslo_config import cfg
	from oslo_log import log as logging

	from nova import config
	from nova import objects
	from nova import service
	from nova import utils

	#eventlet.monkey_patch()

	CONF = cfg.CONF

	config.parse_args([])
	logging.setup(CONF, "nova")
	utils.monkey_patch()
	objects.register_all()

	name = os.path.basename(__file__).rsplit(".", 1)[0]
	paste_conf = "/etc/nova/api-paste.ini"

	options = deploy.appconfig('config:%s' % paste_conf, name=name)
	application = deploy.loadapp('config:%s' % paste_conf, name=name)

Now create a links for the API, so that uWSGI is able to find it:

	:::bash
	ln -sf /usr/lib/cgi-bin/nova-uwsgi/nova.wsgi /usr/lib/cgi-bin/nova-uwsgi/osapi_compute.py

The above script can be executed by a standalone uWSGI instance as follows:

	:::bash
	uwsgi --http-socket :8080 --plugin python --chdir /usr/lib/cgi-bin/nova-uwsgi --module osapi_compute --master --processes 1

If you point to the `http://<server>:8080` URL you should see the nova endpoint
advertising its API versions. Don't forget to stop this process whenever you're
done testing it.

However, the above is not appropriate for a production environment. uWSGI
implements a more convenient module, called "Emperor", where a special uWSGI
instance will control several application instances (called vassals) according
to some specific events (like sudden application termination).  Therefore, we
will rely on the uWSGI emperor mode for spawning all our configured
applications (that is, the different OpenStack Compute APIs) instead of
running them manually.

Lets configure the Emperor. First of all, configure the Emperor itself via its
`/etc/wsgi/emperor.ini`

	:::ini
	[uwsgi]

	# try to autoload appropriate plugin if "unknown" option has been specified
	autoload = true

	# enable master process manager
	master = true

	# spawn 2 uWSGI emperor worker processes
	workers = 2

	# automatically kill workers on master's death
	no-orphans = true

	# place timestamps into log
	log-date = true

	# user identifier of uWSGI processes
	uid = www-data

	# group identifier of uWSGI processes
	gid = www-data

	# vassals directory
	emperor = /etc/uwsgi-emperor/vassals

	# let the emperor change uids and gids
	emperor-tyrant = true

	cap = setgid,setuid

And now configure it as a vassals in `/etc/uwsgi-emperor/vassals/nova.ini`:

		:::ini
		[uwsgi]
		plugin = python
		chdir = /usr/lib/cgi-bin/nova-uwsgi
		module = osapi_compute
		master = true
		processes = 25
		socket = /var/run/nova/nova.uwsgi.sock
		stats = /var/run/nova/nova.uwsgi.stats.sock
		vacuum = true

Now, you can restart it and check that it is working.

### Configure nginx

Now it is time to configure nginx to distribute the requests to the relevant
uWSGI processes. This is the usual nginx configuration for load balancing, so
if you are familiar with nginx configuration you should be familiar with this
configuration. Create a file called `/etc/nginx/sites-enabled/nova.conf` with
the following contents. This setup uses SSL and you should use it too!

	upstream nova {
		server unix:///var/run/nova/nova.uwsgi.sock;
	}

	server {
		listen 8774;
		server_name  controller.example.org;

		root html;
		index index.html index.htm;

		ssl on;
		ssl_certificate /etc/ssl/certs/hostcert.pem;
		ssl_certificate_key /etc/ssl/private/hostkey.pem;

		ssl_session_timeout 5m;

		ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
		ssl_ciphers "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!3DES:!MD5:!PSK";
		ssl_prefer_server_ciphers on;

		location / {
			uwsgi_pass  nova;
			uwsgi_param SCRIPT_NAME "";
			include     /etc/nginx/uwsgi_params;
		}
	}

Restart your services, and you should be done.


### Extra: OpenStack OCCI Interface

If by change you are running an [OCCI](http://occi-wg.org/) interface (or you
want to run it) you can also deploy it using this setup. Assuming that you are
using [ooi](https://launchpad.net/ooi/) the setup will be quite
straightforward.

First, create the required link as follows:

    :::bash
	ln -sf /usr/lib/cgi-bin/nova-uwsgi/nova.wsgi /usr/lib/cgi-bin/nova-uwsgi/ooi_api.py

Now we can create another uWSGI vassal for ooi. Put the following contents in a
file called `/etc/uwsgi-emperor/vassals/ooi.ini`:

	:::ini
	[uwsgi]
	plugin = python
	chdir = /usr/lib/cgi-bin/nova-uwsgi
	module = ooi_api
	master = true
	processes = 4
	socket = /var/run/nova/ooi.uwsgi.sock
	stats = /var/run/nova/ooi.uwsgi.stats.sock
	vacuum = true

Then, add the following nginx configuration:

	:::
	upstream ooi {
		server unix:///var/run/nova/ooi.uwsgi.sock;
	}

	server {
		listen 8787;
		server_name  cloud.ifca.es;

		root html;
		index index.html index.htm;

		ssl on;
		ssl_certificate /etc/ssl/certs/hostcert.pem;
		ssl_certificate_key /etc/ssl/private/hostkey.pem;

		ssl_session_timeout 5m;

		ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
		ssl_ciphers "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!3DES:!MD5:!PSK";
		ssl_prefer_server_ciphers on;

		location / {
			uwsgi_pass ooi;
			uwsgi_param SCRIPT_NAME "";
			include     /etc/nginx/uwsgi_params;
		}
	}
