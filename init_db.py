import psycopg2
import sqlite3
from datetime import date
from urllib.parse import urlparse

#postgres_url = "your_postgres_database_url_here"
#url_parts = urlparse(postgres_url)
#conn = psycopg2.connect(
    #host=url_parts.hostname,
    #port=url_parts.port,
    #database=url_parts.path[1:], 
    #user=url_parts.username,
    #password=url_parts.password,
#)

conn = sqlite3.connect('database/studentsupport.db',check_same_thread=False)

c = conn.cursor()

def create_tables():
  
    c.execute('''CREATE TABLE doctors (
        first_name text,
        last_name text,
        dob date,
        phone_number integer,
        address text,
        doc_id integer,
        password text,
        speciality text,
        status integer
        )''')
    conn.commit()
   
    c.execute('''CREATE TABLE patients (
        first_name text,
        last_name text,
        dob date,
        phone_number integer,
        address text,
        patient_id integer,
        medical_history text,
        status integer
        )''')
    conn.commit()

    c.execute('''CREATE TABLE IF NOT EXISTS superusercreds(
        username text,
        password text
        )''')
    conn.commit()

    c.execute('''CREATE TABLE IF NOT EXISTS doctorappointmentrequests(
        docid integer,
        patientname text,
        patientnum integer,
        appointmentdate date
        )''')
    conn.commit()

    c.execute('''CREATE TABLE IF NOT EXISTS doctorappointments(
        docid integer,
        patientname text,
        patientnum integer,
        appointmentdate date
        )''')
    conn.commit()

if __name__ == '__main__':
    create_tables()
