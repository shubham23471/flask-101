Working repo for learning Flask. 


## Steps
1. export FLASK_APP=<app-name/pythonscript>
2. flask run or flask run --port 50001
3. `flask` command will look for .flaskenv files 



### Steps for GIT init. 
1. git init 
2. git remote add origin [repo-url]
3. git remote -v 
4. git status
5. auth using PAT


### Adding a new table using ORM
1. Create the model class in app/models.py. 
2. flask db migrate -m "<table-name>"
3. flask db upgrade 



### Tools Used
1. DB browser for SQLlite: Perfect for loading .db files and run query. 


### Tips
1. It is always best to move the application logic away from view functions and into models or other auxiliary classes or modules, because as you will see later in this chapter, that makes **unit testing** much easier. For eg: Functionality to follow and unfollow is writted in models.py

### Note
1. User password reset via Email is not tested yet.