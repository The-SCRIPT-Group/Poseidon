from flask import Flask, request, redirect, url_for

from erp import attendance, attendance_json

app = Flask(__name__)


@app.route('/api/attendance', methods=['POST'])
def get_attendance():
    return attendance_json(request.form['username'], request.form['password'])


@app.route('/attendance', methods=['GET', 'POST'])
def view_attendance():
    if request.method == 'POST':
        return attendance(request.form['username'], request.form['password'])
    return """
        <form action="" method="POST">
            <p><input type="text" name="username" required>
            <p><input type="password" name="password" required>
            <p><input type="submit" value="Login">
        </form>
        """


@app.route('/')
def root():
    return redirect(url_for('get_attendance'))


if __name__ == "__main__":
    app.run()
