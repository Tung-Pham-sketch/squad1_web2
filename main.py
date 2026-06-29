import os
from flask import Flask, render_template, request, jsonify, redirect
from flask import session
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "VAECOsquad1"
print(__name__)


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login', methods=['POST'])
def login():

    username = request.form.get('username')
    password = request.form.get('password')

    print("USERNAME =", username)
    print("PASSWORD =", password)

    if username == 'admin' and password == '787hotspot':

        session['edit_mode'] = True

        print("LOGIN SUCCESS")

        return jsonify({
            'success': True
        })

    print("LOGIN FAILED")

    return jsonify({
        'success': False
    })

@app.route('/logout')
def logout():

    session.pop('edit_mode', None)

    return redirect('/hotspot')

@app.context_processor
def utility_processor():

    def hotspot_image(
            image_map,
            hotspot,
            image_type,
            default_image=""):

        try:

            filename = image_map[hotspot][image_type]

            return (
                "/static/uploads/hotspot/"
                + filename
            )

        except:

            return default_image

    return dict(
        hotspot_image=hotspot_image
    )

@app.route('/rules')
def rules():
    return render_template("rules.html")

@app.route('/memories')
def memories():
    return render_template("memories.html")

@app.route('/hotspot')
def hotspot():

    edit_mode = session.get(
        'edit_mode',
        False
    )

    json_file = 'static/data/hotspot_images.json'

    if os.path.exists(json_file):

        with open(
            json_file,
            'r',
            encoding='utf-8'
        ) as f:

            image_map = json.load(f)

    else:

        image_map = {}

    return render_template(
        'hotspot.html',
        edit_mode=edit_mode,
        image_map=image_map
    )

@app.route('/tools')
def b787_tools():
    return render_template("b787_tools.html")

@app.route(
    '/upload-hotspot-image',
    methods=['POST']
)
def upload_hotspot_image():

    if not session.get('edit_mode'):
        return jsonify({
            'success': False
        }), 403

    UPLOAD_FOLDER = 'static/uploads/hotspot'
    JSON_FILE = 'static/data/hotspot_images.json'

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    hotspot = request.form.get('hotspot')
    image_type = request.form.get('type')

    file = request.files.get('image')

    if not hotspot or not image_type or not file:
        return jsonify({
            'success': False,
            'message': 'Missing data'
        }), 400

    extension = os.path.splitext(
        secure_filename(file.filename)
    )[1]

    filename = f"{hotspot}_{image_type}{extension}"

    filepath = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    file.save(filepath)

    # -----------------------
    # Update JSON Mapping
    # -----------------------

    if os.path.exists(JSON_FILE):

        with open(
                JSON_FILE,
                'r',
                encoding='utf-8'
        ) as f:

            image_map = json.load(f)

    else:

        image_map = {}

    if hotspot not in image_map:
        image_map[hotspot] = {}

    image_map[hotspot][image_type] = filename

    with open(
            JSON_FILE,
            'w',
            encoding='utf-8'
    ) as f:

        json.dump(
            image_map,
            f,
            indent=4
        )

    return jsonify({
        'success': True,
        'filename': filename
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)