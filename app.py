from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

from backend.utility import daily_timeline

matplotlib.use('Agg')  # Prevents using Tkinter for rendering
import os
import numpy as np
import preprocessor
import utility
# Load data and model with correct relative paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get backend folder path
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "../frontend/build"), template_folder=os.path.join(BASE_DIR, "../frontend/build"))
df=None
user=None
if not os.path.exists('static'):
    os.makedirs('static')

@app.route("/api/analysis", methods=["POST"])
def all_analysis():
    global df
    data=request.get_json()
    user=data.get("users")
    num_messges,words,num_media_messages,links,active_user_img_link,total_user_percen,wordcloud_display,common_words_link,emoji_link,all_emojis,timeline_link,daily_timeline_link,weekly_timeline_link,monthly_timeline_link,heatmap_link =utility.fetch_stats(user[0],df)
    return jsonify({
        "num_messages": num_messges,
        "num_words":len(words),
        "num_media":num_media_messages,
        "num_links":len(links),
        "active_img":active_user_img_link,
        "total_users":total_user_percen,
        "wordcloud":wordcloud_display,
        "common_words":common_words_link,
        "emoji_link":emoji_link,
        "emoji_list":all_emojis,
        "timeline_link":timeline_link,
        "daily_timeline_link":daily_timeline_link,
        "weekly_timeline_link":weekly_timeline_link,
        "monthly_timeline_link":monthly_timeline_link,
        "heatmap_link":heatmap_link
    })

@app.route("/api/users", methods=["POST"])
def fetch_users():
    global df
    data = request.get_json()
    chat = data.get("chat")
    df=preprocessor.preprocess(chat)
    # Extract unique users from the 'user' column
    unique_users = df["user"].dropna().unique().tolist()
    filtered_users = [user for user in unique_users if user != "group_notification"]
    return jsonify({"users": filtered_users})

@app.route('/static/<path:filename>')
def serve_image(filename):
    return send_from_directory('static',filename)

# Serve React Frontend
@app.route("/")
def serve_react():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)

# Allow CORS
CORS(app, resources={r"/*": {"origins": "*"}})

if __name__ == "__main__":
    from waitress import serve
    app.run(debug=True)
