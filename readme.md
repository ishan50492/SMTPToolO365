# SMTP Tool
A command-line based smtp client utility for email generation and email ingestion using random generated data based on Markov chain generator for building realistic/user-like data sets.

### Tool Features

For O365 Mail Exchange server
- This tool has been configured to send mails via Exchange, SMTP and O365 mail servers
- There are two ways in which O365 Mail exchange server can be used

Way 1
-

### SMTPTool Structure
```
SMTPTool
|    SMTPTool.py             - command-line interface for constructing and send emails
|    RandomEmailGenerator.py - generates random data for each email field
|    RandomTextGenerator.py  - generates sentences for email subject and body
|    email_object.py         - object for email structure
|    reading_file.py         - to read the text file used to generate text
|    readme.md
└───Content                  - directory for content that makes up generated emails
     |   Attachments/                   - directory with variety of files to use as email attachments
     |   Attachments_fr/                - directory with mix of French files to use as email attachments
     |   Attachments_de/                - directory with mix of German files to use as email attachments
     |   SMTPemailaddresses.txt         - contains list of email accounts to use for email sender and recipients fields to send emails via Mail Server
     |   Exchangeemailaddresses.text    - contains list of email accounts to use for email sender and recipients fields to send emails via Exchange Server
     |   news_articles.txt              - text document to use as model input for Markov chain to generate sentences
     |   Der Tod in Venedig.txt         - German text document for generating German content
     |   Le_Diable_au_corps.txt         - French text document for generating French context
```

Usage: SMTPTool.py [args] serveraddress 

SMTPTool.py is the main script which is responsible for sending the data via the provided server

[args] contain all the different combinations of flags with their values

serveraddress is the address of either the SMTP or Mail Server

## Command line arguments
```
usage: SMTPTool.py [args] serveraddress

positional arguments:
  serveraddr            SMTP/Exchange Server

optional arguments:
  -h, --help                                            show this help message and exit
  -t, --usetls                                          Connect using TLS, default is false
  -s, --usessl                                          Connect using SSL, default is false
  -n nnn, --port nnn                                    SMTP server port
  -u username, --username username                      SMTP server auth username
  -p password, --password password                      SMTP server auth password
  -v, --verbose                                         Verbose message printing
  -l n, --debuglevel n                                  Set to 1 to print smtplib.send messages
  -q n, --quantity n                                    Number of emails to be generated
  -r, --dryrun                                          Execute script without sending email
  -i filepath, --jsoninput filepath                     Sends emails from json file
  -j, --jsonoutput                                      Copies emails to json file for email data ingestion
  -o filepath, --jsonoutputfile filepath                File path for emails copies to json file for email data ingestion
  -c n, --attachmentpercent n                           Int value for percentage of emails to include attachments
  -f filepath, --addressesfile filepath                 Email addresses to use for generated emails
  -a filepath, --attachmentsdir filepath                Attachments to use for generated emails
  -x filepath, --textmodelfile filepath                 Input text to use for generated subject and body of emails
  -d domainname, --domainname domainname                Adds/replaces domains of provided email addresses
  -m addresses addresses, --smtp addresses addresses    Use Mail Server for mail transfer
  -e, --exchange                                        Use Exchange for mail transfer
  -g language, --lang language                          language for generating body and subject of mail


```

### Remember
For [args], one out of -e or -m should be present. Rest all are optional.

### Command Examples


**Generate** and send one email to provided email address and exchange host:<br />
Email addresses in case of Exchange server will be read from Exchangeemailaddresses.txt file
```sh
python SMTPTool.py -v -e usw81csv162ex01.162ex.local
```

**Generate** and send 100 emails to provided email address and exchange host:<br />
Email addresses in case of Exchange server will be read from Exchangeemailaddresses.txt file
```sh
python SMTPTool.py -v -e usw81csv162ex01.162ex.local -q 100
```


**Generate** and send 500 emails via Exchange Server with provided emailaddresses file:
```sh
python SMTPTool.py -q 500 -f "./Content/testcompany_addresses.txt" -v -e usw81csv162ex01.162ex.local
```


### Deploying SMTPTool (requires Python 3.6.x) dependencies:

   - Install python
   - Download and unzip folder SMTPTool
   - cd to SMTPTool
   - Install python packages by executing
   ```
   $pip install markovify
   $pip install textblob
   $pip install tzlocal
   $pip install pyodbc
   
   ```
   
### Execution of SMTPToolExchange

    - Download and unnzip the SMTPToolExchange
    - cd to SMTPToolExchange parent folder which contains all the files
    - Execute the commands as shown above
