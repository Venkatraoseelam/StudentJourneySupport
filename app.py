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

c.execute('''CREATE TABLE IF NOT EXISTS doctors(
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

c.execute('''CREATE TABLE IF NOT EXISTS patients(
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

c.execute('''CREATE TABLE IF NOT EXISTS doctorappointmentrequests(
            docid integer,
            patientname text,
            patientnum integer,
            appointmentdate date
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS doctorappointments(
            docid integer,
            patientname text,
            patientnum integer,
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
    c.execute(f"SELECT * FROM doctorappointments")
    conn.commit()
    docsandapps = c.fetchall()
    l = len(docsandapps)
    return docsandapps,l

def getpatdetails(phn):
    c.execute(f"SELECT * FROM patients")
    conn.commit()
    patients = c.fetchall()
    for i in patients:
        if str(i[3])==str(phn):
            return i

def getdocdetails(docid):
    c.execute(f"SELECT * FROM doctors")
    conn.commit()
    doctors = c.fetchall()
    for i in doctors:
        if str(i[5])==str(docid):
            return i


def retdocsandapps(docid):
    c.execute(f"SELECT * FROM doctorappointments")
    conn.commit()
    docsandapps = c.fetchall()
    docsandapps2 = []
    for i in docsandapps:
        if str(i[0])==str(docid):
            docsandapps2.append(i)
    l = len(docsandapps2)
    return docsandapps2,l

def retapprequests(docid):
    c.execute(f"SELECT * FROM doctorappointmentrequests")
    conn.commit()
    appreq = c.fetchall()
    appreq2 = []
    for i in appreq:
        if str(i[0])==str(docid):
            appreq2.append(i)
    l = len(appreq2)
    return appreq,l

def ret_patient_reg_requests():
    c.execute('SELECT * FROM patients')
    conn.commit()
    data = c.fetchall()
    patient_reg_requests = []
    for d in data:
        if str(d[-1])=='0':
            patient_reg_requests.append(d)
    return patient_reg_requests

def ret_doctor_reg_requests():
    c.execute('SELECT * FROM doctors')
    conn.commit()
    data = c.fetchall()
    doctor_reg_requests = []
    for d in data:
        if str(d[-1])=='0':
            doctor_reg_requests.append(d)
    return doctor_reg_requests

def ret_registered_patients():
    c.execute('SELECT * FROM patients')
    conn.commit()
    data = c.fetchall()
    registered_patients = []
    for d in data:
        if str(d[-1])=='1':
            registered_patients.append(d)
    return registered_patients

def ret_registered_doctors():
    c.execute('SELECT * FROM doctors')
    conn.commit()
    data = c.fetchall()
    registered_doctors = []
    for d in data:
        if str(d[-1])=='1':
            registered_doctors.append(d)
    return registered_doctors

def ret_docname_docspec():
    c.execute('SELECT * FROM doctors')
    conn.commit()
    registered_doctors = c.fetchall()
    docname_docid = []
    for i in registered_doctors:
        docname_docid.append(str(i[0])+' '+str(i[1])+'-'+str(i[5])+'-'+str(i[7]))
    l = len(docname_docid)
    return docname_docid,l

def getdocname(docid):
    c.execute('SELECT * FROM doctors')
    conn.commit()
    registered_doctors = c.fetchall()
    for i in registered_doctors:
        if str(i[5])==str(docid):
            return i[0]+'-'+i[1]

def getpatname(patnum):
    c.execute('SELECT * FROM patients')
    conn.commit()
    details = c.fetchall()
    for i in details:
        if str(i[3])==str(patnum):
            return i[0]+' '+i[1]
    else:
        return -1

def get_all_docids():
    c.execute('SELECT * FROM doctors')
    conn.commit()
    registered_doctors = c.fetchall()
    docids = []
    for i in registered_doctors:
        docids.append(str(i[5]))
    return docids


def get_all_patnums():
    c.execute('SELECT * FROM patients')
    conn.commit()
    registered_patients = c.fetchall()
    patnums = []
    for i in registered_patients:
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



@app.route('/addpatient',methods=['POST'])
def addpatient():
    passw = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    dob = request.form['dob']
    phn = request.form['phn']
    address = request.form['address']
    print(firstname,lastname,checkonlyalpha(firstname),checkonlyalpha(lastname))

    if (not checkonlyalpha(firstname)) | (not checkonlyalpha(lastname)):
        return render_template('home.html',mess=f'First Name and Last Name can only contain alphabets.')

    if not checkpass(passw):
        return render_template('home.html',mess=f"Password should be of length 8 and should contain alphabets, numbers and special characters ('@','$','!').") 

    if not checkphnlen(phn):
        return render_template('home.html',mess=f"Phone number should be of length 10.") 

    if str(phn) in get_all_patnums():
        return render_template('home.html',mess=f'Patient with mobile number {phn} already exists.') 
    c.execute(f"INSERT INTO patients VALUES ('{firstname}','{lastname}','{dob}','{phn}','{passw}','{address}',0)")
    conn.commit()
    return render_template('home.html',mess=f'Registration Request sent to Super Admin for Patient {firstname}.')


@app.route('/adddoctor',methods=['GET','POST'])
def adddoctor():
    passw = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    dob = request.form['dob']
    phn = request.form['phn']
    address = request.form['address']
    docid = request.form['docid']
    spec = request.form['speciality']
    
    if not checkonlyalpha(firstname) and not checkonlyalpha(lastname):
        return render_template('home.html',mess=f'First Name and Last Name can only contain alphabets.')

    if not checkonlyalpha(spec):
        return render_template('home.html',mess=f'Doctor Speciality can only contain alphabets.')

    if not checkpass(passw):
        return render_template('home.html',mess=f"Password should be of length 8 and should contain alphabets, numbers and special characters ('@','$','!').") 
    
    if not checkphnlen(phn):
        return render_template('home.html',mess=f"Phone number should be of length 10.") 

    if str(docid) in get_all_docids():
        return render_template('home.html',mess=f'Doctor with Doc ID {docid} already exists.') 
    c.execute(f"INSERT INTO doctors VALUES ('{firstname}','{lastname}','{dob}','{phn}','{address}','{docid}','{passw}','{spec}',0)")
    conn.commit()
    return render_template('home.html',mess=f'Registration Request sent to Super Admin for Doctor {firstname}.') 



@app.route('/studentpage',methods=['GET','POST'])
def studentpage():
    phn = request.form['phn']
    passw = request.form['pass']
    c.execute('SELECT * FROM patients')
    conn.commit()
    registerd_patients = c.fetchall()
    for i in registerd_patients:
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
    c.execute('SELECT * FROM doctors')
    conn.commit()
    registerd_doctors = c.fetchall()

    for i in registerd_doctors:
        if str(i[5])==str(docid) and str(i[6])==str(passw):
            appointment_requests_for_this_doctor,l1 = retapprequests(docid)
            fix_appointment_for_this_doctor,l2 = retdocsandapps(docid)
            return render_template('counselorpage.html',appointment_requests_for_this_doctor=appointment_requests_for_this_doctor,fix_appointment_for_this_doctor=fix_appointment_for_this_doctor,l1=l1,l2=l2,docname=i[0],docid=docid)

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
            patient_reg_requests = ret_patient_reg_requests()
            doctor_reg_requests = ret_doctor_reg_requests()
            registered_patients = ret_registered_patients()
            registered_doctors = ret_registered_doctors()
            l1 = len(patient_reg_requests)
            l2 = len(doctor_reg_requests)
            l3 = len(registered_patients)
            l4 = len(registered_doctors)
            return render_template('adminpage.html',patient_reg_requests=patient_reg_requests,doctor_reg_requests=doctor_reg_requests,registered_patients=registered_patients,registered_doctors=registered_doctors,l1=l1,l2=l2,l3=l3,l4=l4)
    else:
        return render_template('adminlogin.html',err='Please enter correct credentials...')
    

@app.route('/deletepatient',methods=['GET','POST'])
def deletepatient():
    patnum = request.values['patnum']
    c.execute(f"DELETE FROM patients WHERE phone_number='{str(patnum)}' ")
    conn.commit()
    patient_reg_requests = ret_patient_reg_requests()
    doctor_reg_requests = ret_doctor_reg_requests()
    registered_patients = ret_registered_patients()
    registered_doctors = ret_registered_doctors()
    l1 = len(patient_reg_requests)
    l2 = len(doctor_reg_requests)
    l3 = len(registered_patients)
    l4 = len(registered_doctors)
    return render_template('adminpage.html',patient_reg_requests=patient_reg_requests,doctor_reg_requests=doctor_reg_requests,registered_patients=registered_patients,registered_doctors=registered_doctors,l1=l1,l2=l2,l3=l3,l4=l4)
    

@app.route('/deletedoctor',methods=['GET','POST'])
def deletedoctor():
    docid = request.values['docid']
    c.execute(f"DELETE FROM doctors WHERE doc_id='{str(docid)}' ")
    conn.commit()
    patient_reg_requests = ret_patient_reg_requests()
    doctor_reg_requests = ret_doctor_reg_requests()
    registered_patients = ret_registered_patients()
    registered_doctors = ret_registered_doctors()
    l1 = len(patient_reg_requests)
    l2 = len(doctor_reg_requests)
    l3 = len(registered_patients)
    l4 = len(registered_doctors)
    return render_template('adminpage.html',patient_reg_requests=patient_reg_requests,doctor_reg_requests=doctor_reg_requests,registered_patients=registered_patients,registered_doctors=registered_doctors,l1=l1,l2=l2,l3=l3,l4=l4)
   

@app.route('/makeappointment',methods=['GET','POST'])
def makeappointment():
    patnum = request.args['phn']
    appdate = request.form['appdate']
    whichdoctor = request.form['whichdoctor']
    docname = whichdoctor.split('-')[0]
    docid = whichdoctor.split('-')[1]
    patname = getpatname(patnum)
    appdate2 = datetime.strptime(appdate, '%Y-%m-%d').strftime("%Y-%m-%d")
    print(appdate2,datetoday())
    if appdate2>datetoday():
        if patname!=-1:
            c.execute(f"INSERT INTO doctorappointmentrequests VALUES ('{docid}','{patname}','{patnum}','{appdate}')")
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


@app.route('/approvedoctor')
def approvedoctor():
    doctoapprove = request.values['docid']
    c.execute('SELECT * FROM doctors')
    conn.commit()
    doctor_requests = c.fetchall()
    for i in doctor_requests:
        if str(i[5])==str(doctoapprove):
            c.execute(f"UPDATE doctors SET status=1 WHERE doc_id={str(doctoapprove)}")
            conn.commit()
            patient_reg_requests = ret_patient_reg_requests()
            doctor_reg_requests = ret_doctor_reg_requests()
            registered_patients = ret_registered_patients()
            registered_doctors = ret_registered_doctors()
            l1 = len(patient_reg_requests)
            l2 = len(doctor_reg_requests)
            l3 = len(registered_patients)
            l4 = len(registered_doctors)
            return render_template('adminpage.html',mess=f'Doctor Approved successfully!!!',patient_reg_requests=patient_reg_requests,doctor_reg_requests=doctor_reg_requests,registered_patients=registered_patients,registered_doctors=registered_doctors,l1=l1,l2=l2,l3=l3,l4=l4) 
    else:
        patient_reg_requests = ret_patient_reg_requests()
        doctor_reg_requests = ret_doctor_reg_requests()
        registered_patients = ret_registered_patients()
        registered_doctors = ret_registered_doctors()
        l1 = len(patient_reg_requests)
        l2 = len(doctor_reg_requests)
        l3 = len(registered_patients)
        l4 = len(registered_doctors)
        return render_template('adminpage.html',mess=f'Doctor Not Approved...',patient_reg_requests=patient_reg_requests,doctor_reg_requests=doctor_reg_requests,registered_patients=registered_patients,registered_doctors=registered_doctors,l1=l1,l2=l2,l3=l3,l4=l4) 


@app.route('/approvepatient')
def approvepatient():
    pattoapprove = request.values['patnum']
    c.execute('SELECT * FROM patients')
    conn.commit()
    patient_requests = c.fetchall()
    for i in patient_requests:
        if str(i[3])==str(pattoapprove):
            c.execute(f"UPDATE patients SET status=1 WHERE phone_number={str(pattoapprove)}")
            conn.commit()
            patient_reg_requests = ret_patient_reg_requests()
            doctor_reg_requests = ret_doctor_reg_requests()
            registered_patients = ret_registered_patients()
            registered_doctors = ret_registered_doctors()
            l1 = len(patient_reg_requests)
            l2 = len(doctor_reg_requests)
            l3 = len(registered_patients)
            l4 = len(registered_doctors)
            return render_template('adminpage.html',mess=f'Patient Approved successfully!!!',patient_reg_requests=patient_reg_requests,doctor_reg_requests=doctor_reg_requests,registered_patients=registered_patients,registered_doctors=registered_doctors,l1=l1,l2=l2,l3=l3,l4=l4) 

    else:
        patient_reg_requests = ret_patient_reg_requests()
        doctor_reg_requests = ret_doctor_reg_requests()
        registered_patients = ret_registered_patients()
        registered_doctors = ret_registered_doctors()
        l1 = len(patient_reg_requests)
        l2 = len(doctor_reg_requests)
        l3 = len(registered_patients)
        l4 = len(registered_doctors)
        return render_template('adminpage.html',mess=f'Patient Not Approved...',patient_reg_requests=patient_reg_requests,doctor_reg_requests=doctor_reg_requests,registered_patients=registered_patients,registered_doctors=registered_doctors,l1=l1,l2=l2,l3=l3,l4=l4) 


@app.route('/doctorapproveappointment')
def doctorapproveappointment():
    docid = request.values['docid']
    patnum = request.values['patnum']
    patname = request.values['patname']
    appdate = request.values['appdate']
    c.execute(f"INSERT INTO doctorappointments VALUES ('{docid}','{patname}','{patnum}','{appdate}')")
    conn.commit()
    c.execute(f"DELETE FROM doctorappointmentrequests WHERE patientnum='{str(patnum)}'")
    conn.commit()
    appointment_requests_for_this_doctor,l1 = retapprequests(docid)
    fix_appointment_for_this_doctor,l2 = retdocsandapps(docid)
    return render_template('counselorpage.html',appointment_requests_for_this_doctor=appointment_requests_for_this_doctor,fix_appointment_for_this_doctor=fix_appointment_for_this_doctor,l1=l1,l2=l2,docid=docid)

@app.route('/doctordeleteappointment')
def doctordeleteappointment():
    docid = request.values['docid']
    patnum = request.values['patnum']
    c.execute(f"DELETE FROM doctorappointmentrequests WHERE patientnum='{str(patnum)}'")
    conn.commit()
    appointment_requests_for_this_doctor,l1 = retapprequests(docid)
    fix_appointment_for_this_doctor,l2 = retdocsandapps(docid)
    return render_template('counselorpage.html',appointment_requests_for_this_doctor=appointment_requests_for_this_doctor,fix_appointment_for_this_doctor=fix_appointment_for_this_doctor,l1=l1,l2=l2,docid=docid)

@app.route('/deletedoctorrequest')
def deletedoctorrequest():
    docid = request.values['docid']
    c.execute(f"DELETE FROM doctors WHERE doc_id='{str(docid)}'")
    conn.commit()
    patient_reg_requests = ret_patient_reg_requests()
    doctor_reg_requests = ret_doctor_reg_requests()
    registered_patients = ret_registered_patients()
    registered_doctors = ret_registered_doctors()
    l1 = len(patient_reg_requests)
    l2 = len(doctor_reg_requests)
    l3 = len(registered_patients)
    l4 = len(registered_doctors)
    return render_template('adminpage.html',patient_reg_requests=patient_reg_requests,doctor_reg_requests=doctor_reg_requests,registered_patients=registered_patients,registered_doctors=registered_doctors,l1=l1,l2=l2,l3=l3,l4=l4) 

@app.route('/deletepatientrequest')
def deletepatientrequest():
    patnum = request.values['patnum']
    c.execute(f"DELETE FROM patients WHERE phone_number='{str(patnum)}'")
    conn.commit()
    patient_reg_requests = ret_patient_reg_requests()
    doctor_reg_requests = ret_doctor_reg_requests()
    registered_patients = ret_registered_patients()
    registered_doctors = ret_registered_doctors()
    l1 = len(patient_reg_requests)
    l2 = len(doctor_reg_requests)
    l3 = len(registered_patients)
    l4 = len(registered_doctors)
    return render_template('adminpage.html',patient_reg_requests=patient_reg_requests,doctor_reg_requests=doctor_reg_requests,registered_patients=registered_patients,registered_doctors=registered_doctors,l1=l1,l2=l2,l3=l3,l4=l4) 


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

@app.route('/makedoctorupdates',methods=['GET','POST'])
def makedoctorupdates():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    dob = request.form['dob']
    phn = request.form['phn']
    address = request.form['address']
    docid = request.args['docid']
    spec = request.form['speciality']
    c.execute("UPDATE doctors SET first_name=(?) WHERE doc_id=(?)",(firstname,docid))
    conn.commit()
    c.execute("UPDATE doctors SET last_name=(?) WHERE doc_id=(?)",(lastname,docid))
    conn.commit()
    c.execute("UPDATE doctors SET dob=(?) WHERE doc_id=(?)",(dob,docid))
    conn.commit()
    c.execute("UPDATE doctors SET phone_number=(?) WHERE doc_id=(?)",(phn,docid))
    conn.commit()
    c.execute("UPDATE doctors SET address=(?) WHERE doc_id=(?)",(address,docid))
    conn.commit()
    c.execute("UPDATE doctors SET speciality=(?) WHERE doc_id=(?)",(spec,docid))
    conn.commit()
    return render_template('home.html',mess='Updations Done Successfully!!!') 

    
@app.route('/makepatientupdates',methods=['GET','POST'])
def makepatientupdates():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    dob = request.form['dob']
    phn = request.args['phn']
    address = request.form['address']
    c.execute("UPDATE patients SET first_name=(?) WHERE phone_number=(?)",(firstname,phn))
    conn.commit()
    c.execute("UPDATE patients SET last_name=(?) WHERE phone_number=(?)",(lastname,phn))
    conn.commit()
    c.execute("UPDATE patients SET dob=(?) WHERE phone_number=(?)",(dob,phn))
    conn.commit()
    c.execute("UPDATE patients SET address=(?) WHERE phone_number=(?)",(address,phn))
    conn.commit()
    return render_template('home.html',mess='Updations Done Successfully!!!') 


if __name__ == '__main__':
    app.run(debug=True)
