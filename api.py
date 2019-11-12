from flask import Flask, request

from erp import attendance

app = Flask('script erp scraper')


@app.route('/attendance', methods=['GET'])
def get_attendance():
    return attendance(request.args.get('username'), request.args.get('password'))


if __name__ == "__main__":
    app.run()
