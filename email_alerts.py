"""
    email_alerts.py
    Eva Grench, 22 February  2018

    Sends an html email from the server with a table of all the rules that had anomalous values, the
    number of anomalous values under that rule, and a link to view the results on the anomalies
    dashboard. It is sent to a google group.
"""

import os
from email.mime.text import MIMEText
from email.message import EmailMessage
import requests
import datetime
import time

BACKEND_URL = os.environ.get("BASE_URL") or 'http://energycomps.its.carleton.edu/api/'
FRONTEND_URL = 'http://energycomps.its.carleton.edu/'
TO_EMAIL = os.environ.get("TO_EMAIL") or 'energy-analytics.group@carleton.edu'


def get_date(num_days_before_today):
    """
    Calculates what yesterday's date was using today's date (this is under the assumption we are
    sending it the next morning.

    :return: Yesterday's day as a string in the format year-month-day
    """
    current_date = datetime.datetime.now().date()
    # Change the int timedelta takes in to change how many days we want to subtract
    timedelta = datetime.timedelta(num_days_before_today)
    return str(current_date - timedelta)


def get_date_url():
    """
    Encodes the date range so that when the user clicks the link they are taken to the relevant
    results page. Currently this is manually done which is not great, but is because they do it
    differently in Python.

    :return: The (javascript style) encoded date range as a string
    """
    current_time = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Change the int timedelta takes in to change how many days we want to subtract
    timedelta = datetime.timedelta(days=1)

    start_date = str(int(time.mktime((current_time - timedelta).timetuple())) * 1000)
    end_date = str(int(time.mktime((current_time).timetuple())) * 1000)

    date_as_javascript_ecoded_url = '&date_range%5BstartDate%5D=' + start_date +\
                                    '&date_range%5BendDate%5D=' + end_date

    return date_as_javascript_ecoded_url


def get_anomalous_rules():
    """
    Gets all the rules and then finds all the rules for which a value flagged that rule and puts it
    in a list.

    :return: The list of rules that were broken yesterday
    """
    rules = requests.get(BACKEND_URL + 'rules').json()

    anomalous_rules = []
    for rule in rules:
        response = requests.get(BACKEND_URL + 'rule/' + str(rule['rule_id']) + '/count')
        # This is case where the values haven't been imported into the database yet.
        if response.status_code == 404:
            exit(1)

        # Error on the backend, so we will tell them that there was an error.
        if response.status_code == 500:
            rule['num_anomalies'] = 0
            anomalous_rules.append(rule)
            break

        num_anomalies = response.json()
        if num_anomalies > 0:
            rule['num_anomalies'] = num_anomalies
            anomalous_rules.append(rule)

    return anomalous_rules


def construct_anomalies_table(anomalous_rules):
    """
    Gets all the relevant information for constructing the table in the message by getting the rule
    name, count, and link for each rule.

    :param anomalous_rules: The list of rules that actually have anomalies associated with them.
    :return: The html codes that will be the table (and main sources of information) in the email.
    """
    anomalies_table = ''
    for rule in anomalous_rules:
        anomalies_table += '<tr>\n<td>' + rule['rule_name'] + '</td>'
        if rule['num_anomalies'] == 0:
            anomalies_table += '<td>Error occurred in the database</td>'
        else:
            anomalies_table += '<td>' + str(rule['num_anomalies']) + '</td> '

        url = FRONTEND_URL[:-1] + str(rule['url']) + get_date_url()
        link = '<td><a href="' + url + '">view more</a></td>'

        anomalies_table += link + '</tr>\n'

    return anomalies_table


def construct_msg_body_as_html():
    """
    Makes the body of the email sent to facilities. Lists out all the rules, the number of values
    that broke that rule, and the link to see the rule in greater context.

    :return: A string that will be the body of the email.
    """
    anomalous_rules = get_anomalous_rules()

    # This is the case were no anomalies were sent.
    if len(anomalous_rules) == 0:
        return ''

    anomalies_table = construct_anomalies_table(anomalous_rules)

    html = """
        <html>
          <head></head>
          <body>
            <p>The rules broken yesterday, the number of values that flagged that rule, and the link
             to view more are as follows.<br><br>
             <table border="1" cellspacing="0" cellpadding="5">
                <tr>
                    <th>Rule Name</th>
                    <th>Number of Anomalous Values</th>
                    <th>Link to Dashboard</th>
                </tr>
                {code}
             </table>
            </p>
          </body>
        </html>
        """.format(code=anomalies_table)

    html_email = MIMEText(html, 'html')

    return html_email


def send_email(msg_body):
    """
    Sends the email if there is something in the body. The email is sent from the energy-comps email
    and to a google group with relevant people in facilities. (NOT CURRENTLY HOW IT IS DONE)

    :param msg_body: A string that will be the body of the email.
    """
    # In this case, no anomalies were found, so we should not send the email.
    if msg_body == '':
        print('No email was sent because there were no anomalies.')
        return

    message = EmailMessage()
    message['Subject'] = 'Anomalies detected on ' + get_date(1)
    message.set_content(msg_body)

    # pipe the mail to sendmail
    sendmail = os.popen('/usr/sbin/sendmail ' + TO_EMAIL, 'w')
    sendmail.write(message.as_string())

    if sendmail.close() is not None:
        print('Error: Failed to send email.')


def main():
    send_email(construct_msg_body_as_html())


if __name__ == '__main__':
    main()
