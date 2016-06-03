from flask import Flask
app = Flask(__name__)


@app.route("/hooks/git", method=["POST"])
def git_hook():
    return "Hello PyTube!"


if __name__ == "__main__":
    app.run()
