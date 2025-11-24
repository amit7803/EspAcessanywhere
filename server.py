from flask import Flask, render_template_string, request, redirect, jsonify

app = Flask(__name__)

# ✅ Default icons for types
default_icons = {
    "Fan": "https://img.icons8.com/ios-filled/100/fan.png",
    "Light": "https://img.icons8.com/ios-filled/100/light-on.png",
    "Cooler": "https://img.icons8.com/ios-filled/100/air-conditioner.png",
    "AC": "https://img.icons8.com/ios-filled/100/air-conditioner.png",
    "Fridge": "https://img.icons8.com/ios-filled/100/fridge.png",
    "TV": "https://img.icons8.com/ios-filled/100/tv.png",
    "Camera": "https://img.icons8.com/ios-filled/100/camera.png",
    "Motor": "https://img.icons8.com/ios-filled/100/motor.png",
    "Other": "https://img.icons8.com/ios-filled/100/smart-home-connection.png"
}

# ✅ Store devices here
devices = {
    1: {"name": "Fan", "type": "Fan", "image": default_icons["Fan"], "state": "OFF", "gpio": 5},
    2: {"name": "Light", "type": "Light", "image": default_icons["Light"], "state": "OFF", "gpio": 6}
}

# ✅ HTML Page Template
page_template = """
<!DOCTYPE html>
<html>
<head>
  <title>Smart Home Control</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d);
      color: white;
      text-align: center;
      margin: 0; padding: 0;
    }
    h1 { padding: 20px; text-shadow: 2px 2px 5px rgba(0,0,0,0.5); }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px; padding: 20px;
    }
    .card {
      background: rgba(255, 255, 255, 0.15);
      border-radius: 15px; padding: 20px;
      box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
      position: relative;
    }
    .card img { width: 80px; margin-bottom: 10px; }
    .state { margin: 10px 0; font-weight: bold; }
    .switch { position: relative; display: inline-block; width: 60px; height: 34px; }
    .switch input { display: none; }
    .slider {
      position: absolute; cursor: pointer;
      top: 0; left: 0; right: 0; bottom: 0;
      background-color: red; transition: .4s; border-radius: 34px;
    }
    .slider:before {
      position: absolute; content: "";
      height: 26px; width: 26px; left: 4px; bottom: 4px;
      background-color: white; transition: .4s; border-radius: 50%;
    }
    input:checked + .slider { background-color: #22c55e; }
    input:checked + .slider:before { transform: translateX(26px); }
    .delete-btn {
      position: absolute; top: 10px; right: 10px;
      background: #ef4444; border: none; border-radius: 8px;
      color: white; padding: 5px 10px; cursor: pointer; font-size: 12px;
    }
    .delete-btn:hover { background: #b91c1c; }
    .add-form {
      background: rgba(0,0,0,0.3);
      padding: 20px; margin: 20px; border-radius: 15px;
    }
    .add-form input, .add-form select {
      padding: 8px; margin: 5px;
      border-radius: 8px; border: none;
    }
    .add-form button {
      padding: 10px 20px; border: none; border-radius: 8px;
      background: #22c55e; color: white; font-weight: bold; cursor: pointer;
    }
    .add-form button:hover { background: #16a34a; }
    .emergency { margin: 20px; }
    .emergency button {
      background: #ef4444; padding: 12px 25px;
      border: none; border-radius: 10px;
      color: white; font-weight: bold; cursor: pointer;
    }
    .emergency button:hover { background: #b91c1c; }
  </style>
</head>
<body>
  <h1>🏠 Smart Home Controller</h1>
  <div class="grid">
    {% for id, dev in devices.items() %}
      <div class="card">
        <form method="POST" action="/delete/{{ id }}">
          <button type="submit" class="delete-btn">❌ Delete</button>
        </form>
        <img src="{{ dev['image'] }}" alt="{{ dev['name'] }}">
        <h3>{{ dev['name'] }} ({{ dev['type'] }}, GPIO {{ dev['gpio'] }})</h3>
        <p class="state">Status: {{ dev['state'] }}</p>
        <form method="POST" action="/toggle/{{ id }}">
          <label class="switch">
            <input type="checkbox" onchange="this.form.submit()" {{ 'checked' if dev['state']=='ON' else '' }}>
            <span class="slider"></span>
          </label>
        </form>
      </div>
    {% endfor %}
  </div>

  <!-- 🚨 Emergency Button -->
  <div class="emergency">
    <form method="POST" action="/emergency_off">
      <button type="submit">🚨 Emergency OFF (All Devices)</button>
    </form>
  </div>

  <!-- ➕ Add New Device -->
  <div class="add-form">
    <h2>Add New Device</h2>
    <form method="POST" action="/add">
      <input type="text" name="button_name" placeholder="Device Name" required>
      <input type="number" name="gpio" placeholder="GPIO Pin" required>
      <select name="type" required>
        <option value="">-- Select Device Type --</option>
        {% for t in types %}
          <option value="{{t}}">{{t}}</option>
        {% endfor %}
      </select>
      <input type="text" name="image" placeholder="Custom Image URL (optional)">
      <button type="submit">➕ Add Device</button>
    </form>
  </div>
</body>
</html>
"""

# 🏠 Main Page
@app.route("/")
def index():
    return render_template_string(page_template, devices=devices, types=default_icons.keys())

# 🔄 Toggle Device
@app.route("/toggle/<int:dev_id>", methods=["POST"])
def toggle(dev_id):
    if dev_id in devices:
        devices[dev_id]["state"] = "ON" if devices[dev_id]["state"] == "OFF" else "OFF"
    return redirect("/")

# 🚨 Emergency OFF
@app.route("/emergency_off", methods=["POST"])
def emergency_off():
    for dev in devices.values():
        dev["state"] = "OFF"
    return redirect("/")

# ➕ Add Device
@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("button_name")
    gpio = request.form.get("gpio")
    dev_type = request.form.get("type")
    image = request.form.get("image").strip()

    # Agar user image nahi deta → default icon
    if not image:
        image = default_icons.get(dev_type, default_icons["Other"])

    new_id = max(devices.keys(), default=0) + 1
    devices[new_id] = {"name": name, "type": dev_type, "image": image, "state": "OFF", "gpio": gpio}
    return redirect("/")

# ❌ Delete Device
@app.route("/delete/<int:dev_id>", methods=["POST"])
def delete(dev_id):
    if dev_id in devices:
        devices.pop(dev_id)
    return redirect("/")

# 📡 JSON API (for ESP or monitoring) → sirf gpio, name, state
@app.route("/get_state")
def get_state():
    filtered = {
        dev_id: {
            "gpio": dev["gpio"],
            "state": dev["state"]
        }
        for dev_id, dev in devices.items()
    }
    return jsonify(filtered)
