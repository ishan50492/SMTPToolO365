# SMTP Tool	
A command-line based smtp client utility for email generation and email ingestion using random generated data based on Markov chain generator for building realistic/user-like data sets.	

###Prerequisites
 
- Users should be created for the associated exchange server (manual/automation) and stored in UserAccounts.xlsx file    
- Configuration should be done of the tool by installing python and dependent packages as mentioned in readme.md
- Execution of the tool is described in readme.md file
 
###Features of the tool
 
- Can be used to generate any number of mails with attachments provided in the attachment folder(Bigger attachments can be used if space needs to be tested)
- Is configured to send mails via exchange, smtp and O365. The default port is 587
- For authentication, user(username, password) will be picked from UserAccounts.xlsx file and will be used to connect to O365 Mail Exchange server
- Once the execution of the tool is complete, console will generate the overall delivery report. Trace of all exchanged mails can also be seen on the console.
 
###Input Files
 
- UserAccounts.xlsx                            This file contains all the O365 user accounts with their passwords
- emailaddresses.txt(optional)       This file is optional and contains all the recipient mail addresses
 
###Server Configuration
Each user needs to connect to O365 Mail exchange. The default O365 server configuration is:
 
- Server Name:     smtp.office365.com
- Port Number:     587
Server name is provided in the command line.
If a different port number is needed to be used, use this flag : -n {portNumber}/ --port {portNumber}
 
###Working
There are two ways for this utility to work with O365 Mail exchange server:
 
Consider a scenario: Generate and send 10 mails
 
- One way is to randomly pick a user account from UserAccounts.xlsx for each of the 10 mails. While sending each mail, user authentication will take place. Each mail might have a unique sender. The problem with this approach is while sending each mail, since authentication is taking place for each sender, this process is slow. The upside is the senders are unique. If unique sender is not a prerequisite, then approach 2 will come in handy
 ```shell script
$python SMTPTool.py -v -o "smtp.office365.com" -q 10
```
- Another way is to pick a user randomly from UserAccounts.xlsx and use it to authenticate to O365 server. For the recipients, all mail accounts will be randomly picked from emailaddresses.txt and specified number of mails will be sent. One thing to note here is all these mails will have the same sender which was picked from UserAccount.xlsx. The benefit of this approach is the authentication to O365 mail server will only take place once for 10 mails(in this case) so the overall process will be faster
 ```shell script
$python SMTPTool.py -v --one -o "smtp.office365.com" -q 10
```
	
## Command line arguments
```
usage: SMTPTool.py [args] serveraddress

positional arguments:
  serveraddr            SMTP/Exchange Server

optional arguments:
  -o o365servername, --o365 o365servername              O365 Mail Exchange Server Name
  --one                                                 Use this flag to send all mails using one account
  -n nnn, --port nnn                                    Server port
  -v, --verbose                                         Verbose message printing
  -l n, --debuglevel n                                  Set to 1 to print smtplib.send messages
  -q n, --quantity n                                    Number of emails to be generated
  -e, --exchange                                        Use Exchange for mail transfer
  -g language, --lang language                          language for generating body and subject of mail


```

### Command Examples

For O365

**Generate** and send 10 emails to provided email address and o365 exchange (Different senders):<br />
Email addresses will be read from UserAccounts.xlsx file
```sh
$python SMTPTool.py -v -o "smtp.office365.com" -q 10
```

**Generate** and send 10 emails to provided email address and o365 exchange (Same sender):<br />
Senders will be read from UserAccounts.xlsx file and recipients will be read from Content/emailaddresses.txt
```sh
$python SMTPTool.py -v --one -o "smtp.office365.com" -q 10
```

For Exchange and SMTP

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
   $pip install pandas
   $pip install xlrd
   
   ```
   
### Execution of SMTPToolExchange

    - Download and unnzip the SMTPToolExchange
    - cd to SMTPToolExchange parent folder which contains all the files
    - Execute the commands as shown above
