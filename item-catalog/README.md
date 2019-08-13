# Item Catalog Project

We will develop an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

We will be creating this project essentially from scratch, no templates have been provided. 

The project implements:
- Proper authentication and authorisation.
-  Full CRUD support using SQLAlchemy and Flask.
- JSON endpoints.
- oAuth (using Google Sign-in API).

## Steps to run this project
1) Download and install Vagrant
2) Download and install VirtualBox
3) Clone or download the Vagrant VM configuration file from the folder you are in.
4) Open the above directory and *cd* to the vagrant/ directory. Here, open the terminal, and type
	- *vagrant up* (to download the Ubuntu operating system and install it)
	- *vagrant ssh*
	- *cd /vagrant/* (here you can download or clone this repository, and *cd* into it)
5) Install/Upgrade Flask with *sudo python -m pip install --upgrade flask*
6) Set up the database by typing:
*python catalog_db.py*
*python lotsofcategories.py*

7) Run the application:
*python app.py*
8) Open http://localhost:8000/ in your Web browser
