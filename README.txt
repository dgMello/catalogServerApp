Catalog Application
Description
This python progam creates a web application called Catalog Applicatoin.  This application contains a database of categories and the items in them.

Users can choose to browse the catalog without logging in, but will be unable add, edit or delete items.  Users can login using Google or Facebook.

Installing & Running
Step 1. Use the command line to start up and and log into the Vagrant VM and navigate to the catalog directory.

$ vagrant up
$ vagrant ssh
$ cd /vagrant/catalog

Step 2. Use the catagoryCreator.py file to setup the categories. Feel free to add any catories you want.

vagrant@vagrant:/vagrant/catalog$ python categoryCreator.py

Step 3. Run the project.py file.

vagrant@vagrant:/vagrant/catalog$ python project.py

Step 3. Navigate to http://localhost:8000/catalog/ in your web browser.

Step 4. Explore the application in whatever way you choose.

Author
Doug Mello
