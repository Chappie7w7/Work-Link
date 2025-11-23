from app import create_app
from app.extensiones import socketio

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
