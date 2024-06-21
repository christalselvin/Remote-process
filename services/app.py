"""App entry point."""
import sys
sys.path.append("C:/Users/christal/PycharmProjects/RemoteAccess")
from services import create_app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
