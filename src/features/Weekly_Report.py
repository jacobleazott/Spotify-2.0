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
import textwrap

from datetime             import datetime, timedelta
from email.mime.image     import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from itertools            import product
from PIL                  import Image, ImageDraw, ImageFont

from src.helpers.decorators  import *
from src.helpers.Settings    import Settings
from src.features.Statistics import SpotifyStatistics

# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# GRAPH HELPERS ═══════════════════════════════════════════════════════════════════════════════════════════════════════
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Flatten nested dictionaries and lists while preserving structure.
INPUT: current - int of current progress towards 'goal'.
       goal - int of the end goal of the progress bar.
       target - int of the expected current target of the progress bar.
       filename - path/ name to save progress bar to.
OUTPUT: N/A - Saves progress bar to 'filename'.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def create_progress_bar(current: int, goal: int, target: int, filename: str = "progress_bar.png") -> None:
    width, height = 600, 100
    bar_height = 40
    
    bg_color =      (255, 255, 255, 0  )  # Transparent background
    bar_color =     (76 , 175, 80 , 255)  # Green
    border_color =  (66 , 66 , 66 , 255)  # Dark gray
    target_color =  (255, 87 , 34 , 255)  # Orange
    text_color =    (204, 204, 204, 255)  # Light gray
    
    image = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Draw bar background with rounded corners
    draw.rounded_rectangle([(0, (height - bar_height) // 2), (width, (height + bar_height) // 2)]
                         , radius=bar_height // 2, outline=border_color, width=3, fill=bg_color)
    
    # Draw progress bar with rounded corners
    progress_width = int(width * (current / goal))
    draw.rounded_rectangle([(0, (height - bar_height) // 2), (progress_width, (height + bar_height) // 2)]
                         , radius=bar_height // 2, fill=bar_color)
    
    # Draw target marker
    target_x = int(width * (target / goal))
    line_thickness = 4
    draw.rectangle([(target_x - line_thickness // 2, (bar_height // 2))
                  , (target_x + line_thickness // 2, (height - bar_height // 2))]
                   , fill=target_color)
    
    font = ImageFont.truetype("DejaVuSans.ttf", 30)
    
    text_y = (height - bar_height) // 2 + (bar_height - font.getbbox("Ay")[3]) // 2
    # Draw current text (left)
    draw.text((10, text_y), f"{current}", font=font, fill=text_color)
    
    # Draw goal text (right)
    goal_text_x = width - 10 - draw.textlength(f"{goal}", font=font)
    draw.text((goal_text_x, text_y), f"{goal}", font=font, fill=text_color)
    
    # Add target text
    target_text = f"{target}"
    draw.text((min(target_x + 15, width - 100), height - 30), target_text, font=font, fill=target_color)
    
    image.save(filename, "PNG")

# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# HTML HELPERS ════════════════════════════════════════════════════════════════════════════════════════════════════════
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Flatten nested dictionaries and lists while preserving structure.
INPUT: row - Dictionary to flatten.
       parent_key - Key to prepend to nested keys.
OUTPUT: "Flattened" dictionary with nested keys expanded.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def flatten_row(row: dict, parent_key: str="") -> dict:
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
INPUT: data - List of dictionaries to expand.
OUTPUT: List of expanded and flattened dictionaries.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def expand_rows(data: list) -> list:
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
DESCRIPTION: Merges duplicate values in a list of dictionaries based on specified keys.
INPUT: expanded_rows - List of dictionaries to merge duplicates in.
       preserve_keys - List of keys to preserve when merging duplicates.
OUTPUT: 'expanded_rows' with duplicates merged.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def merge_duplicates(expanded_rows: list, preserve_keys: list) -> list:
    previous_row = {}
    
    for row in expanded_rows:
        for key in preserve_keys:
            if row.get(key) == previous_row.get(key):
                row[key] = ""
            else:
                previous_row[key] = row[key]
    
    return expanded_rows


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Generates a dynamic HTML table based on the provided data given in a dictionary.
INPUT: data - List of dictionaries containing table data.
OUTPUT: HTML code for the generated table.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def generate_dynamic_table(data: list) -> str:
    if not data:
        return "<p>No data available.</p>\n"
    
    expanded_data = expand_rows(data)
    preserve_keys = [key for key in expanded_data[0].keys() if "Playlist" in key]
    expanded_data = merge_duplicates(expanded_data, preserve_keys)
    
    headers = expanded_data[0].keys()
    table_html = "<table> <thead> <tr>"
    
    for header in headers:
        table_html += f'<th>{header}</th>'
    table_html += "</tr> </thead> <tbody>"
    
    for idx, row in enumerate(expanded_data):
        table_html += f'\n\t<tr style="background-color: {"#1E1E1E" if idx % 2 == 0 else "#252525"};">'
        
        for key in headers:
            value = row.get(key, "")
            table_html += f'<td>{value}</td>'
        
        table_html += "</tr>"
    
    table_html += "</tbody> </table>\n"
    return table_html


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Class that handles creating a backup of the user's followed artists, playlists, and all their tracks.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class WeeklyReport(LogAllMethods):
    LISTENING_DATA_PLOT_FILEPATH = 'logs/listening_data_plot.png'
    PROGRESS_BAR_FILEPATH = 'logs/progress_bar.png'
    
    def __init__(self, sanity_tester, logger=None):
        self.sanity_tester = sanity_tester
        self.logger = logger if logger is not None else logging.getLogger()
        self.statistics = SpotifyStatistics(logger=self.logger)
        
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # GRAPH FUNCTIONS ═════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
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
    DESCRIPTION: Generates a progress bar for the progress on the current years playlist.
    INPUT: N/A
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def _gen_progress_bar(self):
        GOAL = 500
        # Find current year playlist, and count number of tracks, if it exists
        playlists = [playlist['id'] for playlist in self.sanity_tester.dbh.db_get_user_playlists() 
                            if playlist['name'] == f'{datetime.today().year}']
        current = len(self.sanity_tester.dbh.db_get_tracks_from_playlist(playlists[0])) if len(playlists) > 0 else 0

        # Calculate the percentage of the way to the middle of October
        target = min(GOAL, int((datetime.today().timetuple().tm_yday / 288) * GOAL))
        create_progress_bar(current, GOAL, target, filename=self.PROGRESS_BAR_FILEPATH)

    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # EMAIL/ REPORT ═══════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
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
        
        with open(self.PROGRESS_BAR_FILEPATH, 'rb') as image_file:
            image_data = image_file.read()
        
        msg_image = MIMEImage(image_data, name=os.path.basename(self.PROGRESS_BAR_FILEPATH))
        msg_image.add_header('Content-ID', f'<{self.PROGRESS_BAR_FILEPATH}>')
        msgRoot.attach(msg_image)
        
        # Define source address in ipv4 format to force SMTP server to use ipv4, issues with ipv6 for some reason.
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, source_address=('0.0.0.0', 0)) as smtp_server:
            smtp_server.login(Settings.SENDER_EMAIL, os.environ['GMAIL_TOKEN'])
            smtp_server.sendmail(Settings.SENDER_EMAIL, Settings.RECIPIENT_EMAIL, msgRoot.as_string())
            
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Helper to take a list of tuples and generate html tables from them. Using the first index as a title.
    INPUT: table_data - Tuple of title and table data stored in a dictionary.
           indent - Int number of tabs to indent.
    OUTPUT: Indentend html table.
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def _html_table_helper(self, table_data, indent=0):
        html_tables = ""
        for table in table_data:
            html_tables += f"\n<h2>{table[0]}</h2>"
            html_tables += generate_dynamic_table(table[1])
            html_tables += """<hr style="border: none; height: 1px; 
                                background: linear-gradient(to right, #CCCCCC, #888888); 
                                margin: 15px 0;">"""
        
        return textwrap.indent(html_tables, "\t" * indent)

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Generates a 'weekly' emall report for the user. Giving the user a sumary of all the sanity tests, 
                 listening data, and music progress, and more.
    INPUT: N/A
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def gen_weekly_report(self):
        statistic_tables = [
            ("This Weeks Top Artists", self.statistics.generate_latest_artists(datetime.now() - timedelta(days=7)))
          , ("Most Featured Non-Followed Artists", self.statistics.generate_featured_artists_list(10))
        ]
        
        sanity_tables = [
            ("Differences In Playlists", self.sanity_tester.sanity_diffs_in_major_playlist_sets())
          , ("In Progress Artists", self.sanity_tester.sanity_in_progress_artists())
          , ("Duplicates", self.sanity_tester.sanity_duplicates())
          , ("Artist Integrity", self.sanity_tester.sanity_artist_playlist_integrity())
          , ("Contributing Artists Missing", self.sanity_tester.sanity_contributing_artists())
          , ("Non-Playable Tracks", self.sanity_tester.sanity_playable_tracks())
        ]
        
        self._gen_playback_graph()
        self._gen_progress_bar()
        
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
                        <h1 style="color: #1DB954;"> Statistics </h1>
                        <hr style="border: 2px dashed #1DB954;">
                        <div style="text-align: center;">
                            <h2> Weekly Listening Data </h2>
                            <img src="cid:{self.LISTENING_DATA_PLOT_FILEPATH}">
                            <h2> New Music Progress </h2>
                            <img src="cid:{self.PROGRESS_BAR_FILEPATH}">
                        </div>
                        {self._html_table_helper(statistic_tables, indent=6)}
                        <h1 style="color: #1DB954;"> Sanity Checks </h1>
                        <hr style="border: 2px dashed #1DB954;">
                        {self._html_table_helper(sanity_tables, indent=6)}
                    </div>
                </body>
                </html>
            """
        
        subject = f"Weekly Spotify Report - {datetime.today().strftime('%b %d %Y')}"
        self._send_email(subject, body)


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════