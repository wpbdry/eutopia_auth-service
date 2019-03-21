import secret

# Edit the below variables to match correct database settings
db_type = 'postgresql'
db_user = 'postgres'
db_password = secret.database_password
db_url = 'localhost'
db_port = '5432'
db_name = 'eut-auth'

db_connection_string = "%s://%s:%s@%s:%s/%s" % (db_type, db_user, db_password, db_url, db_port, db_name)


# Flask settings
flask_host = "localhost"
flask_port = 5000