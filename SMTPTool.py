import smtplib
from textblob import TextBlob
import os
import io
import re
import argparse
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime
import json
import RandomEmailGenerator
import email_object
import time
import math
import logging
import SendMail


def custom_join(list_of_strings, sep):
    strings = ''
    for string in list_of_strings:
        if (string is not None and string.strip() != ''):
            strings += string + sep

    # remove trailing char
    strings = strings.rstrip(sep)

    return strings


def replace_emaildomain(args, line):
    if (args.domain_name):
        if "@" in line:
            line = re.sub(r"(?<=@)[^.]+(?=\.)[^,]*", args.domain_name, line)
        else:
            line += "@" + args.domain_name
    return line


# mail_random_emails - mails randomized generated emails
def mail_random_emails(args):
    count = 0
    failed_count = 0
    server = None

    try:
        server = mail_connect(args)
    except smtplib.SMTPException:
        # retry
        server = mail_connect(args)

    if (server is None and not args.dryrun):
        print('Failed to connect to smtp server: ', args.serveraddr)
        return

    if (args.json_output_path is None):
        json_output_file = "emails_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".json"
    else:
        json_output_file = args.json_output_path

    random_emails_json = "["
    email_gtr = RandomEmailGenerator.EmailGenerator(
        addresses_file_path=args.addresses_file,
        attachments_dir_path=args.attachments_dir,
        text_model_file_path=args.text_model_file,
        domain_name=args.domain_name, args=args)

    attachmentLimit = 0

    if (args.attachment_percent < 0 or args.attachment_percent > 100):
        includeAttachments = 2
    elif (args.attachment_percent == 0):
        includeAttachments = 0
    else:
        includeAttachments = 1
        attachmentLimit = math.ceil(args.quanity * args.attachment_percent / 100)

    attachmentCount = 0

    for i in range(args.quantity):

        print("Sending " + str(i) + " th mail")
        logger.info("Sending " + str(i) + " th mail")

        random_email = None
        random_email = email_gtr.get_email(include_attachments=includeAttachments)

        msg = MIMEMultipart()

        userAccount = email_gtr.get_useraccount()
        msg['From'] = replace_emaildomain(args, random_email.sender[0])
        msg['Date'] = random_email.sent_date

        # Sequentially send all mails From all user accounts for the Current Group args.addresses_file

        # If subject is required to be translated from english, translate it
        if args.flag_lang != 'en':
            blob = TextBlob(str(random_email.subject[0]))
            print("Printing subject: ", blob.translate(to=args.flag_lang))
            msg['Subject'] = str(blob.translate(to=args.flag_lang))
        else:
            msg['Subject'] = random_email.subject[0]

        if random_email.to is None or len(random_email.to) == 0:
            msg['To'] = 'shouldnthappen@devtest-jb.com'
        elif len(random_email.to) > 1:
            msg['To'] = replace_emaildomain(args, custom_join(random_email.to, ', '))
        else:
            msg['To'] = random_email.to[0]

        print('From: ', msg['From'])
        print('To: ', msg['To'])

        if (random_email.cc is None or len(random_email.cc) == 0):
            msg['cc'] = ''
        elif len(random_email.cc) > 1:
            msg['cc'] = replace_emaildomain(args, custom_join(random_email.cc, ', '))
        else:
            msg['cc'] = random_email.cc[0]

        if (random_email.bcc is None or len(random_email.bcc) == 0):
            msg['bcc'] = ''
        elif len(random_email.bcc) > 1:
            msg['bcc'] = replace_emaildomain(args, custom_join(random_email.bcc, ', '))
        else:
            msg['bcc'] = random_email.bcc[0]

        if (random_email.body is None or len(random_email.body) == 0):
            msg.attach(MIMEText('This shouldn\'t happen but just in case.... \n'))
        elif len(random_email.body) > 1:

            # Translate the body if lang is not English
            if args.flag_lang != 'en':
                blob = TextBlob(str(random_email.body))
                print("Printing flag: ", args.flag_lang)
                print("Printing body: ", blob.translate(to=args.flag_lang))
                msg.attach(MIMEText(str(blob.translate(to=args.flag_lang)), 'plain', 'utf-8'))
            else:
                msg.attach(MIMEText(custom_join(random_email.body, '\n'), 'plain', 'utf-8'))
        else:
            msg.attach(MIMEText(random_email.body[0].encode('utf-8'), 'plain', 'utf-8'))

        if (attachmentLimit <= attachmentCount and includeAttachments < 2):
            random_email.b_attachments = None
            random_email.attachments = list()

        if (random_email.b_attachments == 1):
            attachmentCount = attachmentCount + 1

            for attachment in random_email.attachments:
                file_name = args.attachments_dir + attachment
                part = MIMEBase('application', "octet-stream")

                with open(file_name, "rb") as f:
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition',
                                    'attachment; filename="{0}"'.format(os.path.basename(file_name)))
                msg.attach(part)

        # output email obj json to later write to file
        if args.json_copy:
            random_emails_json += json.dumps(random_email, cls=email_object.ComplexEncoder, ensure_ascii=False) + ','
        print("Server: ", server)

        try:
            mail(server, args, msg)
            #server.sendmail('ishan.shinde@veritas.com', 'ishanshinde17@gmail.com', msg.as_string())
            print("Sent " + str(i) + " th mail")
            logger.info("Sent " + str(i) + " th mail")

        except Exception:
            # output failed email
            failed_email_file = "failedemails_" + datetime.now().strftime("%Y%m%d") + ".json"
            failed_email_json = json.dumps(random_email, cls=email_object.ComplexEncoder, ensure_ascii=False) + ','
            # should put this in consumable json format...
            with io.open(failed_email_file, "a+", encoding="utf8") as f:
                f.write(failed_email_json)
            failed_count = failed_count + 1

        count = count + 1
        if (count % 1000 == 0):
            print(str(count) + ' emails generated')

        if (args.json_copy and count % 100000 == 0):
            # remove trailing comma and write json to file
            with io.open(json_output_file, "a+", encoding="utf8") as f:
                f.write(random_emails_json)
            random_emails_json = ''

    if args.json_copy:
        random_emails_json = random_emails_json.rstrip(',') + "]"
        with io.open(json_output_file, "a+", encoding="utf8") as f:
            f.write(random_emails_json)

    mail_disconnect(args, server)
    if args.verbose:
        print("Attachment count: " + str(attachmentCount))
        print("Attachment Limit: " + str(attachmentLimit))

    print(str(count - failed_count) + ' emails successfully sent.')
    print(str(failed_count) + ' failed emails.')

    if (args.verbose and args.json_copy):
        print("Emails copied to: " + json_output_file)
        if (failed_count > 0):
            print("Failed emails copied to: " + failed_email_file)


def mail_random_emails_o365(args):
    print("Inside mail_random_emails")
    count = 0
    failed_count = 0
    server = None

    if (args.json_output_path is None):
        json_output_file = "emails_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".json"
    else:
        json_output_file = args.json_output_path

    random_emails_json = "["
    email_gtr = RandomEmailGenerator.EmailGenerator(
        addresses_file_path=args.addresses_file,
        attachments_dir_path=args.attachments_dir,
        text_model_file_path=args.text_model_file,
        domain_name=args.domain_name, args=args)

    email_gtr.loadO365UserAccounts(args.useraccounts_file)
    attachmentLimit = 0

    if (args.attachment_percent < 0 or args.attachment_percent > 100):
        includeAttachments = 2
    elif (args.attachment_percent == 0):
        includeAttachments = 0
    else:
        includeAttachments = 1
        attachmentLimit = math.ceil(args.quanity * args.attachment_percent / 100)

    attachmentCount = 0

    for i in range(args.quantity):

        userAccount = email_gtr.get_useraccount()

        args.SMTP_USER, args.SMTP_PASS = userAccount
        try:
            server = mail_connect(args)
        except smtplib.SMTPException:
            # retry
            server = mail_connect(args)

        if server is None and not args.dryrun:
            print('Failed to connect to smtp server: ', args.serveraddr)
            return

        print("Sending " + str(i) + " th mail")
        logger.info("Sending " + str(i) + " th mail")

        random_email = None
        random_email = email_gtr.get_email_o365(include_attachments=includeAttachments)

        msg = MIMEMultipart()


        msg['From'] = userAccount[0]
        msg['Date'] = random_email.sent_date

        # Sequentially send all mails From all user accounts for the Current Group args.addresses_file

        # If subject is required to be translated from english, translate it
        if args.flag_lang != 'en':
            blob = TextBlob(str(random_email.subject[0]))
            print("Printing subject: ", blob.translate(to=args.flag_lang))
            msg['Subject'] = str(blob.translate(to=args.flag_lang))
        else:
            msg['Subject'] = random_email.subject[0]


        msg['To'] = email_gtr.get_useraccount()[0]

        print('From: ', msg['From'])
        print('To: ', msg['To'])

        if (random_email.cc is None or len(random_email.cc) == 0):
            msg['cc'] = ''
        elif len(random_email.cc) > 1:
            msg['cc'] = replace_emaildomain(args, custom_join(random_email.cc, ', '))
        else:
            msg['cc'] = random_email.cc[0]

        if (random_email.bcc is None or len(random_email.bcc) == 0):
            msg['bcc'] = ''
        elif len(random_email.bcc) > 1:
            msg['bcc'] = replace_emaildomain(args, custom_join(random_email.bcc, ', '))
        else:
            msg['bcc'] = random_email.bcc[0]

        if (random_email.body is None or len(random_email.body) == 0):
            msg.attach(MIMEText('This shouldn\'t happen but just in case.... \n'))
        elif len(random_email.body) > 1:

            # Translate the body if lang is not English
            if args.flag_lang != 'en':
                blob = TextBlob(str(random_email.body))
                print("Printing flag: ", args.flag_lang)
                print("Printing body: ", blob.translate(to=args.flag_lang))
                msg.attach(MIMEText(str(blob.translate(to=args.flag_lang)), 'plain', 'utf-8'))
            else:
                msg.attach(MIMEText(custom_join(random_email.body, '\n'), 'plain', 'utf-8'))
        else:
            msg.attach(MIMEText(random_email.body[0].encode('utf-8'), 'plain', 'utf-8'))

        if (attachmentLimit <= attachmentCount and includeAttachments < 2):
            random_email.b_attachments = None
            random_email.attachments = list()

        if (random_email.b_attachments == 1):
            attachmentCount = attachmentCount + 1

            for attachment in random_email.attachments:
                file_name = args.attachments_dir + attachment
                part = MIMEBase('application', "octet-stream")

                with open(file_name, "rb") as f:
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition',
                                    'attachment; filename="{0}"'.format(os.path.basename(file_name)))
                msg.attach(part)

        # output email obj json to later write to file
        if args.json_copy:
            random_emails_json += json.dumps(random_email, cls=email_object.ComplexEncoder, ensure_ascii=False) + ','
        print("Server: ", server)

        try:
            #mail(server, args, msg)
            server.sendmail(userAccount[0], msg['To'], msg.as_string())
            print("Sent " + str(i) + " th mail")
            logger.info("Sent " + str(i) + " th mail")

        except Exception:
            # output failed email
            failed_email_file = "failedemails_" + datetime.now().strftime("%Y%m%d") + ".json"
            failed_email_json = json.dumps(random_email, cls=email_object.ComplexEncoder, ensure_ascii=False) + ','
            # should put this in consumable json format...
            with io.open(failed_email_file, "a+", encoding="utf8") as f:
                f.write(failed_email_json)
            failed_count = failed_count + 1

        count = count + 1
        if (count % 1000 == 0):
            print(str(count) + ' emails generated')

        if (args.json_copy and count % 100000 == 0):
            # remove trailing comma and write json to file
            with io.open(json_output_file, "a+", encoding="utf8") as f:
                f.write(random_emails_json)
            random_emails_json = ''

    if args.json_copy:
        random_emails_json = random_emails_json.rstrip(',') + "]"
        with io.open(json_output_file, "a+", encoding="utf8") as f:
            f.write(random_emails_json)

    mail_disconnect(args, server)
    if args.verbose:
        print("Attachment count: " + str(attachmentCount))
        print("Attachment Limit: " + str(attachmentLimit))

    print(str(count - failed_count) + ' emails successfully sent.')
    print(str(failed_count) + ' failed emails.')

    if (args.verbose and args.json_copy):
        print("Emails copied to: " + json_output_file)
        if (failed_count > 0):
            print("Failed emails copied to: " + failed_email_file)

def mail_random_emails_o365_1User(args):
    print('Inside 1 User')
    count = 0
    failed_count = 0
    server = None

    if (args.json_output_path is None):
        json_output_file = "emails_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".json"
    else:
        json_output_file = args.json_output_path

    random_emails_json = "["
    email_gtr = RandomEmailGenerator.EmailGenerator(
        addresses_file_path=args.addresses_file,
        attachments_dir_path=args.attachments_dir,
        text_model_file_path=args.text_model_file,
        domain_name=args.domain_name, args=args)

    email_gtr.loadO365UserAccounts(args.useraccounts_file)
    email_gtr.loadEmailAddresses(args.addresses_file)

    userAccount = email_gtr.get_useraccount()

    args.SMTP_USER, args.SMTP_PASS = userAccount
    try:
        server = mail_connect(args)
    except smtplib.SMTPException:
        # retry
        server = mail_connect(args)

    if server is None and not args.dryrun:
        print('Failed to connect to smtp server: ', args.serveraddr)
        return

    attachmentLimit = 0

    if (args.attachment_percent < 0 or args.attachment_percent > 100):
        includeAttachments = 2
    elif (args.attachment_percent == 0):
        includeAttachments = 0
    else:
        includeAttachments = 1
        attachmentLimit = math.ceil(args.quanity * args.attachment_percent / 100)

    attachmentCount = 0

    for i in range(args.quantity):

        print("Sending " + str(i) + " th mail")
        logger.info("Sending " + str(i) + " th mail")

        random_email = None
        random_email = email_gtr.get_email_o365(include_attachments=includeAttachments)

        msg = MIMEMultipart()

        msg['From'] = userAccount[0]
        msg['Date'] = random_email.sent_date

        # Sequentially send all mails From all user accounts for the Current Group args.addresses_file

        # If subject is required to be translated from english, translate it
        if args.flag_lang != 'en':
            blob = TextBlob(str(random_email.subject[0]))
            print("Printing subject: ", blob.translate(to=args.flag_lang))
            msg['Subject'] = str(blob.translate(to=args.flag_lang))
        else:
            msg['Subject'] = random_email.subject[0]


        msg['To'] = random_email.to[0]

        print('From: ', msg['From'])
        print('To: ', msg['To'])

        if (random_email.cc is None or len(random_email.cc) == 0):
            msg['cc'] = ''
        elif len(random_email.cc) > 1:
            msg['cc'] = replace_emaildomain(args, custom_join(random_email.cc, ', '))
        else:
            msg['cc'] = random_email.cc[0]

        if (random_email.bcc is None or len(random_email.bcc) == 0):
            msg['bcc'] = ''
        elif len(random_email.bcc) > 1:
            msg['bcc'] = replace_emaildomain(args, custom_join(random_email.bcc, ', '))
        else:
            msg['bcc'] = random_email.bcc[0]

        if (random_email.body is None or len(random_email.body) == 0):
            msg.attach(MIMEText('This shouldn\'t happen but just in case.... \n'))
        elif len(random_email.body) > 1:

            # Translate the body if lang is not English
            if args.flag_lang != 'en':
                blob = TextBlob(str(random_email.body))
                print("Printing flag: ", args.flag_lang)
                print("Printing body: ", blob.translate(to=args.flag_lang))
                msg.attach(MIMEText(str(blob.translate(to=args.flag_lang)), 'plain', 'utf-8'))
            else:
                msg.attach(MIMEText(custom_join(random_email.body, '\n'), 'plain', 'utf-8'))
        else:
            msg.attach(MIMEText(random_email.body[0].encode('utf-8'), 'plain', 'utf-8'))

        if (attachmentLimit <= attachmentCount and includeAttachments < 2):
            random_email.b_attachments = None
            random_email.attachments = list()

        if (random_email.b_attachments == 1):
            attachmentCount = attachmentCount + 1

            for attachment in random_email.attachments:
                file_name = args.attachments_dir + attachment
                part = MIMEBase('application', "octet-stream")

                with open(file_name, "rb") as f:
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition',
                                    'attachment; filename="{0}"'.format(os.path.basename(file_name)))
                msg.attach(part)

        # output email obj json to later write to file
        if args.json_copy:
            random_emails_json += json.dumps(random_email, cls=email_object.ComplexEncoder, ensure_ascii=False) + ','
        print("Server: ", server)

        try:
            #mail(server, args, msg)
            server.sendmail(userAccount[0], msg['To'], msg.as_string())
            print("Sent " + str(i) + " th mail")
            logger.info("Sent " + str(i) + " th mail")

        except Exception:
            # output failed email
            failed_email_file = "failedemails_" + datetime.now().strftime("%Y%m%d") + ".json"
            failed_email_json = json.dumps(random_email, cls=email_object.ComplexEncoder, ensure_ascii=False) + ','
            # should put this in consumable json format...
            with io.open(failed_email_file, "a+", encoding="utf8") as f:
                f.write(failed_email_json)
            failed_count = failed_count + 1

        count = count + 1
        if (count % 1000 == 0):
            print(str(count) + ' emails generated')

        if (args.json_copy and count % 100000 == 0):
            # remove trailing comma and write json to file
            with io.open(json_output_file, "a+", encoding="utf8") as f:
                f.write(random_emails_json)
            random_emails_json = ''

    if args.json_copy:
        random_emails_json = random_emails_json.rstrip(',') + "]"
        with io.open(json_output_file, "a+", encoding="utf8") as f:
            f.write(random_emails_json)

    mail_disconnect(args, server)
    if args.verbose:
        print("Attachment count: " + str(attachmentCount))
        print("Attachment Limit: " + str(attachmentLimit))

    print(str(count - failed_count) + ' emails successfully sent.')
    print(str(failed_count) + ' failed emails.')

    if (args.verbose and args.json_copy):
        print("Emails copied to: " + json_output_file)
        if (failed_count > 0):
            print("Failed emails copied to: " + failed_email_file)
# mail_input_emails - mails emails from an given json file
def mail_input_emails(args):
    count = 0
    failed_count = 0
    server = None

    with io.open(args.json_input, "r", encoding="utf8") as f:
        emails_json = f.read()

    try:
        server = mail_connect(args)
    except smtplib.SMTPException:
        # retry
        server = mail_connect(args)

    if (server is None and not args.dryrun):
        print('Failed to connect to smtp server: ', args.serveraddr)
        return

    emails_input = json.loads(emails_json, encoding="utf8")
    for em in emails_input:
        try:
            msg = MIMEMultipart()
            msg['From'] = replace_emaildomain(args, em['sender'])
            msg['Date'] = em['sentdate']

            # If subject is required to be translated from english, translate it
            if args.flag_lang != 'en':
                blob = TextBlob(str(em['subject']))
                msg['Subject'] = str(blob.translate(to=args.flag_lang))
            else:
                msg['Subject'] = em['subject']

            if (em['to'] is None or len(em['to']) == 0):
                msg['To'] = 'shouldnthappen@devtest-jb.com'
            elif len(em['to']) > 1:
                msg['To'] = replace_emaildomain(args, custom_join(em['to'], ', '))
            else:
                msg['To'] = replace_emaildomain(args, em['to'][0])

            if (em['cc'] is None or len(em['cc']) == 0):
                msg['cc'] = ''
            elif len(em['cc']) > 1:
                msg['cc'] = replace_emaildomain(args, custom_join(em['cc'], ', '))
            elif len(em['cc']) == 1:
                msg['cc'] = replace_emaildomain(args, em['cc'][0])

            if (em['bcc'] is None or len(em['bcc']) == 0):
                msg['bcc'] = ''
            elif len(em['bcc']) > 1:
                msg['bcc'] = replace_emaildomain(args, custom_join(em['bcc'], ', '))
            elif len(em['bcc']) == 1:
                msg['bcc'] = replace_emaildomain(args, em['bcc'][0])

            # Working with the body
            if (em['body'] is None or len(em['body']) == 0):

                # Translate the body if lang is not English
                if args.flag_lang != 'en':
                    blob = TextBlob('This shouldnt happen, but just in case...')
                    msg.attach(MIMEText(str(blob.translate(to=args.flag_lang))))
                else:
                    msg.attach(MIMEText('This shouldnt happen, but just in case...'))
            elif len(em['body']) > 1:

                # Translate the body if lang is not English
                if args.flag_lang != 'en':
                    blob = TextBlob(str(em['body']))
                    msg.attach(MIMEText(str(blob.translate(to=args.flag_lang)), 'plain', 'utf-8'))
                else:
                    msg.attach(MIMEText(custom_join(em['body'], '\n').encode('utf-8'), 'plain', 'utf-8'))

            else:
                msg.attach(MIMEText(em['body'][0].encode('utf-8'), 'plain', 'utf-8'))

            if em['attachments'] is not None:
                for attachment in em['attachments']:
                    file_name = args.attachments_dir + attachment
                    part = MIMEBase('application', "octet-stream")

                    with open(file_name, "rb") as f:
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 'attachment; filename="{0}"'
                                        .format(os.path.basename(file_name).encode('utf-8')))
                    msg.attach(part)

            # if args.verbose:
            #    print(msg)

            mail(server, args, msg)
        except Exception as e:
            print(e)
            # output failed email
            failed_email_file = "failedemails_" + datetime.now().strftime("%Y%m%d") + ".json"
            failed_email_json = json.dumps(em, cls=email_object.ComplexEncoder) + ','
            # should put this in consumable json format...
            with io.open(failed_email_file, "a+", encoding="utf8") as f:
                f.write(failed_email_json)
            failed_count = failed_count + 1

        count = count + 1
        time.sleep(0.01)
        if (count % 1000 == 0):
            # sleep for 3 secs, don't want to overload smtp server
            time.sleep(3)
            print(str(count) + ' emails sent...')

    mail_disconnect(args, server)
    print(str(count - failed_count) + ' emails successfully sent.')
    print(str(failed_count) + ' failed emails.')


def mail_connect(args):
    server = None
    if args.o365:
        print('Printing MailConnect %s', args.serveraddr)
        server = smtplib.SMTP(args.serveraddr, args.serverport)

        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(args.SMTP_USER, args.SMTP_PASS)

    else:
        if args.usessl:
            server = smtplib.SMTP_SSL()
        else:
            server = smtplib.SMTP()

        if not args.dryrun:
            server.set_debuglevel(args.debuglevel)
            server.connect(args.serveraddr, args.serverport)
            if args.usetls: server.starttls()
            if args.SMTP_USER != "": server.login(args.SMTP_USER, args.SMTP_PASS)

    return server


def mail_disconnect(args, server):
    if not args.dryrun:
        server.quit()


def mail(server, args, msg):
    if not args.dryrun:
        try:
            # If Exchange is used to send mail
            if args.exc:
                server.sendmail(msg['From'], msg['To'], msg.as_string())
            # Else if Mail Server is used to send mail
            elif args.o365:
                print('In O365')
                server.sendmail('ishan.shinde@veritas.com','ishanshinde17@gmail.com', msg.as_string())
            else:
                print('In SMTP')
                server.sendmail(args.addresses[0], args.addresses[1], msg.as_string())
        except smtplib.SMTPException:
            raise Exception('Failed to send email!')

    return server


def main():
    usage = "%(prog)s [args] serveraddress"
    parser = argparse.ArgumentParser(usage=usage)

    # Setting the defaults
    parser.set_defaults(usetls=False)
    parser.set_defaults(usessl=False)
    parser.set_defaults(serverport=587)
    parser.set_defaults(SMTP_USER="")
    parser.set_defaults(SMTP_PASS="")
    parser.set_defaults(debuglevel=0)
    parser.set_defaults(verbose=False)
    parser.set_defaults(quantity=1)
    parser.set_defaults(dryrun=False)
    parser.set_defaults(json_copy=False)
    parser.set_defaults(json_input="")
    parser.set_defaults(json_output_path=None)
    parser.set_defaults(attachment_percent=-1)
    parser.set_defaults(smtp_addresses_file="./Content/SMTPemailaddresses.txt")
    parser.set_defaults(exchange_addresses_file="./Content/Exchangeemailaddresses.txt")
    parser.set_defaults(o365exchange_useraccounts_file="Content/UserAccounts.xlsx")
    parser.set_defaults(o365exchange_addresses_file="Content/emailaddresses.txt")
    parser.set_defaults(attachments_dir=u"./Content/Attachments/")
    parser.set_defaults(text_model_file="./Content/news_articles.txt")
    parser.set_defaults(domain_name=None)
    parser.set_defaults(fromaddr="")
    parser.set_defaults(toaddr="")
    parser.set_defaults(serveraddr="")

    # Adding positional Arguments
    parser.add_argument("serveraddr", help="SMTP/Exchange Server")

    # Adding optional arguments
    parser.add_argument("-t", "--usetls", action="store_true", dest="usetls", default=False,
                        help="Connect using TLS, default is false")
    parser.add_argument("-s", "--usessl", action="store_true", dest="usessl", default=False,
                        help="Connect using SSL, default is false")
    parser.add_argument("-n", "--port", action="store", type=int, dest="serverport", help="SMTP server port",
                        metavar="nnn")
    parser.add_argument("-u", "--username", action="store", type=str, dest="SMTP_USER",
                        help="SMTP server auth username", metavar="username")
    parser.add_argument("-p", "--password", action="store", type=str, dest="SMTP_PASS",
                        help="SMTP server auth password", metavar="password")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=False,
                        help="Verbose message printing")
    parser.add_argument("-l", "--debuglevel", type=int, dest="debuglevel",
                        help="Set to 1 to print smtplib.send messages", metavar="n")
    parser.add_argument("-q", "--quantity", type=int, dest="quantity", help="Number of emails to be generated",
                        metavar="n")
    parser.add_argument("-r", "--dryrun", action="store_true", dest="dryrun",
                        help="Execute script without sending email")
    parser.add_argument("-i", "--jsoninput", action="store", type=str, dest="json_input",
                        help="Sends emails from json file", metavar="filepath")
    parser.add_argument("-j", "--jsonoutput", action="store_true", dest="json_copy",
                        help="Copies emails to json file for email data ingestion")
    parser.add_argument("-c", "--attachmentpercent", type=int, dest="attachment_percent",
                        help="Int value for percentage of emails to include attachments", metavar="n")
    parser.add_argument("-f", "--addressesfile", action="store", type=str, dest="addresses_file",
                        help="Email addresses to use for generated emails", metavar="filepath")
    parser.add_argument("-a", "--attachmentsdir", action="store", type=str, dest="attachments_dir",
                        help="Attachments to use for generated emails", metavar="filepath")
    parser.add_argument("-x", "--textmodelfile", action="store", type=str, dest="text_model_file",
                        help="Input text to use for generated subject and body of emails", metavar="filepath")

    parser.add_argument("-m", "--smtp", nargs=2, dest="addresses", help="Use Mail Server for mail transfer",
                        metavar="addresses")
    parser.add_argument("-e", "--exchange", action="store_true", dest="exc", default=False,
                        help="Use Exchange for mail transfer")
    parser.add_argument("-o", "--o365", action="store_true", dest="o365", default=False,
                        help="Use o365 Exchange for mail transfer")
    parser.add_argument("-g", "--lang", action="store", dest="language", default="english", metavar="language",
                        help="language for generating body and subject of mail")

    parser.add_argument("--one", action="store_true", dest="oneAccount", default=False,
                        help="Use only one o365 account from  UserAccounts to send mails")

    args = parser.parse_args()

    # Check if atleast one of Exchange Server or Mail Server is provided
    if args.addresses is None and args.exc is False and args.o365 is False:
        print("Atleast one of Exchange, Mail Server or O365 should be selected")
        return

    # If Exchange is used to send mail, and external file is not provided, use Exchangeemailaddresses.txt
    if args.exc:
        if args.addresses_file is None:
            args.addresses_file = args.exchange_addresses_file
    # If Mail Server is used to send mail, and external file is not provided, use SMTPemailaddresses.txt
    elif args.addresses:
        if args.addresses_file is None:
            args.addresses_file = args.smtp_addresses_file
    # If O365 Exchange Server is used to send mail, and external file is not provided, use O365Exchangeemailaddresses.txt
    elif args.o365:
        if args.addresses_file is None:
            args.useraccounts_file = args.o365exchange_useraccounts_file
            args.addresses_file = args.o365exchange_addresses_file

    # Setting the language flag for the language chosen for subject and body
    if str(args.language).lower() == 'english':
        args.flag_lang = 'en'
    elif str(args.language).lower() == 'japanese':
        args.flag_lang = 'ja'
    elif str(args.language).lower() == 'french':
        args.flag_lang = 'fr'
    elif str(args.language).lower() == 'german':
        args.flag_lang = 'de'

    if args.verbose:
        print('usetls             : ', args.usetls)
        print('usessl             : ', args.usessl)
        print('server address     : ', args.serveraddr)
        print('server port        : ', args.serverport)
        print('envelope sender    : ', args.fromaddr)
        print('envelope recipient : ', args.toaddr)
        print('smtp username      : ', args.SMTP_USER)
        print('smtplib debuglevel : ', args.debuglevel)
        print('dryrun             : ', args.dryrun)
        print('json copy          : ', args.json_copy)
        print('json input         : ', args.json_input)
        print('json output        : ', args.json_output_path)
        if not args.json_input:
            print('# of emails        : ', str(args.quantity))
        if args.attachment_percent > 0:
            print('   w/ attachments  : ', str(math.ceil(args.quantity * args.attachment_percent / 100)))
        print('SMTPaddresses filepath   : ', args.smtp_addresses_file)
        print('Exchangeaddresses filepath   : ', args.exchange_addresses_file)
        print('Externaladdresses filepath   : ', args.addresses_file)
        print('attachments dirpath  : ', args.attachments_dir)
        print('text model filepath  : ', args.text_model_file)
        print('domain name        : ', args.domain_name)
        print('language for subject and body: ', args.language)

        print('Generating ' + str(args.quantity) + ' emails...')
        if args.oneAccount:
            mail_random_emails_o365_1User(args)
        else:
            mail_random_emails_o365(args)


if __name__ == "__main__":
    logger = logging.getLogger('my_app')
    main()