import io
import os
import re
import random
from datetime import datetime
from datetime import timedelta
import RandomTextGenerator
import email_object
import tzlocal
import pandas as pd

class EmailGenerator(object):
    mem_list = list()
    attachments_dir = None
    text_generator = None
    addresses_file_path = "./Content/emailaddresses.txt"
    attachments_dir_path = u"./Content/Attachments"
    text_model_file_path = "./Content/news_articles.txt"
    
    def __init__(self, addresses_file_path=None, attachments_dir_path=None, text_model_file_path=None, domain_name=None, args=None):
        self.addresses_file_path = addresses_file_path or self.addresses_file_path
        self.attachments_dir_path = attachments_dir_path or self.attachments_dir_path
        self.text_model_file_path = text_model_file_path or self.text_model_file_path
        self.args = args
        self.userAccounts = None
        self.attachments_dir = os.listdir(self.attachments_dir_path)
        self.text_generator = RandomTextGenerator.TextGenerator(self.text_model_file_path)
        self.domain_name = domain_name

    def loadO365UserAccounts(self, userAccountsFilePath):
        df = pd.read_excel(userAccountsFilePath, sheet_name='Sheet1')
        self.userAccounts = list(zip(df['Username'].to_list(), df['Password'].to_list()))

    def loadEmailAddresses(self, addresses_file_path):

        #load file into memory
        with io.open(addresses_file_path, "r", encoding="utf8") as f:
            #if domain_name is provided, update/replace each email address with domain
            domain_name = self.domain_name
            if(domain_name):
                for line in f:
                    if "@" in line:
                        line = re.sub(r"(?<=@)[^.]+(?=\.).*", domain_name, line)
                    else:
                        line = line.strip() + "@" + domain_name
                    self.mem_list.append(line)
            else:
                self.mem_list = f.readlines()

    def get_emailaddress(self, n=1):
        addresses = list()
        line = next(iter(self.mem_list))
        for i in range(n):
            item = self.get_random_item(iter(self.mem_list))
            item = item.rstrip() if item else line.rstrip()
            if item not in set(addresses):
                addresses.append(item)    

        return addresses

    def get_useraccount(self):
        return random.choice(self.userAccounts)

    def get_attachment(self, n=1):
        attachments = list()

        att_file = next(iter(self.attachments_dir))
        for i in range(n):
            item = self.get_random_item(iter(self.attachments_dir))
            item = item if item else att_file
            if item not in set(attachments):
                attachments.append(item)
    
        return attachments

    def get_random_item(self, itr):
        item = None
        for num, aitem in enumerate(itr):
            if random.randrange(num + 2):
                continue
            item = aitem
        return item

    # default 1 sentence of length 65 characters
    def get_subject(self, n=65):
        strv = list()
        while(not strv or not strv[0]):
            strv = self.text_generator.generate_text(1, n)

        return strv

    # defaults 5 sentences
    def get_body(self, n=5):
        strv = list()
        while(not strv or len(strv) == 0):
            strv = self.text_generator.generate_text(n)

        return strv

    def randomize_attachment(self):
        return random.getrandbits(1)

    def get_date(self):
        #nothing in the future or before previous year
        end_time = datetime.now()
        #start_time = end_time - timedelta(days= 30)
        #random_time = start_time + random.random() * (end_time - start_time)
        tz = tzlocal.get_localzone()
        time = tz.localize(end_time)

        return datetime.strftime(time, '%a, %d %b %Y %H:%M:%S %z')
    
    # get_email(emailaddress_limit, body_sentences_limit, attachments_limit, include_attachments) - generates email with randomize data
    # params: 
    #   emailaddress_limit   - caps email addresses in to, cc and bcc to a specific value
    #       defaults: 5
    #   body_sentences_limit - caps sentences in email body to a specific value 
    #       defaults: 20
    #   attachments_limit    - caps attachments in email to a specific value 
    #       defaults: 5
    #   include_attachments  - specifies whether to include attachments or not for email
    #       default: 1
    #           values (int):
    #               - 0                  - do not include attachments
    #               - 1                  - include attachments
    #               - any other int      - randomize decision to include attachments
    # returns:
    #   email_object
    def get_email(self, emailaddress_limit=5, body_sentences_limit=20, attachments_limit=5, include_attachments=1):
        sender = self.get_emailaddress()
        to = self.get_emailaddress(random.randrange(1, emailaddress_limit))
        cc = self.get_emailaddress(random.randrange(0, emailaddress_limit))
        bcc = self.get_emailaddress(random.randrange(0, emailaddress_limit))
        subject = self.get_subject()
        body = self.get_body(random.randrange(1, body_sentences_limit))
        sent_date = self.get_date()

        if(include_attachments == 1):
            attachments = self.get_attachment(random.randrange(1, attachments_limit))
        elif(include_attachments == 0):
            attachments = None
        else:
            include_attachments = self.randomize_attachment()
            attachments = None if include_attachments == 0 else self.get_attachment(random.randrange(1, attachments_limit))
        
        return email_object.email_object(sender, to, cc, bcc, subject, body, include_attachments, attachments, sent_date)

    def get_email_o365(self, emailaddress_limit=5, body_sentences_limit=20, attachments_limit=5, include_attachments=1):

        if self.args.oneAccount:
            to = self.get_emailaddress(random.randrange(1, emailaddress_limit))
        else:
            to = ''
        cc = ''
        bcc = ''
        subject = self.get_subject()
        body = self.get_body(random.randrange(1, body_sentences_limit))
        sent_date = self.get_date()

        if (include_attachments == 1):
            attachments = self.get_attachment(random.randrange(1, attachments_limit))
        elif (include_attachments == 0):
            attachments = None
        else:
            include_attachments = self.randomize_attachment()
            attachments = None if include_attachments == 0 else self.get_attachment(
                random.randrange(1, attachments_limit))

        return email_object.email_object('', to, cc, bcc, subject, body, include_attachments, attachments,
                                         sent_date)

if __name__ == "__main__":
    #print(EmailGenerator().get_emailaddress(2))
    #print(EmailGenerator().get_attachment(3))

    eg = EmailGenerator()
    print(eg.get_email().to_string())
    print(eg.get_email().to_string())
    print(eg.get_email().to_string())

    ef = EmailGenerator(domain_name="test.com")
    print(ef.get_email().to_string())

    eh = EmailGenerator(addresses_file_path="./Content/50514_addresses_de.txt", text_model_file_path="./Content/Der Tod in Venedig.txt")
    print(eh.get_email().to_string())
    print(eh.get_email(include_attachments=0).to_string())
    print(eh.get_email(include_attachments=3).to_string())
