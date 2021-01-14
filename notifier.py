import urllib3
import time
import json
import boto3
from botocore.exceptions import ClientError
import logging

logging.basicConfig(filename='exec.log', level=logging.INFO)

SENDER = "Gabe Gutierrez <gegr93@gmail.com>"
RECIPIENTS = ["gegr93@gmail.com", "megwillett@comcast.net"]
AWS_REGION = "us-east-1"
SUBJECT = "COVID-19 Vaccine Seems to be Available on Vacstrac"
client = boto3.client('ses', region_name=AWS_REGION)

def send_email(payload):
    BODY_TEXT = "It's suspected that Harris County Public Health has vaccines available.\n" \
        "The received payload is as follows: " + str(payload) + "\n" \
        "Visit https://vacstrac.hctx.net to confirm.\n"
    try:
        logging.info('Attempting to send e-mail')
        response = client.send_email(
            Destination={'ToAddresses': RECIPIENTS},
            Message={
                'Body': {
                    'Text': {
                        'Charset': 'UTF-8',
                        'Data': BODY_TEXT
                    },
                    'Html': {
                        'Charset': 'UTF-8',
                        'Data': BODY_TEXT
                    }
                },
                    'Subject': {
                        'Charset': 'UTF-8',
                        'Data': SUBJECT
                    }
                },
            Source=SENDER
        )
        logging.info("Response: " + str(response))
    except ClientError as e:
        logging.error(e.response)

def check_status():
    logging.info("Checking status")
    http = urllib3.PoolManager()
    r = http.request('GET', 'https://secureapp.hcphtx.org/vaxwebapi/api/PatientVaccine/checkifregistrationisavailable')
    data = r.data.decode('UTF-8')
    payload = json.loads(data)
    logging.info("Response: " + str(payload))
    if payload['IsSuccess']:
        logging.info('Success')
        send_email(payload)



while True:
    logging.info('Running')
    check_status()
    logging.info('Sleeping')
    time.sleep(60)