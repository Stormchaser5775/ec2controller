from flask import Flask, request, jsonify
from flask_apscheduler import APScheduler
from flask_cors import CORS, cross_origin
import boto3
import random
import time
import smtplib, ssl

# session = boto3.Session(
#     aws_access_key_id='YOUR_ACCESS_KEY',
#     aws_secret_access_key='YOUR_SECRET_KEY',
#     region_name='YOUR_REGION'
# )

app = Flask(__name__)

cors = CORS(app)

scheduler = APScheduler()

otp = {}
app.config['CORS_HEADERS'] = 'Content-Type'
rds = boto3.client('rds')
ec2 = boto3.client('ec2')

emailList = ["aptachu@gmail.com"]
active = ["14.97.224.242", "180.151.61.70"]
activeE = {"14.97.224.242": "aptachu@gmail.com", "180.151.61.70": "aptachu@gmail.com"}
loginUrl = "pass.html"
ec2Url = "UI.html"
timee = 21;

def emailOtp(otp, recEmail):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "testtmailbot@gmail.com"
    receiver_email = recEmail
    password = "rzkk ezgi iztm udyj"
    message = f"""\
Subject: OTP

your OTP is {otp}"""
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
    print(otp)

@app.route('/status', methods=['POST'])
@cross_origin()
def status_change():
    data = request.json
    if data == None:
        data = {}
    receiver_email = activeE[data['ip']]
    time.sleep(3)
    response = ec2.describe_instances()
    status = response['Reservations'][data['num']]['Instances'][0]['State']['Name']
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "testtmailbot@gmail.com"
    password = "rzkk ezgi iztm udyj"
    while True:
        response = ec2.describe_instances()
        status = response['Reservations'][data['num']]['Instances'][0]['State']['Name']
        if status == 'pending' or status == 'stopping':
            message = f"""\
Subject: Status change of {data['id']}

A status change of the EC2 instance {data['id']} has been initiated. The instance is {status}."""
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)
            return jsonify("done")
        elif status != 'pending' and status != 'stopping' and status != 'running' and status != "stopped":
            message = f"""\
Subject: Error

The status change of the EC2 instance {data['id']} resulted in an error"""
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)
            return jsonify("done")

@app.route('/email', methods=['POST'])
@cross_origin()
def email():
    data = request.json
    if data == None:
        data = {}
    response = ec2.describe_instances()
    initial = response['Reservations'][data['num']]['Instances'][0]['State']['Name']
    receiver_email = activeE[data['ip']]
    time.sleep(3)
    while True:
        response = ec2.describe_instances()
        status = response['Reservations'][data['num']]['Instances'][0]['State']['Name']

        if (status == 'running' or status == "stopped") and status != initial:
            port = 465  # For SSL
            smtp_server = "smtp.gmail.com"
            sender_email = "testtmailbot@gmail.com"
            password = "rzkk ezgi iztm udyj"
            message = f"""\
Subject: Status change of {data['id']}

The EC2 instance {data['id']} has been {data['status']}."""
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)
            return jsonify("done")
        else:
            time.sleep(5)
            if status != 'pending' and status != 'stopping' and status != 'running' and status != "stopped":
                port = 465  # For SSL
                smtp_server = "smtp.gmail.com"
                sender_email = "testtmailbot@gmail.com"
                password = "rzkk ezgi iztm udyj"
                message = f"""\
Subject: Error or Timeout

The status change of the EC2 instance {data['id']} resulted in an error."""
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                    server.login(sender_email, password)
                    server.sendmail(sender_email, receiver_email, message)
                return jsonify("done")



@app.route('/start', methods=['POST'])
@cross_origin()
def start():
    data = request.json
    if data == None:
        data = {}
    start_response = ec2.start_instances(InstanceIds=[data["id"]])
    return jsonify("done")

@app.route('/stop', methods=['POST'])
@cross_origin()
def stop():
    data = request.json
    if data == None:
        data = {}
    stop_response = ec2.stop_instances(InstanceIds=[data["id"]])
    return jsonify("done")

@app.route('/otp', methods=['POST'])
@cross_origin()
def genOtp():
    data = request.json
    if data == None:
        data = {}
    global otp
    otp[data['recEmail']] = random.randrange(10000, 100000)
    if data['recEmail'] in emailList:
        emailOtp(otp[data['recEmail']], data['recEmail'])
    return jsonify("done")

@app.route('/check', methods=['POST'])
@cross_origin()
def check():
    data = request.json
    if data == None:
        data = {}
    global otp, active
    if int(data['pwd']) == otp[data['email']]:
        otp[data['email']] = random.randrange(10000, 100000)
        active.append(data['ip'])
        activeE[data['ip']] = data['email']
        print(active)
        return jsonify('window.location=' + f"'{ec2Url}'")
    return jsonify('window.location=' + f"'{loginUrl}'")

@app.route('/confirm', methods=['POST'])
@cross_origin()
def confirm():
    data = request.json
    if data == None:
        data = {}
    global active
    if data['ip'] in active:
        return jsonify(True)
    return jsonify(False)

@app.route('/listOinst', methods=['POST'])
@cross_origin()
def listOinst():
    response = ec2.describe_instances()
    listOinsts = {}
    for i in range(len(response['Reservations'])):
        listOinsts[i] = response['Reservations'][i]['Instances'][0]['InstanceId']
    return listOinsts

@app.route('/listOnames', methods=['POST'])
@cross_origin()
def listOnames():
    response = ec2.describe_instances()
    listOnames = {}
    for i in range(len(response['Reservations'])):
        listOnames[i] = response['Reservations'][i]['Instances'][0]['Tags'][0]['Value']
    return listOnames

@app.route('/statusi', methods=['POST'])
@cross_origin()
def statusi():
    response = ec2.describe_instances()
    statusi = {}
    for i in range(len(response['Reservations'])):
        statusi[i] = response['Reservations'][i]['Instances'][0]['State']['Name']
    return statusi

@app.route('/logOut', methods=['POST'])
@cross_origin()
def logOut():
    data = request.json
    if data == None:
        data = {}
    active.remove(data['ip'])
    activeE.pop(data['ip'])
    return jsonify('window.location=' + f"'{loginUrl}'")

@app.route('/rdsstatus', methods=['POST'])
@cross_origin()
def rds_status_change():
    data = request.json
    if data == None:
        data = {}
    receiver_email = activeE[data['ip']]
    time.sleep(30)
    response = rds.describe_db_clusters()
    status = response['DBClusters'][data['num']]['Status']
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "testtmailbot@gmail.com"
    password = "rzkk ezgi iztm udyj"
    while True:
        response = rds.describe_db_clusters()
        status = response['DBClusters'][data['num']]['Status']
        if status == 'starting' or status == 'stopping':
            message = f"""\
Subject: Status change of {data['id']}

A status change of the RDS instance {data['id']} has been initiated. The instance is {status}."""
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)
            return jsonify("done")
        elif status != 'starting' and status != 'stopping' and status != 'available' and status != "stopped":
            message = f"""\
Subject: Error

The status change of the RDS instance {data['id']} resulted in an error"""
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)
            return jsonify("done")
        else:
            time.sleep(5);

@app.route('/rdsemail', methods=['POST'])
@cross_origin()
def rds_email():
    data = request.json
    if data == None:
        data = {}
    receiver_email = activeE[data['ip']]
    response = rds.describe_db_clusters()
    initial = response['DBClusters'][data['num']]['Status']
    time.sleep(30)
    while True:
        response = rds.describe_db_clusters()
        status = response['DBClusters'][data['num']]['Status']

        if (status == 'available' or status == "stopped") and (status != initial):
            port = 465  # For SSL
            smtp_server = "smtp.gmail.com"
            sender_email = "testtmailbot@gmail.com"
            password = "rzkk ezgi iztm udyj"
            message = f"""\
Subject: Status change of {data['id']}

The RDS instance {data['id']} has been {data['status']}."""
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)
            return jsonify("done")
        else:
            time.sleep(5)
            if status != 'starting' and status != 'stopping' and status != 'available' and status != "stopped":
                port = 465  # For SSL
                smtp_server = "smtp.gmail.com"
                sender_email = "testtmailbot@gmail.com"
                password = "rzkk ezgi iztm udyj"
                message = f"""\
Subject: Error

The status change of the RDS instance {data['id']} resulted in an error."""
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                    server.login(sender_email, password)
                    server.sendmail(sender_email, receiver_email, message)
                return jsonify("done")



@app.route('/rdsstart', methods=['POST'])
@cross_origin()
def rdsstart():
    data = request.json
    if data == None:
        data = {}
    start_response = rds.start_db_cluster(DBClusterIdentifier=data["id"])
    return jsonify("done")

@app.route('/rdsstop', methods=['POST'])
@cross_origin()
def rdsstop():
    data = request.json
    if data == None:
        data = {}
    stop_response = rds.stop_db_cluster(DBClusterIdentifier=data["id"])
    return jsonify("done")

@app.route('/rdslistOinst', methods=['POST'])
@cross_origin()
def rds_listOinst():
    response = rds.describe_db_clusters()
    listOinsts = {}
    for i in range(len(response['DBClusters'])):
        listOinsts[i] = response['DBClusters'][i]['DBClusterIdentifier']
    return listOinsts

@app.route('/rdsstatusi', methods=['POST'])
@cross_origin()
def rdsstatusi():
    response = rds.describe_db_clusters()
    statusi = {}
    for i in range(len(response['DBClusters'])):
        statusi[i] = response['DBClusters'][i]['Status']
    return statusi


@app.route('/setTime', methods=['POST'])
@cross_origin()
def setTimee():
    data = request.json
    if data == None:
        data = {}
    global timee
    if (int(data["time"]) <= 23) and (int(data["time"]) >= 0):
        timee = int(data["time"])
    return jsonify(timee)

@app.route('/Timee', methods=['POST'])
@cross_origin()
def timeee():
    return jsonify(timee)

@scheduler.task('cron', id='do_job', hour=timee)
def stopEc2():
    response = ec2.describe_instances()
    listOinsts = {}
    for i in range(len(response['Reservations'])):
        listOinsts[i] = response['Reservations'][i]['Instances'][0]['InstanceId']
    stop_response = ec2.stop_instances(InstanceIds=list(listOinsts.values()))

@scheduler.task('cron', id='do_job', hour=timee)
def stopRds():
    response = ec2.describe_instances()
    listOinsts = {}
    for i in range(len(response['DBClusters'])):
        listOinsts[i] = response['DBClusters'][i]['DBClusterIdentifier']
    dbs = list(listOinsts.values())
    for i in dbs:
        stop_response = rds.stop_db_cluster(DBClusterIdentifier=i)



@scheduler.task('interval', id='do_job_1', hours=1)
def signOutAll():
    global active, acitveE
    active = []
    activeE = {}

if __name__ == '__main__':
    scheduler.init_app(app)
    scheduler.start()
    app.run(debug=True)
