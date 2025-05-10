import os
import cv2
import numpy as np
from flask import Flask, request, jsonify
from database import create_table, get_db_connection, add_cube

app = Flask(__name__)
create_table()


@app.route("/cubes", methods=["GET"])
def get_all_cubes():
    conn = get_db_connection()
    cubes = conn.execute("SELECT * FROM cubes").fetchall()
    conn.close()
    return jsonify([dict(row) for row in cubes]), 200


@app.route("/top-cubes", methods=["GET"])
def get_top_cubes():
    conn = get_db_connection()
    top_cubes = conn.execute(
        "SELECT * FROM cubes ORDER BY stock DESC LIMIT 3"
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in top_cubes]), 200


@app.route("/cubes", methods=["DELETE"])
def delete_all_cubes():
    conn = get_db_connection()
    conn.execute("DELETE FROM cubes")
    conn.commit()
    conn.close()
    return "", 204


@app.route("/cubes", methods=["PATCH"])
def patch_cubes():
    cubes_to_update = request.get_json()

    if not isinstance(cubes_to_update, list):
        return jsonify({"error": "Request body must be a list"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    for cube in cubes_to_update:
        color = cube.get("color")
        quantity = cube.get("quantity")

        if color is None or quantity is None:
            continue  # skip invalid entries

        cursor.execute(
            """
            UPDATE cubes
            SET stock = MAX(stock - ?, 0)
            WHERE color = ?
            """,
            (quantity, color),
        )

    conn.commit()
    conn.close()
    return "", 204

def detect_color(image_path):
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv = cv2.GaussianBlur(hsv, (5, 5), 0)

    lower_blue = np.array([100, 150, 100])
    upper_blue = np.array([140, 255, 255])

    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])

    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([40, 255, 255])

    lower_orange = np.array([5, 150, 100])
    upper_orange = np.array([15, 255, 255])

    lower_pink = np.array([160, 50, 50])
    upper_pink = np.array([170, 255, 255])

    lower_lime = np.array([30, 100, 100])
    upper_lime = np.array([90, 255, 255])

    lower_cyan = np.array([80, 100, 100])
    upper_cyan = np.array([100, 255, 255])

    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_red = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)
    mask_pink = cv2.inRange(hsv, lower_pink, upper_pink)
    mask_lime = cv2.inRange(hsv, lower_lime, upper_lime)
    mask_cyan = cv2.inRange(hsv, lower_cyan, upper_cyan)

    color_counts = {
        "red": cv2.countNonZero(mask_red),
        "blue": cv2.countNonZero(mask_blue),
        "green": cv2.countNonZero(mask_green),
        "yellow": cv2.countNonZero(mask_yellow),
        "orange": cv2.countNonZero(mask_orange),
        "pink": cv2.countNonZero(mask_pink),
        "lime": cv2.countNonZero(mask_lime),
        "cyan": cv2.countNonZero(mask_cyan)
    }

    detected_color = max(color_counts, key=color_counts.get)

    if color_counts[detected_color] == 0:
        return "unknown"

    return detected_color


# Ruta pentru procesarea imaginilor trimise
@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return 'No image part', 400

    image_file = request.files['image']
    image_path = 'temp_image.jpg'
    image_file.save(image_path)

    try:
        cube_color = detect_color(image_path)
    except Exception as e:
        os.remove(image_path)
        return jsonify({"error": str(e)}), 500

    os.remove(image_path)

    if cube_color != "unknown":
        add_cube(cube_color)

    return jsonify({"message": f"Detected cube color: {cube_color}"}), 200


if _name_ == '_main_':
    app.run(host='0.0.0.0', port=5000, debug=True)