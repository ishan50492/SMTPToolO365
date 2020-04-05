import json

class email_object(object):
    sender = None
    to = None
    cc = None
    bcc = None
    subject = None
    body = None
    b_attachments = None
    attachments = None
    sent_date = None

    def __init__(self, sender, to, cc, bcc, subject, body, b_attachments, attachments, sent):
        self.sender = sender
        self.to =  to
        self.cc = cc
        self.bcc = bcc
        self.subject = subject
        self.body = body
        self.b_attachments = b_attachments
        self.attachments = attachments
        self.sent_date = sent

    def to_string(self):
        str_output = 'Sender: ' + self.sender[-1] + '\n'
        str_output += 'To: ' + ','.join(self.to) + '\n'
        str_output += 'CC: ' + ','.join(self.cc) + '\n'
        str_output += 'BCC: ' + ','.join(self.bcc) + '\n'
        str_output += 'Subject: ' + self.subject[-1] + '\n'
        str_output += 'Body: ' + ','.join(self.body) + '\n'
        if self.b_attachments:
            str_output += 'Attachments: ' + ','.join(self.attachments) + '\n'
        else:
            str_output += 'Attachments: \n'
        str_output += 'Sent Date: ' + self.sent_date + '\n'
        
        return str_output

    def reprJSON(self):
        return dict(
            sender=self.sender[-1],
            to=self.to,
            cc=self.cc,
            bcc=self.bcc,
            subject=self.subject[-1],
            body=self.body,
            attachments=self.attachments,
            sentdate=self.sent_date
        )

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)