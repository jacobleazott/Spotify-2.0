# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    WEEKLY EMAIL REPORT                      CREATED: 2024-07-13          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# This script is to generate a report of specified information from spotify to the user.
#
# Current Reporting Functionality -
# SANITY TESTS -
#   All sanity tests under Sanity_Tests.py are currently being run and pushed to the user.
#
# LISTENING DATA -
#   It generates a graph giving you how many hours you listened to each day over the past week. It also overlays a line
#   graph that shows you your current average over the past 4 weeks.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import matplotlib.pyplot as plt 
import os
import smtplib
import sqlite3

from datetime             import datetime, timedelta
from email.mime.image     import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from itertools            import product

from src.helpers.decorators import *
from src.helpers.Settings   import Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Flatten nested dictionaries and lists while preserving structure.
INPUT: 
OUTPUT: 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def flatten_row(row, parent_key=""):
    flattened = {}

    for key, value in row.items():
        new_key = f"{parent_key} {key}".strip()

        if isinstance(value, list):
            # If list contains dictionaries, expand them
            if all(isinstance(item, dict) for item in value):
                expanded = [flatten_row(item, new_key) for item in value]
                # Store expanded dictionaries for later processing
                flattened[new_key] = expanded
            else:
                flattened[new_key] = ", ".join(map(str, value))
        elif isinstance(value, dict):
            flattened.update(flatten_row(value, new_key))
        else:
            flattened[new_key] = value

    return flattened


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Expands nested lists of dictionaries while preserving relationships.
INPUT: 
OUTPUT: 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def expand_rows(data):
    flat_data = [flatten_row(item) for item in data]
    expanded_rows = []

    for row in flat_data:
        # Identify and handle multi-level dictionary expansions
        multi_columns = {k: v for k, v in row.items() if isinstance(v, list) and all(isinstance(i, dict) for i in v)}

        if multi_columns:
            for values in product(*multi_columns.values()):
                new_row = row.copy()
                for key, value in zip(multi_columns.keys(), values):
                    new_row.update(value)  # Merge expanded dictionary
                    del new_row[key]       # Avoid keeping the nested structure
                expanded_rows.append(new_row)
        else:
            expanded_rows.append(row)

    return expanded_rows



"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Avoid repeating parent rows by leaving subsequent cells blank.
INPUT: 
OUTPUT: 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def merge_duplicates(expanded_rows, preserve_keys):
    previous_row = {}

    for row in expanded_rows:
        for key in preserve_keys:
            if row.get(key) == previous_row.get(key):
                row[key] = ""
            else:
                previous_row[key] = row[key]
                
    print(previous_row)

    return expanded_rows


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: 
INPUT: 
OUTPUT: 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def generate_dynamic_table(data):
    if not data:
        return "<p>No data available.</p>"
    
    expanded_data = expand_rows(data)
    preserve_keys = [key for key in expanded_data[0].keys() if "Playlist" in key or "Track" in key]
    expanded_data = merge_duplicates(expanded_data, preserve_keys)
    
    headers = expanded_data[0].keys()
    table_html = "<table> <thead> <tr>"
    
    for header in headers:
        table_html += f'<th>{header}</th>'
    table_html += "</tr> </thead> <tbody>"
    
    for idx, row in enumerate(expanded_data):
        table_html += f'<tr style="background-color: {"#1E1E1E" if idx % 2 == 0 else "#252525"};">'
        
        for key in headers:
            value = row.get(key, "")
            table_html += f'<td>{value}</td>'
        
        table_html += "</tr>"
    
    table_html += "</tbody> </table>"
    return table_html


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Class that handles creating a backup of the user's followed artists, playlists, and all their tracks.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class WeeklyReport(LogAllMethods):
    LISTENING_DATA_PLOT_FILEPATH = 'logs/listening_data_plot.png'
    
    def __init__(self, sanity_tester, logger=None):
        self.sanity_tester = sanity_tester
        self.logger = logger if logger is not None else logging.getLogger()

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Sends an email with subject, and body to 'RECIPIENT_EMAIL' from 'SENDER_EMAIL', requires app creds from
                 the referenced location.
    INPUT: subject - Str title of the email.
           body - Str html body of the email.
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def _send_email(self, subject, body):
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = subject
        msgRoot['From'] = Settings.SENDER_EMAIL
        msgRoot['To'] = Settings.RECIPIENT_EMAIL
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        msgText = MIMEText(body, 'html')
        msgAlternative.attach(msgText)

        with open(self.LISTENING_DATA_PLOT_FILEPATH, 'rb') as image_file:
            image_data = image_file.read()

        msg_image = MIMEImage(image_data, name=os.path.basename(self.LISTENING_DATA_PLOT_FILEPATH))
        msg_image.add_header('Content-ID', f'<{self.LISTENING_DATA_PLOT_FILEPATH}>')
        msgRoot.attach(msg_image)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(Settings.SENDER_EMAIL, os.environ['GMAIL_TOKEN'])
            smtp_server.sendmail(Settings.SENDER_EMAIL, Settings.RECIPIENT_EMAIL, msgRoot.as_string())
            
            
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Creates a bar plot for the last week of listening shown in hours Sunday-Saturday.
    INPUT: N/A
    OUTPUT: Saves off a listening_data_plot.png file for use later.
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def _gen_playback_graph(self):
        conn = sqlite3.connect(Settings.LISTENING_DB)
        values = []

        for diff_day in range(0, 7):
            # Since we run on Monday AM, we want prev Sun to this past Sat
            date = datetime.today() - timedelta(days=8-diff_day)
            db_res = conn.execute(f"""SELECT * FROM '{date.year}'
                                  WHERE time >= ?
                                  AND time < ?;"""
                                  , (f"{date.strftime(r"%Y-%m-%d")} 00:00:00", f"{date.strftime(r"%Y-%m-%d")} 23:59:59")
                                  ).fetchall()
            values.append([date.strftime("%A\n%m/%d"), db_res])

        fig, ax = plt.subplots(figsize = (10, 5))
        fig.patch.set_facecolor('#181818')  # Dark gray background
        ax.set_facecolor('#181818')  # Dark gray background for the axis

        # Add x, y gridlines
        ax.tick_params(axis='both', labelcolor='white', colors='white')
        ax.grid(axis='y', color='white', linestyle='-.', linewidth=1, alpha=0.3)
        ax.set_axisbelow(True)

        plt.bar([val[0] for val in values], [len(val[1])/240 for val in values], color='#1DB954', width=0.8)
        plt.ylabel("Hours Spent Listening", color='white')
        plt.title(f"Spotify Listening For {(datetime.today() - timedelta(days=8)).strftime('%b %d %Y')} -"
                  f"{(datetime.today() - timedelta(days=2)).strftime('%b %d %Y')}", color='white')
        
        # Add previous month of listening data
        average = self._gen_average_for_past_month(conn, 28)
        plt.plot(average, color='#CCCCCC', linewidth=1.5)

        conn.close()
        plt.savefig(self.LISTENING_DATA_PLOT_FILEPATH) 
    
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Generates listening data average over the last 'days_back' by weekday. Disregards days with less than 
                 25 mins of listening to disregard token refresh errors.
    INPUT: listening_conn - Db object for listening_data.
           days_back - Number of days to go back for average.
    OUTPUT: list of average hours listened to by 0 Monday - 6 Sunday.
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def _gen_average_for_past_month(self, listening_conn, days_back):
        start = datetime.today() - timedelta(days=days_back)
        days = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
        for delta in range((datetime.today() - start).days):
            result_date = (start + timedelta(days=delta)).date()
            tmp_vals = listening_conn.execute(f"""SELECT * FROM '{result_date.year}'
                                WHERE time >= ?
                                AND time < ?;""",
                                (f"{result_date} 00:00:00", f"{result_date} 23:59:59")).fetchall()
            
            if len(tmp_vals) >= 100: # Basically just > 25 mins total
                index = (result_date.weekday() + 1) % 7
                days[index] = [len(tmp_vals)*15 + days[index][0], days[index][1] + 1]
        
        return [(day[0]/3600)/day[1] if day[1] != 0 else 0 for day in days]

    def gen_weekly_report(self):
        tables = [
            ("Differences In Playlists", self.sanity_tester.sanity_diffs_in_major_playlist_sets())
          , ("In Progress Artists", self.sanity_tester.sanity_in_progress_artists())
          , ("Duplicates", self.sanity_tester.sanity_duplicates())
          , ("Artist Integrity", self.sanity_tester.sanity_artist_playlist_integrity())
          , ("Contributing Artists Missing", self.sanity_tester.sanity_contributing_artists())
          , ("Non-Playable Tracks", self.sanity_tester.sanity_playable_tracks())
        ]
        html_tables = ""
        for table in tables:
            html_tables += f"<h1>{table[0]}</h1>"
            html_tables += generate_dynamic_table(table[1])
            
        self._gen_playback_graph()
        
        body = f"""
                <html>
                <head>
                    <meta name="color-scheme" content="dark light">
                    <meta name="supported-color-schemes" content="dark light">
                    <style>
                        body {{
                            margin: 0;
                            padding: 0;
                        }}
                        .email-container {{
                            background-color: #181818;
                            color: #CCCCCC;
                            font-family: Arial, sans-serif;
                            padding: 20px;
                        }}
                        table {{
                            border-collapse: collapse;
                            width: 100%;
                        }}
                        thead tr {{
                            background-color: #1DB954;
                            color: #FFFFFF; 
                        }}
                        th, td {{
                            padding: 10px;
                            border: 1px solid #333333;
                            text-align: left;
                        }}
                    </style>
                </head>
                <body>
                    <div class="email-container">
                        <h1> Weekly Listening Data </h1>
                        <div style="text-align: center;">
                            <img src="cid:{self.LISTENING_DATA_PLOT_FILEPATH}">
                        </div>
                        {html_tables}
                    </div>
                </body>
                </html>
            """

        subject = f"Weekly Spotify Report - {datetime.today().strftime('%b %d %Y')}"
        self._send_email(subject, body)


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════