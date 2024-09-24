# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                            ╠══╣
# ║  ║    WEEKLY EMAIL REPORT                     CREATED: 2024-07-13          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                            ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ═══════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# This script is to generate a report of specified information from spotify to the user.
#
# Current Reporting Functionality -
# SANITY TESTS -
#   All sanity tests under Sanity_Tests.py are currently being run and pushed to the user.
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import Sanity_Tests
import smtplib
import textwrap
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from PIL import Image
from datetime import datetime, timedelta
import sqlite3
import matplotlib.pyplot as plt 

SENDER_EMAIL = "jacobs.spotify.email@gmail.com"
RECIPIENT_EMAIL = "jacob.leazott@gmail.com"
LISTENING_DB = "databases/listening_data.db"


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Sends an email with subject, and body to 'RECIPIENT_EMAIL' from 'SENDER_EMAIL', requires app creds from
             the referenced location
INPUT: subject - str title of the email
       body - str html body of the email
OUTPUT: NA
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def send_email(subject, body):
    global SENDER_EMAIL, RECIPIENT_EMAIL
    msgRoot = MIMEMultipart('related')

    msgRoot['Subject'] = subject
    msgRoot['From'] = SENDER_EMAIL
    msgRoot['To'] = RECIPIENT_EMAIL
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)
    msgText = MIMEText(body, 'html')
    msgAlternative.attach(msgText)
    
    # Add images
    fp = open("Test/listening_data_plot.png", "rb")
    msgImage = MIMEImage(fp.read())
    fp.close()
    
    msgImage.add_header('Content-ID', '<listening_data_plot>')
    msgRoot.attach(msgImage)
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        f = open(r"tokens/email_token.txt", 'r')
        cred = f.readline().rstrip()
        f.close()
        smtp_server.login(SENDER_EMAIL, cred)
        smtp_server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msgRoot.as_string())
        
        
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Creates a bar plot for the last week of listening shown in hours Sunday-Saturday
INPUT: NA
OUTPUT: Saves off a listening_data_plot.png file for use later
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def gen_playback_graph():
    conn = sqlite3.connect(LISTENING_DB)
    values = []

    for diff_day in range(0, 7):
        # Since we run on Monday AM, we want prev Sun to this past Sat
        date = datetime.today() - timedelta(days=8-diff_day)
        values.append([date.strftime("%A\n%m/%d"), conn.execute(f"""SELECT * FROM '{date.year}' 
                                                WHERE time >= '{date.strftime(r"%Y-%m-%d")} 00:00:00'
                                                AND time < '{date.strftime(r"%Y-%m-%d")} 23:59:59';""").fetchall()])

    fig, ax = plt.subplots(figsize = (10, 5))

    # Add x, y gridlines
    ax.grid(axis='y', color ='grey',
        linestyle ='-.', linewidth = 1,
        alpha = 0.3)
    ax.set_axisbelow(True)

    plt.bar([val[0] for val in values], [len(val[1])/240 for val in values], color='maroon', width=0.8)
    plt.ylabel("Hours Spent Listening")
    plt.title(f"Spotify Listening For {(datetime.today() - timedelta(days=8)).strftime('%b %d %Y')} -" + 
    f"{(datetime.today() - timedelta(days=2)).strftime('%b %d %Y')}")
    
    # Add previous month of listening data
    average = gen_average_for_past_month(conn, 28)
    plt.plot(average, color='black')

    conn.close()
    plt.savefig('Test/listening_data_plot.png') 
    
    
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Generates listening data average over the last 'days_back' by weekday. Disregards days with less than 
             25 mins of listening to disregard token refresh errors
INPUT: listening_conn - db object for listening_data
       days_back - number of days to go back for average
OUTPUT: list of average hours listened to by 0 Monday - 6 Sunday
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def gen_average_for_past_month(listening_conn, days_back):
    start = datetime.today() - timedelta(days=days_back)
    days = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
    for delta in range((datetime.today() - start).days+1):
        result_date = (start + timedelta(days=delta)).date()
        tmp_vals = listening_conn.execute(f"""SELECT * FROM '{result_date.year}' 
                            WHERE time >= '{result_date} 00:00:00'
                            AND time < '{result_date} 23:59:59';""").fetchall()
        if len(tmp_vals) > 100: # Basically just > 25 mins total
            index = (result_date.weekday() + 1) % 7
            days[index] = [len(tmp_vals)*15 + days[index][0], days[index][1] + 1]
    
    res_avg = []
    for day in days:
        res_avg.append((day[0]/3600)/day[1])
    
    # Probably don't need this since we hardcode the len of array but just to be safe
    if len(res_avg) != 7:
        res_avg = [0, 0, 0, 0, 0, 0, 0]
    
    return res_avg


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Helper function to format html sections when we want data in header/ unordered list formats
INPUT: values - list of tuple values where the first elem is the section title and second value is list that goes under
       default - str we should return if nothing was in the values
OUTPUT: html formatted str of 'values'
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def gen_html_header_list(values, default):
    html_str = ""

    for val in values:
        html_str += f"\n<h4> {val[0]} - </h4>\n<ul>\n"
        for elem in val[1]:
            html_str += f"\t<li> {elem} </li>\n"
        html_str += "</ul>"
        
    if html_str == "":
        html_str = f"<p><b> {default} </b></p>"
        
    return html_str


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Helper function to format html sections when we just want data listed in unordered lists
INPUT: values - list of values that will be in our unordered list
       default - str we should return if nothing was in the values
OUTPUT: html formatted str of 'values'
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def gen_html_unordered_list(values, default):
    html_str = "\n<ul>\n"
    
    for val in values:
        html_str += f"\t<li> {val} </li>\n"
    html_str += "</ul>"
    
    if len(values) == 0:
        html_str = f"<p><b> {default} </b></p>"

    return html_str


def main():
    st = Sanity_Tests.SanityTest()
    
    st_diffs = gen_html_header_list(st.sanity_diffs_in_major_playlist_sets(), "No Differences Detected For Master, Years, and '__' Good Job!")
    st_prog = gen_html_unordered_list(st.sanity_in_progress_artists(), "No Differences Detected For Master, Years, and '__' Good Job!")
    st_dupe = gen_html_header_list(st.sanity_duplicates(), "No Duplicates Detected Good Job!")
    st_integ = gen_html_unordered_list(st.sanity_artist_playlist_integrity(), "No Issues Detected In Artist Integrity Good Job!")
    st_contr = gen_html_unordered_list(st.sanity_contributing_artists(), "No Missing Tracks From Contributing Artists Good Job!")
    
    gen_playback_graph()
    
    body = \
    f"""
    <html>
        <h1> Weekly Spotify Report </h1>
        <h1> Weekly Listening Data </h1>
        <img src="cid:listening_data_plot">
        <h1> Sanity Tests -</h1>
        <h2> - Playlist Diffs - </h2>
        <div style="margin-left:35px;"> {textwrap.indent(st_diffs, "\t\t")} \n\t </div>
        <h2> - In Progress Artists - </h2>
        <div style="margin-left:35px;"> {textwrap.indent(st_prog, "\t\t")} \n\t </div>
        <h2> - Duplicates - </h2>
        <div style="margin-left:35px;"> {textwrap.indent(st_dupe, "\t\t")} \n\t </div>
        <h2> - Artist Integrity - </h2>
        <div style="margin-left:35px;"> {textwrap.indent(st_integ, "\t\t")} \n\t </div>
        <h2> - Contributing Artists Missing - </h2>
        <div style="margin-left:35px;"> {textwrap.indent(st_contr, "\t\t")} \n\t </div>
    </html>
    """
    subject = f"Weekly Spotify Report - {datetime.today().strftime('%b %d %Y')}"
    
    send_email(subject, body)


if __name__ == "__main__":
    main()

# FIN ════════════════════════════════════════════════════════════════════════════════════════════════════════════════