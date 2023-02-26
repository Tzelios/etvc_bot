# Email To Viber Channel Bot#

**A simple bot to fetch the *unseen* emails using imap and send the results to a channel in viber.**
<br/><br/>
To run this script you need a webhook server. See details [here](https://developers.viber.com/docs/tools/channels-post-api/#setting-a-webhook).

<br/><br/>
## You need to modify the **.env** file with: ##

1. **imap server, username, password**, and **viber chanel token**,

2. Need to provide the email(s) **whitelist** with comma separated values,

3. Specify the **text line(s)** to search in the body of the email with comma separated values(white space matters).
<br/><br/>

Then run:
    
    python3 main.py

<br/><br/>
* The emails will be fetched every 10 minutes and a message will appear in your channel.

* Note: if more than one superusers exist only the first one will send messages.


<br/><br/>
For more information visit the [Viber API Documentation.](https://developers.viber.com/docs/tools/channels-post-api/)

