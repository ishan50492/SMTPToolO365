
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
$python SMTPTool.py -v -o "smtp.office365.com" -q 10
```

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
