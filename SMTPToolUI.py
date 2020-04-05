import pyforms
from   pyforms          import *
from   pyforms.controls import ControlText
from   pyforms.controls import ControlButton
from   pyforms.controls import ControlCheckBox
import SMTPTool

class Options(object):
        serverport = 0
        serveraddr = None
        toaddr = None
        fromaddr = None
        quanity = 1
        json_copy = None
        json_input = None
        usetls = False
        usessl = False
        SMTP_USER = ""
        SMTP_PASS = ""
        debuglevel = 0
        verbose = False
        dryrun = True

        #some defaults from ui
        

class SMTPToolUI(BaseWidget):

    def __init__(self):
        BaseWidget.__init__(self,'SMTPToolUI')
        self.parent = None

        #Definition of the forms fields
        self._serverportField    = ControlText('Smtp Port')
        self._serveraddrField   = ControlText('Smtp Host')
        self._toaddrField     = ControlText('Envelope Sender')
        self._fromaddrField     = ControlText('Envelope Recipient')
        self._quanityField      = ControlText('Number of Emails')
        self._jsoncopyField     = ControlCheckBox('Json Copy?')
        self._jsoninputField    = ControlText('Bulk Upload Path')
        
        self._buttonField       = ControlButton('Send')

        #Define the button action
        self._buttonField.value = self.buttonAction

        self.formset = ['_serverportField', '_serveraddrField', '_toaddrField', 
            '_fromaddrField', '_quanityField', '_jsoncopyField', '_jsoninputField',
            (' ','_buttonField', ' '), ' ']


    def buttonAction(self):
        options = Options()
        options.serverport = int(self._serverportField.value)
        options.serveraddr = self._serveraddrField.value
        options.toaddr = self._toaddrField.value
        options.fromaddr = self._fromaddrField.value
        options.quanity =  int(self._quanityField.value)
        options.attachment_percent = -1
        options.json_copy = bool(self._jsoncopyField.value)
        options.json_input = self._jsoninputField.value
        options.json_output_path = None
        options.addresses_file = "./Content/emailaddresses.txt"
        options.attachments_dir = u"./Content/Attachments/"
        options.text_model_file = "./Content/news_articles.txt"
        options.domain_name = None

        SMTPTool.interf(options)

#Execute the application
if __name__ == "__main__":
    pyforms.start_app(SMTPToolUI, geometry=(200, 200, 250, 250) )