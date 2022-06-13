import flask
from flask import Flask, jsonify, request, render_template
from rankedRetrieval import handleQuery
app = Flask(__name__)
app.config.from_object(__name__)

@app.route("/", methods=['GET'])
def home():
    resp = {
        "url": []
    }
    if request.method == 'GET':
        print("Come here for the get request")
        return render_template('heheStinky.html')
    # if request.method == 'POST':
    #     data = request.get_json()
    #     query = data["query"]
    #     # 1. retreive the url from the code and push it to the user
    #     # 2. store the url to the resp
    #     resp["status"] = "succeed"
    return jsonify(resp)

@app.route("/search", methods=['POST'])
def search():
    topUrls = None
    if request.method == 'POST':
        # Grab query from request body
        data = request.form.get("q")
        if len(data) > 0:
            topUrls = handleQuery(data)
        else:
            topUrls = handleQuery("hentai sex")
        # Display a list of urls

    return render_template('heheStinky.html', urls=topUrls)


if __name__ == "__main__":
    app.run(debug=True)
    