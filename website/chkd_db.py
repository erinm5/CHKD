import psycopg2     # db library
import datetime     # time zone
import pytz
from sqlalchemy import DECIMAL         # time zone
from decimal import Decimal

# Connect to the CHKD Database
curr_time = datetime.datetime.now(pytz.timezone('US/Eastern'))
conn = psycopg2.connect(database="CHKD", user = "postgres", password = "postgres", host = "127.0.0.1", port = "5432")
cur = conn.cursor()

# When finished with db call, close DB connection
def finished():
    conn.close()

# Fill in the blanks if you want to create more users
def newUser():
    full_name = " "
    username = " "
    password = "abc123"
    # Make the Database Call
    cur.execute("INSERT INTO public.user(full_name,username,password, created_at,updated_at) VALUES (%s, %s,'%s, %s, %s)",[full_name, username, password, curr_time,curr_time])
    conn.commit()

# Creates a new Group
def newGroup(name, owner):
    # Gets the user ID
    userId = findUser(owner)
    # Make the Database Call
    cur.execute("INSERT INTO public.group(full_name,username,password, created_at,updated_at) VALUES (%s, %s, %s, %s)",[name, userId, curr_time,curr_time])
    conn.commit()


# Look for user via username
def findUser(username):
    try:
        cur.execute( "SELECT user_id FROM public.user WHERE username = %s", [username] )
        userId = cur.fetchone()
        conn.commit()

        # checks if user exists
        if(userId):
            userId = userId[0]
            return userId
        
        else:
            return -1

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print("The username search failed. Try again")
        conn.rollback() 

# Login via username and password
def login(username, password):
    try:
        cur.execute( "SELECT user_id FROM public.user WHERE username = %s and password = %s", [username, password] )
        userId = cur.fetchone()
        conn.commit()

        # checks if user exists
        if(userId):
            userId = userId[0]
            return userId
        
        else:
            return -1

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print("The username or password you’ve entered is incorrect. Try again")
        conn.rollback() 