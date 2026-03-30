from app import app, initialize_app_data


if __name__ == "__main__":
    initialize_app_data()
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
