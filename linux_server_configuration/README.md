# Linux Server Configuration

In this project we will take a baseline installation of a Linux server and prepare it to host our web applications . We will secure our server from a number of attack vectors, install and configure a database server, and deploy one of our existing web applications (item-catalog application from the same Nanodegree program) onto it.

You can visit http://52.29.19.147.xip.io/ for the web-app deployed.

Public IP address: 52.29.19.147
SSH port: 2200


## Get your server

1. Create an AWS account
2. Click Create instance button on the home page of Amazon Lightsail
3. Select Linux/Unix platform
4. Select OS Only and Ubuntu as blueprint
5. Select an instance plan
6. Name your instance
7. Click Create button

## Connect to the server

1. Download private key from the Account section on Amazon Lightsail (pem file)
2. SSH into the instance: $ ssh -i ~/.ssh/path_to_pem_file ubuntu@52.29.19.147

## Update currently installed packages

1. Run *sudo apt-get update* to update packages
2. Run *sudo apt-get upgrade* to install newest versions of packages
3. Set for future updates: *sudo apt-get dist-upgrade*

## Change SSH port from 22 to 2200

1. Run *sudo nano /etc/ssh/sshd_config* to open up the configuration file
2. Change the port number from 22 to 2200 in this file
3. Save and exit the file
4. Restart SSH: *sudo service ssh restart*

## Firewall configuration

1. Set firewall to deny all incomings: *sudo ufw default deny incoming*
2. Set firewall to allow all outgoings: *sudo ufw default allow outgoing*
3. Allow incoming TCP packets on port 2200 (SSH): *sudo ufw allow 2200/tcp*
4. Allow incoming TCP packets on port 80 (HTTP): *sudo ufw allow www*
5. Allow incoming UDP packets on port 123 (NTP): *sudo ufw allow 123/udp*
6. Close port 22: *sudo ufw deny 22*
7. Enable firewall: *sudo ufw enable*
8. Update the firewall configuration on Amazon Lightsail website under Networking. 
	* Delete default SSH port 22 
	* Add custom port 80
	* Add custom port 123
	* Add custom port 2200
9. Now you can ssh in using the new port 2200: *ssh -i path_to_pem_file ubuntu@52.29.19.147 -p 2200*

## Grader account with sudo access

1. Create account grader: *sudo adduser grader*
2. *sudo nano /etc/sudoers* and add *grader ALL=(ALL:ALL) ALL* under the root user line.
3. Save and exit

## Grader ssh

1. Create an SSH key pair for grader using the ssh-keygen tool on your local machine - *ssh-keygen -t rsa*
2. Save it in ~/.ssh path
3. Deploy public key on development environment:
	- Read the public key on the local machine *cat ~/.ssh/FILE-NAME.pub*
	- On your virtual machine
   		* under /home/grader/ -> *mkdir .ssh*
   		* *sudo nano .ssh/authorized_keys* and copy the public key, then save the file
		* To change file permission, run:
			a. *sudo chown grader:grader .ssh* 
			b. *sudo chmod 700 .ssh*
			c. *sudo chmod 644 .ssh/authorized_keys*
4. Restart SSH: *sudo service ssh restart*
5. Login in as grader: *ssh -i ~/.ssh/grader_key grader@52.29.19.147 -p 2200
6. To unable grader password, open the configuration file with *sudo nano /etc/ssh/sshd_config* and change PasswordAuthentication yes to no. Then restart SSH with *sudo service ssh restart*

## UTC time zone

1. *sudo dpkg-reconfigure tzdata
2. Choose None of the above and set timezone to UTC

## Apache configuration

1. Install Apache *sudo apt-get install apache2*
2. Go to http://52.29.19.147/ to see Apache2 Ubuntu Default Page

## Python mod_wsgi

1. Install the mod_wsgi package for python3 *sudo apt-get install libapache2-mod-wsgi-py3 python3-dev*
2. Enable mod_wsgi: *sudo a2enmod wsgi*
3. Restart Apache: *sudo service apache2 restart*

## PostgreSQL

1. Run *sudo apt-get install postgresql*
2. Do not allow remote connections. Find the remote connection permission in the file *sudo cat /etc/postgresql/9.5/main/pg_hba.conf*

## PostgreSQL user - catalog

1. *sudo su - postgres*
2. Connect to PostgreSQL *psql*
3. Create user catalog with LOGIN role: *CREATE ROLE catalog WITH PASSWORD 'password';*
4. Allow user to create database tables: # ALTER USER catalog CREATEDB;
5. Create database: # CREATE DATABASE catalog WITH OWNER catalog;
6. Connect to database catalog: # \c catalog
7. Revoke all the rights: # REVOKE ALL ON SCHEMA public FROM public;
8. Grant access to catalog: # GRANT ALL ON SCHEMA public TO catalog;
9. Exit psql: \q 
10. Exit user postgres: exit

## Linux user catalog 

1. *sudo adduser catalog*
2. Give catalog user sudo access *sudo nano /etc/sudoers* by adding the line *catalog ALL=(ALL:ALL) ALL* under the line *root ALL=(ALL:ALL) ALL*
3. Save and exit the file

## Install git and clone the application 
1. *sudo apt-get install git*
2. Make the folder  for the application *sudo mkdir /var/www/item_catalog/
3. CD to this directory  *cd /var/www/item_catalog/*
4. Clone the catalog app *sudo git clone FlaskApp-URL*
5. Change the ownership *sudo chown -R ubuntu:ubuntu item_catalog/*
6. CD to /var/www/item_catalog/FlaskApp
7. Change file app.py to __init__.py: *sudo mv app.py __init__.py*
8. Change line app.run(host='0.0.0.0', port=8000, threaded=False) to app.run() in init.py file
9. In the __init__.py file edit: 
	* the paths to client_secrets.json with absolute path "/var/www/item_catalog/FlaskApp/client_secrets.json"
	* the import *from catalog_db import XXX* to *from FlaskApp.catalog_db import XXX*
10. Replace lines in __init__.py, catalog_db.py, and lotsofitems.py with:
*engine = create_engine('postgresql://catalog:password@localhost/catalog')*


## Setup for deploying 

Install packages:
   *sudo pip3 install httplib2*
   *sudo pip3 install requests*
   *sudo pip3 install --upgrade oauth2client*
   *sudo pip3 install sqlalchemy*
   *sudo pip3 install flask*
   *sudo apt-get install libpq-dev*
   *sudo pip3 install psycopg2*


## Setup the virtual host

1. Create the file catalog.conf *sudo nano /etc/apache2/sites-available/catalog.conf*

```
<virtualHost *:80>
    ServerName 'XXX.XXX.XXX.XXX'
    ServerAdmin XXXX@gmail.com
    WSGIScriptAlias / /var/www/item_catalog/catalog.wsgi
    <Directory /var/www/item_catalog/FlaskApp>
        Order allow,deny
        Allow from all
    </Directory>
    Alias /static /var/www/item_catalog/FlaskApp/static
    <Directory /var/www/item_catalog/FlaskApp/static/>
        Order allow,deny
        Allow from all
    </Directory>
    ErrorLog /home/grader/serverErrors/serverError.log
    LogLevel warn
    CustomLog /home/grader/serverErrors/access.log combined
</VirtualHost>
```

2. Run *sudo a2ensite catalog.conf* to enable the virtual host
3. *sudo service apache2 reload*



## Configure .wsgi file

1. *cd /var/www/item_catalog/*
2. *sudo nano catalog.wsgi*
3. Add the following lines of code to the .wsgi file

```
#!/usr/bin/python

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/item_catalog")

from FlaskApp import app as application
application.secret_key = 'super_secret_key'
```
4. Restart Apache: $ sudo service apache2 reload

## Final setup

1. Run *sudo python3 catalog_db.py*
2. Run *sudo python3 lotsofitems.py*
3. Restart Apache: *sudo service apache2 reload*
4. Go to http://52.29.19.147/ to see the application runing online
5. go to console.developers.google.com and under your app credential section add http://52.29.19.147.xip.io/ to the authorized origins
6. Go to http://52.29.19.147.xip.io and the application should run fine (together with login)

## References

1. [Digital Ocean - Deploy A Flask App on ubuntu Server](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)
2. [AWS documentation](https://docs.aws.amazon.com/index.html)
3. [Medium](https://medium.com/@manivannan_data/how-to-deploy-the-flask-app-as-ubuntu-service-399c0adf3606)
4. [Ubuntu Forums](https://ubuntuforums.org/)
