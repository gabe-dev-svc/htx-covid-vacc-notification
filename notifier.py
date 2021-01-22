import urllib3
import time
import json
import boto3
from botocore.exceptions import ClientError
import logging
import sys
import random

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

SENDER = "Gabe Gutierrez <gegr93@gmail.com>"
RECIPIENTS = ["gegr93@gmail.com", "ryan.gonzalez064@gmail.com"]
AWS_REGION = "us-east-1"
SUBJECT = "COVID-19 Vaccine Seems to be Available on Vacstrac"
client = boto3.client('ses', region_name=AWS_REGION)

def alert_exception(payload):
    BODY_TEXT = "The COVID notification application is failing: " + payload
    try:
        logger.info('Attempting to send e-mail')
        response = client.send_email(
            Destination={'ToAddresses': ['gegr93@gmail.com']},
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
                        'Data': 'COVID Notification Application failing'
                    }
                },
            Source=SENDER
        )
        logger.info("Sent allert successfully")
    except ClientError as e:
        logger.error("Error encountered sending e-mail")
        logger.error(e.response)
    


def send_email(payload):
    BODY_TEXT = "It's suspected that Harris County Public Health has vaccines available.\n" \
        "The received payload is as follows: " + str(payload) + "\n" \
        "Visit https://vacstrac.hctx.net to confirm.\n"
    try:
        logger.info('Attempting to send e-mail')
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
        logger.info("Sent notification successfully")
    except ClientError as e:
        logger.error("Error encountered sending e-mail")
        logger.error(e.response)
    

def check_status():
    http = urllib3.PoolManager()
    r = http.request('GET', 'https://secureapp.hcphtx.org/vaxwebapi/api/PatientVaccine/checkifregistrationisavailable')
    data = r.data.decode('UTF-8')
    payload = json.loads(data)
    if payload['IsSuccess']:
        logger.info('Success!')
        send_email(payload)
        return random.randint(300,400)
    else:
        logger.info('No luck')
        return random.randint(60,180)



while True:
    logger.info('Starting service')
    try:
        sleep_time = check_status()
    except Exception as e:
        sleep_time = 120
        logger.error(e)
        payload = str(e)
        try:
            alert_exception(payload)
        except Exception as ex:
            logger.error("Failed to send alert: " + str(ex))
        
    logger.info('Sleeping %s seconds' % str(sleep_time))
    time.sleep(sleep_time)