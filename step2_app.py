from from flask import Flask, jsonify, request, render_template, send_file, send_from_directory
import os, csv

app = Flask(__name__)

IMAGE_ROOT = "."
DATA_FILE  = "facecard.csv"

people_data = {}

def name_to_key(full_name, ext=".png"):
    return full_name.strip().replace(" ", "_") + ext

def load_people_data():
    global people_data
    people_data = {}
    if not os.path.exists(DATA_FILE):
        print(f"[WARNING] 找不到 {DATA_FILE}")
        return
    with open(DATA_FILE, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            name = row.get("Name", "").strip()
            if not name:
                continue
            # 同時支援 .png 和 .jpg
            for ext in (".png", ".jpg"):
                key = name_to_key(name, ext)
                parts = name.split(" ", 1)
                people_data[key] = {
                    "name":      name,
                    "first_name": parts[0],
                    "last_name":  parts[1] if len(parts) > 1 else "",
                    "company":   row.get("Company Name",             ""),
                    "role":      row.get("Role",                     ""),
                    "pipeline":  row.get("Sale's pipeline progress", ""),
                    "bd":        row.get("BD in charge",             ""),
                    "isr":       row.get("ISR in charge",            ""),
                    "linkedin":  row.get("Linkedin",                 ""),
                    "app_name":  row.get("App name",                 ""),
                    "mmp":       row.get("MMP",                      ""),
                    "daily_dl":  row.get("Daily downloads",          ""),
                    "dau":       row.get("DAU",                      ""),
                }
    print(f"[INFO] 載入 {len(people_data)//2} 筆")

load_people_data()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_folders")
def get_folders():
    folders = sorted([
        f for f in os.listdir(IMAGE_ROOT)
        if os.path.isdir(os.path.join(IMAGE_ROOT, f))
        and any(
            fn.endswith((".jpg", ".png"))
            for fn in os.listdir(os.path.join(IMAGE_ROOT, f))
        )
    ], reverse=True)
    return jsonify(folders)

@app.route("/get_images")
def get_images():
    folder = request.args.get("folder", "")
    folder_path = os.path.join(IMAGE_ROOT, folder)
    if not folder or not os.path.exists(folder_path):
        return jsonify([])

    result = []
    for fname in sorted(os.listdir(folder_path)):
        if not fname.endswith((".jpg", ".png")):
            continue
        info = people_data.get(fname, {})
        clean_name = fname.replace(".png", "").replace(".jpg", "").replace("_", " ")
        result.append({
            "file":       fname,
            "name":       info.get("name",       clean_name),
            "first_name": info.get("first_name", clean_name.split(" ")[0]),
            "last_name":  info.get("last_name",  ""),
            "company":    info.get("company",    ""),
            "role":       info.get("role",       ""),
            "pipeline":   info.get("pipeline",   ""),
            "bd":         info.get("bd",         ""),
            "isr":        info.get("isr",        ""),
            "linkedin":   info.get("linkedin",   ""),
            "app_name":   info.get("app_name",   ""),
            "mmp":        info.get("mmp",        ""),
            "daily_dl":   info.get("daily_dl",   ""),
            "dau":        info.get("dau",        ""),
            "img_src":    f"/{folder}/{fname}",
        })
    return jsonify(result)

@app.route("/<path:path>")
def serve_file(path):
    return send_from_directory(".", path)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
