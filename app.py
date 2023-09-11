from datetime import datetime
import sqlite3
from datetime import date
from flask import Flask,request,render_template
import psycopg2
from urllib.parse import urlparse

app = Flask(__name__)

#conn = sqlite3.connect('database/studentsupport.db',check_same_thread=False)
postgres_url = "postgres://jxfjpzmwdyejru:3b010fa533acfb800a8f0ea5ef7d3faa2ac281af2d110e8a27b8c607a3ab0571@ec2-99-80-246-170.eu-west-1.compute.amazonaws.com:5432/dmuc4ce13v3h6"
url_parts = urlparse(postgres_url)
conn = psycopg2.connect(
    host=url_parts.hostname,
    port=url_parts.port,
    database=url_parts.path[1:], 
    user=url_parts.username,
    password=url_parts.password,
)

c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS counsellors(
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

c.execute('''CREATE TABLE IF NOT EXISTS students(
            first_name text,
            last_name text,
            dob date,
            phone_number integer,
            password text,
            address text,
            status integer
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS superusercreds(
            username text,
            password text
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS counsellorappointmentrequests(
            docid integer,
            studentname text,
            studentnum integer,
            appointmentdate date
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS counsellorappointments(
            docid integer,
            studentname text,
            studentnum integer,
            appointmentdate date
            )''')



c.execute('SELECT * from superusercreds')
conn.commit()
adminuser = c.fetchall()
if not adminuser:
    c.execute("INSERT INTO superusercreds VALUES ('admin','admin')")
    conn.commit()


def datetoday():
    today = datetime.now().strftime("%Y-%m-%d")
    return today

def checkonlyalpha(x):
    return x.isalpha()

def checkonlynum(x):
    return x.isdigit()

def checkpass(x):
    f1,f2,f3 = False,False,False
    if len(x)<8:
        return False
    if any(c.isalpha() for c in x):
        f1 = True
    if any(c.isdigit() for c in x):
        f2 = True
    if any(c in x for c in ['@','$','!']):
        f3 = True

    return f1 and f2 and f3

def checkphnlen(x):
    return len(x)==10

def retalldocsandapps():
    c.execute(f"SELECT * FROM counsellorappointments")
    conn.commit()
    docsandapps = c.fetchall()
    l = len(docsandapps)
    return docsandapps,l

def getpatdetails(phn):
    c.execute(f"SELECT * FROM students")
    conn.commit()
    students = c.fetchall()
    for i in students:
        if str(i[3])==str(phn):
            return i

def getdocdetails(docid):
    c.execute(f"SELECT * FROM counsellors")
    conn.commit()
    counsellors = c.fetchall()
    for i in counsellors:
        if str(i[5])==str(docid):
            return i


def retdocsandapps(docid):
    c.execute(f"SELECT * FROM counsellorappointments")
    conn.commit()
    docsandapps = c.fetchall()
    docsandapps2 = []
    for i in docsandapps:
        if str(i[0])==str(docid):
            docsandapps2.append(i)
    l = len(docsandapps2)
    return docsandapps2,l

def retapprequests(docid):
    c.execute(f"SELECT * FROM counsellorappointmentrequests")
    conn.commit()
    appreq = c.fetchall()
    appreq2 = []
    for i in appreq:
        if str(i[0])==str(docid):
            appreq2.append(i)
    l = len(appreq2)
    return appreq,l

def ret_student_reg_requests():
    c.execute('SELECT * FROM students')
    conn.commit()
    data = c.fetchall()
    student_reg_requests = []
    for d in data:
        if str(d[-1])=='0':
            student_reg_requests.append(d)
    return student_reg_requests

def ret_counsellor_reg_requests():
    c.execute('SELECT * FROM counsellors')
    conn.commit()
    data = c.fetchall()
    counsellor_reg_requests = []
    for d in data:
        if str(d[-1])=='0':
            counsellor_reg_requests.append(d)
    return counsellor_reg_requests

def ret_registered_students():
    c.execute('SELECT * FROM students')
    conn.commit()
    data = c.fetchall()
    registered_students = []
    for d in data:
        if str(d[-1])=='1':
            registered_students.append(d)
    return registered_students

def ret_registered_counsellors():
    c.execute('SELECT * FROM counsellors')
    conn.commit()
    data = c.fetchall()
    registered_counsellors = []
    for d in data:
        if str(d[-1])=='1':
            registered_counsellors.append(d)
    return registered_counsellors

def ret_docname_docspec():
    c.execute('SELECT * FROM counsellors')
    conn.commit()
    registered_counsellors = c.fetchall()
    docname_docid = []
    for i in registered_counsellors:
        docname_docid.append(str(i[0])+' '+str(i[1])+'-'+str(i[5])+'-'+str(i[7]))
    l = len(docname_docid)
    return docname_docid,l

def getdocname(docid):
    c.execute('SELECT * FROM counsellors')
    conn.commit()
    registered_counsellors = c.fetchall()
    for i in registered_counsellors:
        if str(i[5])==str(docid):
            return i[0]+'-'+i[1]

def getpatname(patnum):
    c.execute('SELECT * FROM students')
    conn.commit()
    details = c.fetchall()
    for i in details:
        if str(i[3])==str(patnum):
            return i[0]+' '+i[1]
    else:
        return -1

def get_all_docids():
    c.execute('SELECT * FROM counsellors')
    conn.commit()
    registered_counsellors = c.fetchall()
    docids = []
    for i in registered_counsellors:
        docids.append(str(i[5]))
    return docids


def get_all_patnums():
    c.execute('SELECT * FROM students')
    conn.commit()
    registered_students = c.fetchall()
    patnums = []
    for i in registered_students:
        patnums.append(str(i[3]))
    return patnums



@app.route('/')
def home():
    return render_template('home.html') 


@app.route('/studentreg')
def patreg():
    return render_template('studentregistration.html') 


@app.route('/counselorreg')
def docreg():
    return render_template('counselorregistration.html') 


@app.route('/studentlogin')
def loginpage1():
    return render_template('studentlogin.html') 


@app.route('/counsellorlogin')
def loginpage2():
    return render_template('counsellorlogin.html') 


@app.route('/adminlogin')
def loginpage3():
    return render_template('adminlogin.html') 



@app.route('/addstudent',methods=['POST'])
def addstudent():
    passw = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    dob = request.form['dob']
    phn = request.form['phn']
    address = request.form['address']
    print(firstname,lastname,checkonlyalpha(firstname),checkonlyalpha(lastname))

    if (not checkonlyalpha(firstname)) | (not checkonlyalpha(lastname)):
        return render_template('studentregistration.html',mess=f'First Name and Last Name can only contain alphabets.')

    if not checkpass(passw):
        return render_template('studentregistration.html',mess=f"Password should be of length 8 and should contain alphabets, numbers and special characters ('@','$','!').") 

    if not checkphnlen(phn):
        return render_template('studentregistration.html',mess=f"Phone number should be of length 10.") 

    if str(phn) in get_all_patnums():
        return render_template('studentregistration.html',mess=f'student with mobile number {phn} already exists.') 
    c.execute(f"INSERT INTO students VALUES ('{firstname}','{lastname}','{dob}','{phn}','{passw}','{address}',0)")
    conn.commit()
    return render_template('home.html',mess=f'Registration Request sent to Super Admin for student {firstname}.')


@app.route('/addcounsellor',methods=['GET','POST'])
def addcounsellor():
    passw = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    dob = request.form['dob']
    phn = request.form['phn']
    address = request.form['address']
    docid = request.form['docid']
    spec = request.form['speciality']
    
    if not checkonlyalpha(firstname) and not checkonlyalpha(lastname):
        return render_template('counselorregistration.html',mess=f'First Name and Last Name can only contain alphabets.')

    if not checkonlyalpha(spec):
        return render_template('counselorregistration.html',mess=f'counsellor Speciality can only contain alphabets.')

    if not checkpass(passw):
        return render_template('counselorregistration.html',mess=f"Password should be of length 8 and should contain alphabets, numbers and special characters ('@','$','!').") 
    
    if not checkphnlen(phn):
        return render_template('counselorregistration.html',mess=f"Phone number should be of length 10.") 

    if str(docid) in get_all_docids():
        return render_template('counselorregistration.html',mess=f'counsellor with Counsellor ID {docid} already exists.') 
    c.execute(f"INSERT INTO counsellors VALUES ('{firstname}','{lastname}','{dob}','{phn}','{address}','{docid}','{passw}','{spec}',0)")
    conn.commit()
    return render_template('home.html',mess=f'Registration Request sent to Super Admin for counsellor {firstname}.') 



@app.route('/studentpage',methods=['GET','POST'])
def studentpage():
    phn = request.form['phn']
    passw = request.form['pass']
    c.execute('SELECT * FROM students')
    conn.commit()
    registerd_students = c.fetchall()
    for i in registerd_students:
        if str(i[3])==str(phn) and str(i[4])==str(passw):
            docsandapps,l = retalldocsandapps()
            docname_docid,l2 = ret_docname_docspec()
            docnames = []
            for i in docsandapps:
                docnames.append(getdocname(i[0]))
            return render_template('studentpage.html',docsandapps=docsandapps,docnames=docnames,docname_docid=docname_docid,l=l,l2=l2,patname=i[0],phn=phn) 

    else:
        return render_template('studentlogin.html',err='Please enter correct credentials...')


@app.route('/counselorpage',methods=['GET','POST'])
def counselorpage():
    docid = request.form['docid']
    passw = request.form['pass']
    c.execute('SELECT * FROM counsellors')
    conn.commit()
    registerd_counsellors = c.fetchall()

    for i in registerd_counsellors:
        if str(i[5])==str(docid) and str(i[6])==str(passw):
            appointment_requests_for_this_counsellor,l1 = retapprequests(docid)
            fix_appointment_for_this_counsellor,l2 = retdocsandapps(docid)
            return render_template('counselorpage.html',appointment_requests_for_this_counsellor=appointment_requests_for_this_counsellor,fix_appointment_for_this_counsellor=fix_appointment_for_this_counsellor,l1=l1,l2=l2,docname=i[0],docid=docid)

    else:
        return render_template('counsellorlogin.html',err='Please enter correct credentials...')
    

@app.route('/adminpage',methods=['GET','POST'])
def adminpage():
    username = request.form['username']
    passw = request.form['pass']
    c.execute('SELECT * FROM superusercreds')
    conn.commit()
    superusercreds = c.fetchall()

    for i in superusercreds:
        if str(i[0])==str(username) and str(i[1])==str(passw):
            student_reg_requests = ret_student_reg_requests()
            counsellor_reg_requests = ret_counsellor_reg_requests()
            registered_students = ret_registered_students()
            registered_counsellors = ret_registered_counsellors()
            l1 = len(student_reg_requests)
            l2 = len(counsellor_reg_requests)
            l3 = len(registered_students)
            l4 = len(registered_counsellors)
            return render_template('adminpage.html',student_reg_requests=student_reg_requests,counsellor_reg_requests=counsellor_reg_requests,registered_students=registered_students,registered_counsellors=registered_counsellors,l1=l1,l2=l2,l3=l3,l4=l4)
    else:
        return render_template('adminlogin.html',err='Please enter correct credentials...')
    

@app.route('/deletestudent',methods=['GET','POST'])
def deletestudent():
    patnum = request.values['patnum']
    c.execute(f"DELETE FROM students WHERE phone_number='{str(patnum)}' ")
    conn.commit()
    student_reg_requests = ret_student_reg_requests()
    counsellor_reg_requests = ret_counsellor_reg_requests()
    registered_students = ret_registered_students()
    registered_counsellors = ret_registered_counsellors()
    l1 = len(student_reg_requests)
    l2 = len(counsellor_reg_requests)
    l3 = len(registered_students)
    l4 = len(registered_counsellors)
    return render_template('adminpage.html',student_reg_requests=student_reg_requests,counsellor_reg_requests=counsellor_reg_requests,registered_students=registered_students,registered_counsellors=registered_counsellors,l1=l1,l2=l2,l3=l3,l4=l4)
    

@app.route('/deletecounsellor',methods=['GET','POST'])
def deletecounsellor():
    docid = request.values['docid']
    c.execute(f"DELETE FROM counsellors WHERE doc_id='{str(docid)}' ")
    conn.commit()
    student_reg_requests = ret_student_reg_requests()
    counsellor_reg_requests = ret_counsellor_reg_requests()
    registered_students = ret_registered_students()
    registered_counsellors = ret_registered_counsellors()
    l1 = len(student_reg_requests)
    l2 = len(counsellor_reg_requests)
    l3 = len(registered_students)
    l4 = len(registered_counsellors)
    return render_template('adminpage.html',student_reg_requests=student_reg_requests,counsellor_reg_requests=counsellor_reg_requests,registered_students=registered_students,registered_counsellors=registered_counsellors,l1=l1,l2=l2,l3=l3,l4=l4)
   

@app.route('/makeappointment',methods=['GET','POST'])
def makeappointment():
    patnum = request.args['phn']
    appdate = request.form['appdate']
    whichcounsellor = request.form['whichcounsellor']
    docname = whichcounsellor.split('-')[0]
    docid = whichcounsellor.split('-')[1]
    patname = getpatname(patnum)
    appdate2 = datetime.strptime(appdate, '%Y-%m-%d').strftime("%Y-%m-%d")
    print(appdate2,datetoday())
    if appdate2>datetoday():
        if patname!=-1:
            c.execute(f"INSERT INTO counsellorappointmentrequests VALUES ('{docid}','{patname}','{patnum}','{appdate}')")
            conn.commit()
            docsandapps,l = retalldocsandapps()
            docname_docid,l2 = ret_docname_docspec()
            docnames = []
            for i in docsandapps:
                docnames.append(getdocname(i[0]))
            return render_template('studentpage.html',mess=f'Appointment Request sent to Counselor.',docnames=docnames,docsandapps=docsandapps,docname_docid=docname_docid,l=l,l2=l2,patname=patname) 
        else:
            docsandapps,l = retalldocsandapps()
            docname_docid,l2 = ret_docname_docspec()
            docnames = []
            for i in docsandapps:
                docnames.append(getdocname(i[0]))
            return render_template('studentpage.html',mess=f'No user with such contact number.',docnames=docnames,docsandapps=docsandapps,docname_docid=docname_docid,l=l,l2=l2,patname=patname) 
    else:
        docsandapps,l = retalldocsandapps()
        docname_docid,l2 = ret_docname_docspec()
        docnames = []
        for i in docsandapps:
            docnames.append(getdocname(i[0]))
        return render_template('studentlogin.html',mess=f'Please select a date after today.',docnames=docnames,docsandapps=docsandapps,docname_docid=docname_docid,l=l,l2=l2,patname=patname) 


@app.route('/approvecounsellor')
def approvecounsellor():
    doctoapprove = request.values['docid']
    c.execute('SELECT * FROM counsellors')
    conn.commit()
    counsellor_requests = c.fetchall()
    for i in counsellor_requests:
        if str(i[5])==str(doctoapprove):
            c.execute(f"UPDATE counsellors SET status=1 WHERE doc_id={str(doctoapprove)}")
            conn.commit()
            student_reg_requests = ret_student_reg_requests()
            counsellor_reg_requests = ret_counsellor_reg_requests()
            registered_students = ret_registered_students()
            registered_counsellors = ret_registered_counsellors()
            l1 = len(student_reg_requests)
            l2 = len(counsellor_reg_requests)
            l3 = len(registered_students)
            l4 = len(registered_counsellors)
            return render_template('adminpage.html',mess=f'counsellor Approved successfully!!!',student_reg_requests=student_reg_requests,counsellor_reg_requests=counsellor_reg_requests,registered_students=registered_students,registered_counsellors=registered_counsellors,l1=l1,l2=l2,l3=l3,l4=l4) 
    else:
        student_reg_requests = ret_student_reg_requests()
        counsellor_reg_requests = ret_counsellor_reg_requests()
        registered_students = ret_registered_students()
        registered_counsellors = ret_registered_counsellors()
        l1 = len(student_reg_requests)
        l2 = len(counsellor_reg_requests)
        l3 = len(registered_students)
        l4 = len(registered_counsellors)
        return render_template('adminpage.html',mess=f'counsellor Not Approved...',student_reg_requests=student_reg_requests,counsellor_reg_requests=counsellor_reg_requests,registered_students=registered_students,registered_counsellors=registered_counsellors,l1=l1,l2=l2,l3=l3,l4=l4) 


@app.route('/approvestudent')
def approvestudent():
    pattoapprove = request.values['patnum']
    c.execute('SELECT * FROM students')
    conn.commit()
    student_requests = c.fetchall()
    for i in student_requests:
        if str(i[3])==str(pattoapprove):
            c.execute(f"UPDATE students SET status=1 WHERE phone_number={str(pattoapprove)}")
            conn.commit()
            student_reg_requests = ret_student_reg_requests()
            counsellor_reg_requests = ret_counsellor_reg_requests()
            registered_students = ret_registered_students()
            registered_counsellors = ret_registered_counsellors()
            l1 = len(student_reg_requests)
            l2 = len(counsellor_reg_requests)
            l3 = len(registered_students)
            l4 = len(registered_counsellors)
            return render_template('adminpage.html',mess=f'student Approved successfully!!!',student_reg_requests=student_reg_requests,counsellor_reg_requests=counsellor_reg_requests,registered_students=registered_students,registered_counsellors=registered_counsellors,l1=l1,l2=l2,l3=l3,l4=l4) 

    else:
        student_reg_requests = ret_student_reg_requests()
        counsellor_reg_requests = ret_counsellor_reg_requests()
        registered_students = ret_registered_students()
        registered_counsellors = ret_registered_counsellors()
        l1 = len(student_reg_requests)
        l2 = len(counsellor_reg_requests)
        l3 = len(registered_students)
        l4 = len(registered_counsellors)
        return render_template('adminpage.html',mess=f'student Not Approved...',student_reg_requests=student_reg_requests,counsellor_reg_requests=counsellor_reg_requests,registered_students=registered_students,registered_counsellors=registered_counsellors,l1=l1,l2=l2,l3=l3,l4=l4) 


@app.route('/counsellorapproveappointment')
def counsellorapproveappointment():
    docid = request.values['docid']
    patnum = request.values['patnum']
    patname = request.values['patname']
    appdate = request.values['appdate']
    c.execute(f"INSERT INTO counsellorappointments VALUES ('{docid}','{patname}','{patnum}','{appdate}')")
    conn.commit()
    c.execute(f"DELETE FROM counsellorappointmentrequests WHERE studentnum='{str(patnum)}'")
    conn.commit()
    appointment_requests_for_this_counsellor,l1 = retapprequests(docid)
    fix_appointment_for_this_counsellor,l2 = retdocsandapps(docid)
    return render_template('counselorpage.html',appointment_requests_for_this_counsellor=appointment_requests_for_this_counsellor,fix_appointment_for_this_counsellor=fix_appointment_for_this_counsellor,l1=l1,l2=l2,docid=docid)

@app.route('/counsellordeleteappointment')
def counsellordeleteappointment():
    docid = request.values['docid']
    patnum = request.values['patnum']
    c.execute(f"DELETE FROM counsellorappointmentrequests WHERE studentnum='{str(patnum)}'")
    conn.commit()
    appointment_requests_for_this_counsellor,l1 = retapprequests(docid)
    fix_appointment_for_this_counsellor,l2 = retdocsandapps(docid)
    return render_template('counselorpage.html',appointment_requests_for_this_counsellor=appointment_requests_for_this_counsellor,fix_appointment_for_this_counsellor=fix_appointment_for_this_counsellor,l1=l1,l2=l2,docid=docid)

@app.route('/deletecounsellorrequest')
def deletecounsellorrequest():
    docid = request.values['docid']
    c.execute(f"DELETE FROM counsellors WHERE doc_id='{str(docid)}'")
    conn.commit()
    student_reg_requests = ret_student_reg_requests()
    counsellor_reg_requests = ret_counsellor_reg_requests()
    registered_students = ret_registered_students()
    registered_counsellors = ret_registered_counsellors()
    l1 = len(student_reg_requests)
    l2 = len(counsellor_reg_requests)
    l3 = len(registered_students)
    l4 = len(registered_counsellors)
    return render_template('adminpage.html',student_reg_requests=student_reg_requests,counsellor_reg_requests=counsellor_reg_requests,registered_students=registered_students,registered_counsellors=registered_counsellors,l1=l1,l2=l2,l3=l3,l4=l4) 

@app.route('/deletestudentrequest')
def deletestudentrequest():
    patnum = request.values['patnum']
    c.execute(f"DELETE FROM students WHERE phone_number='{str(patnum)}'")
    conn.commit()
    student_reg_requests = ret_student_reg_requests()
    counsellor_reg_requests = ret_counsellor_reg_requests()
    registered_students = ret_registered_students()
    registered_counsellors = ret_registered_counsellors()
    l1 = len(student_reg_requests)
    l2 = len(counsellor_reg_requests)
    l3 = len(registered_students)
    l4 = len(registered_counsellors)
    return render_template('adminpage.html',student_reg_requests=student_reg_requests,counsellor_reg_requests=counsellor_reg_requests,registered_students=registered_students,registered_counsellors=registered_counsellors,l1=l1,l2=l2,l3=l3,l4=l4) 


@app.route('/updatestudent')
def updatestudent():
    phn = request.args['phn']
    fn,ln,dob,phn,passw,add,status = getpatdetails(phn)
    return render_template('updatestudent.html',fn=fn,ln=ln,dob=dob,phn=phn,passw=passw,add=add,status=status) 


@app.route('/updatecounselor')
def updatecounselor():
    docid = request.args['docid']
    fn,ln,dob,phn,add,docid,passw,spec,status = getdocdetails(docid)
    return render_template('updatecounselor.html',fn=fn,ln=ln,dob=dob,phn=phn,passw=passw,add=add,status=status,spec=spec,docid=docid) 

@app.route('/makecounsellorupdates',methods=['GET','POST'])
def makecounsellorupdates():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    dob = request.form['dob']
    phn = request.form['phn']
    address = request.form['address']
    docid = request.args['docid']
    spec = request.form['speciality']
    c.execute("UPDATE counsellors SET first_name=(?) WHERE doc_id=(?)",(firstname,docid))
    conn.commit()
    c.execute("UPDATE counsellors SET last_name=(?) WHERE doc_id=(?)",(lastname,docid))
    conn.commit()
    c.execute("UPDATE counsellors SET dob=(?) WHERE doc_id=(?)",(dob,docid))
    conn.commit()
    c.execute("UPDATE counsellors SET phone_number=(?) WHERE doc_id=(?)",(phn,docid))
    conn.commit()
    c.execute("UPDATE counsellors SET address=(?) WHERE doc_id=(?)",(address,docid))
    conn.commit()
    c.execute("UPDATE counsellors SET speciality=(?) WHERE doc_id=(?)",(spec,docid))
    conn.commit()
    return render_template('home.html',mess='Updations Done Successfully!!!') 

    
@app.route('/makestudentupdates',methods=['GET','POST'])
def makestudentupdates():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    dob = request.form['dob']
    phn = request.args['phn']
    address = request.form['address']
    c.execute("UPDATE students SET first_name=(?) WHERE phone_number=(?)",(firstname,phn))
    conn.commit()
    c.execute("UPDATE students SET last_name=(?) WHERE phone_number=(?)",(lastname,phn))
    conn.commit()
    c.execute("UPDATE students SET dob=(?) WHERE phone_number=(?)",(dob,phn))
    conn.commit()
    c.execute("UPDATE students SET address=(?) WHERE phone_number=(?)",(address,phn))
    conn.commit()
    return render_template('home.html',mess='Updations Done Successfully!!!') 


if __name__ == '__main__':
    app.run(debug=True)
