from app import app

if __name__ == "__main__":
    # Bind only to localhost so the app is accessible only on this machine
    app.run(host="127.0.0.1", port=5000, debug=True)
