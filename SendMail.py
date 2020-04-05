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
import random


def mail_sequential_emails(args):
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
        domain_name=args.domain_name)

    attachmentLimit = 0

    if (args.attachment_percent < 0 or args.attachment_percent > 100):
        includeAttachments = 2
    elif (args.attachment_percent == 0):
        includeAttachments = 0
    else:
        includeAttachments = 1
        attachmentLimit = math.ceil(args.quanity * args.attachment_percent / 100)

    attachmentCount = 0

    # msg['From'] = replace_emaildomain(args, random_email.sender[0])
    # msg['Date'] = random_email.sent_date

    inputFile = open(args.addresses_file, 'r', encoding='utf8')
    accounts = inputFile.readlines()
    k = 0
    for account in accounts:

        print('Sending for Account No: ' + str(k + 1))
        k += 1

        msg = MIMEMultipart()
        msg['From'] = account.rstrip('\n')

        for i in range(args.quantity):
            print("Sending Mail No: " + str(i+1))

            random_email = None
            random_email = email_gtr.get_email(include_attachments=includeAttachments)

            msg['Date'] = random_email.sent_date

            # If subject is required to be translated from english, translate it
            if args.flag_lang != 'en':
                blob = TextBlob(str(random_email.subject[0]))
                print("Printing subject: ", blob.translate(to=args.flag_lang))
                msg['Subject'] = str(blob.translate(to=args.flag_lang))
            else:
                msg['Subject'] = random_email.subject[0]

            if (random_email.to is None or len(random_email.to) == 0):
                msg['To'] = 'shouldnthappen@devtest-jb.com'
            elif len(random_email.to) > 1:
                msg['To'] = replace_emaildomain(args, custom_join(random_email.to, ', '))
            else:
                msg['To'] = random_email.to[0]

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

            try:
                mail(server, args, msg)
                print("Sent " + str(i + 1) + " mail")
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

    inputFile.close()

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
        domain_name=args.domain_name)

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
        #logger.info("Sending " + str(i) + " th mail")

        random_email = None
        random_email = email_gtr.get_email(include_attachments=includeAttachments)

        msg = MIMEMultipart()
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

        if (random_email.to is None or len(random_email.to) == 0):
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
                print("Printing body: ", blob.translate(to = args.flag_lang))
                msg.attach(MIMEText(str(blob.translate(to = args.flag_lang)), 'plain', 'utf-8'))
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
            print("Sent " + str(i) + " th mail")
            #logger.info("Sent " + str(i) + " th mail")

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
            else:
                server.sendmail(args.addresses[0], args.addresses[1], msg.as_string())
        except smtplib.SMTPException:
            raise Exception('Failed to send email!')

    return server
