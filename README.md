# ShareJar

##Clone this repository
$ git clone https://github.com/lpalmore/ShareJar.git

##Setting up Virtual Environment
$ pip install virtualenv  
$virtualenv -p /usr/bin/python2.7 venv  
$ cd ShareJar  
/ShareJar $ source venv/bin/activate (this is for a Mac)  

##Download requirements
(venv) $ pip install –r requirements.txt

##Start the App
/ShareJar $ source venv/bin/activate  
/ShareJar $ python manage.py runserver  
See the app running by going to http://127.0.0.1:8000/  

##Creating Users (temporarily)
/ShareJar/sharejarsite $ python manage.py createsuperuser  

##Deactivate the virtual environment
(venv) $ deactivate

##After downloading anything using pip for this project, please run this
$ pip freeze > requirements.txt
