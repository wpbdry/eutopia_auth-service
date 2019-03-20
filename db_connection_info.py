import secret

# Edit the below variables to match correct database settings
db_type = 'postgresql'
user = 'postgres'
password = secret.database_password
url = 'localhost'
port = '5432'
db_name = 'eut-auth'

connection_string = "%s://%s:%s@%s:%s/%s" % (db_type, user, password, url, port, db_name)
