from app import app

def run_server():
    app.run(port=app.config["PORT"])

if __name__ == '__main__':
    run_server()
