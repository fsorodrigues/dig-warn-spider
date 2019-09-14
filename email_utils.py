# importing datetime module
from datetime import datetime

# importing email utilities
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# function receives list and iterates over rows creating email notification
def send_notification(rows,s,pw):
    text = []
    html = []

    for row in rows:
        date = datetime.strptime(row['notice_date'],'%Y-%m-%dT%H:%M:%S').strftime('%m/%d/%Y')
        text.append(f'''
            {row["employer_name"]}: {row["total_affected"]} employees affected in {row["address"]["city"]}.\n
            Date of notice: {date}\n
            Access notice at: {row["url"]}
        ''')
        html.append(f'''
            <h4 style="margin: 25px 0 5px 0">{row["employer_name"]}</h4>
            <p style="margin: 0 0 5px 0">Notice on {date} affecting {row["total_affected"]} employees in {row["address"]["city"]}</p>
            <p style="margin: 0 0 10px 0">Access notice <a href="{row["url"]}">here</a>.</p>
        ''')

    now = datetime.now()
    today = now.strftime("%a, %d %b")
    text_plain = "\n\n".join(text)
    text_html = "\n".join(html)

    msg_plain = f'New reports scraped on {today}\n\n{text_plain}'
    msg_html = f'''
        <html>
            <body>
                <div>
                    <h3>New reports scraped on {today}</h3>
                    {text_html}
                </div>
            </body>
        </html>'''

    email_from = 'frodrigues@vtdigger.org'
    email_to = 'VTDigger'
    email_subscribers = [email_from,"agalloway@vtdigger.org","cmeyn@vtdigger.org","awallaceallen@vtdigger.org@vtdigger.org"]

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'WARN Notices {now.strftime("%m/%d/%y")}'
    msg['From'] = 'WARN Notices'
    msg['To'] = email_to

    part1 = MIMEText(msg_plain,'plain')
    part2 = MIMEText(msg_html,'html')

    msg.attach(part1)
    msg.attach(part2)

    s.ehlo()
    s.starttls()
    s.login(email_from,pw)
    s.sendmail(email_from, email_subscribers, msg.as_string())
    s.quit()
