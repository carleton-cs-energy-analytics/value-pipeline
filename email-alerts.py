import smtplib
from email.message import EmailMessage
import json
import requests
import datetime

BACKEND_URL = 'http://energycomps.its.carleton.edu:8080/api/'


def get_date():
    """
    Calculates what yesterday's date was using today's date (this is under the assumption we are
    sending it the next morning.

    :return: Yesterday's day as a string in the format year-month-day
    """
    current_date = datetime.datetime.now().date()
    # Change the int timedelta takes in to change how many days we want to subtract
    timedelta = datetime.timedelta(1)
    return str(current_date - timedelta)


def get_anomalous_rules():
    """
    Gets all the rules and then finds all the rules for which a value flagged that rule and puts it
    in a list

    :return: The list of rules that were broken yesterday
    """
    rules = requests.get(BACKEND_URL + 'rules').json()

    anomalous_rules = []
    for rule in rules:
        response = requests.get(BACKEND_URL + 'rule/' + str(rule['rule_id']) + '/count')
        # This is case where the values haven't been imported into the database yet.
        if response.status_code == 404:
            exit(1)

        num_anomalies = response.json()
        if num_anomalies > 0:
            rule['num_anomalies'] = num_anomalies
            anomalous_rules.append(rule)

    return anomalous_rules


def construct_msg_body():
    """
    Makes the body of the email sent to facilities. Lists out all the rules, the number of values
    that broke that rule, and the link to see the rule in greater context.

    :return: A string that will be the body of the email.
    """
    anomalous_rules = get_anomalous_rules()

    # This is the case were no anomalies were sent.
    if len(anomalous_rules) == 0:
        return ''

    msg_body = 'The rules broken yesterday, the number of values that flagged that rule, and the' \
               'link to view more are as follows.\n\n'
    for rule in anomalous_rules:
        print(str(rule))
        msg_body += rule['rule_name'] + ': ' + str(rule['num_anomalies']) + ' ' + str(
            rule['url']) + '\n'  # TODO: FIGURE OUT HOW TO GET THE DATE IN HERE

    return msg_body


def send_email(msg_body):
    """
    Sends the email if there is something in the body. The email is sent from the energy-comps email
    and to a google group with relevant people in facilities. (NOT CURRENTLY HOW IT IS DONE)

    :param msg_body: A string that will be the body of the email.
    """
    # In this case, no anomalies were found, so we should not send the email.
    if msg_body == '':
        return

    # Create a text/plain message
    msg = EmailMessage()
    msg['Subject'] = 'Anomalies detected on ' + get_date()  # Should probably make this better
    msg['From'] = 'grenche@carleton.edu'  # what address do we send from???
    msg['To'] = 'grenche@carleton.edu'  # what address do we send to???
    msg.set_content(msg_body)

    # Is this how we want to do it?
    server = smtplib.SMTP('smtp.carleton.edu', 587)
    server.starttls()
    server.login('grenche@carleton.edu', 'password')  # Don't worry. This is not my real password.
    server.send_message(msg)


def main():
    send_email(construct_msg_body())


if __name__ == '__main__':
    main()
