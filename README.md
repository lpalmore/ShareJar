# ShareJar

##Clone this repository
$ git clone https://github.com/lpalmore/ShareJar.git

##Install Virtual Environment
$ pip install virtualenv

##Activate the Virtual Environment included with this github project
$ cd ShareJar
/ShareJar $ source venv/bin/activate

##Download requirements
(venv) $ pip install –r requirements.txt

##Start the App
/ShareJar $ source venv/bin/activate
/ShareJar $ python manage.py runserver
See the app running by going to http://127.0.0.1:8000/

##Deactivate the virtual environment
(venv) $ deactivate

##After downloading anything for this project
$ pip freeze > requirements.txt
