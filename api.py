from random import choice

from flask import Flask, request, redirect, url_for, render_template

from erp import attendance, attendance_json, timetable, miscellaneous, fees, fees_json

# Initialize our Flask application
app = Flask(__name__)

# Map our methods to the string returned by webpage to make function calls easier
methods = {
    "attendance": attendance,
    "timetable": timetable,
    "fees": fees,
    "miscellaneous": miscellaneous,
}


@app.route("/api/attendance", methods=["POST"])
def get_attendance():
    """
    # Route for attendance API
    Returns
    -------
    JSON with person's attendance OR error message
    """
    if "username" not in request.form.keys() or "password" not in request.form.keys():
        return "Please provide all details if you want your attendance", 400
    username = request.form["username"]
    password = request.form["password"]
    if username == "S0000000000" and password == "password":
        random_attendance = [
            '[{"subject": "Design and Analysis of Algorithms", "th_present": 11, "th_total": 24, "tu_present": 8, "tu_total": 8}, {"subject": "Data Warehousing and Data Mining", "th_present": 7, "th_total": 24, "pr_present": 4, "pr_total": 5}, {"subject": "Information Security", "th_present": 7, "th_total": 14, "pr_present": 6, "pr_total": 8}, {"subject": "High Performance Computing", "th_present": 10, "th_total": 29, "pr_present": 6, "pr_total": 7}, {"subject": "Web Technology Lab", "pr_present": 8, "pr_total": 14}, {"subject": "Finance and Costing", "th_present": 3, "th_total": 15}]',
            '[{"subject": "Design and Analysis of Algorithms", "th_present": 23, "th_total": 33, "tu_present": 10, "tu_total": 12}, {"subject": "Data Warehousing and Data Mining", "th_present": 7, "th_total": 26, "pr_present": 2, "pr_total": 7}, {"subject": "Information Security", "th_present": 11, "th_total": 31, "pr_present": 3, "pr_total": 6}, {"subject": "High Performance Computing", "th_present": 6, "th_total": 18, "pr_present": 2, "pr_total": 5}, {"subject": "Web Technology Lab", "pr_present": 6, "pr_total": 12}, {"subject": "Finance and Costing", "th_present": 4, "th_total": 15}]',
        ]
        return choice(random_attendance)
    return attendance_json(username, password)

@app.route("/api/fees", methods=["POST"])
def get_fees():
    """
    # Route for Fees API
    Returns
    -------
    JSON with person's fees OR error message
    """
    if "username" not in request.form.keys() or "password" not in request.form.keys():
        return "Please provide all details if you want your fees", 400
    username = request.form["username"]
    password = request.form["password"]
    if username == "S0000000000" and password == "password":
        random_fees = [
            '[{"Fees Type": "Structural Fee", "Particulars": "TUITION FEE [1]", "Receivable Amount": "50000", "Received Amount": "50000", "Adjustment": "0", "Outstanding": "0", "Advance": "0"}, {"Fees Type": "Structural Fee", "Particulars": "STUDENT ACTIVITY FEE [1]", "Receivable Amount": "50000", "Received Amount": "50000", "Adjustment": "0", "Outstanding": "0", "Advance": "0"}, {"Fees Type": "Structural Fee", "Particulars": "OTHER ACADEMIC FEES [2]", "Receivable Amount": "8850", "Received Amount": "0", "Adjustment": "0", "Outstanding": "8850", "Advance": "0"}, {"Fees Type": "Structural Fee", "Particulars": "DEVELOPMENT FEE [2]", "Receivable Amount": "29500", "Received Amount": "0", "Adjustment": "0", "Outstanding": "29500", "Advance": "0"}, {"Fees Type": "Structural Fee", "Particulars": "STUDENT ACTIVITY FEE [2]", "Receivable Amount": "150", "Received Amount": "0", "Adjustment": "0", "Outstanding": "150", "Advance": "0"}, {"Fees Type": "Structural Fee", "Particulars": "TUITION FEE [2]", "Receivable Amount": "61500", "Received Amount": "8250", "Adjustment": "0", "Outstanding": "53250", "Advance": "0"}, {"Fees Type": "Structural Fee", "Particulars": "TUITION FEE [3]", "Receivable Amount": "95000", "Received Amount": "0", "Adjustment": "0", "Outstanding": "95000", "Advance": "0"}, {"Fees Type": "Examination", "Particulars": "CAP FEE", "Receivable Amount": "200", "Received Amount": "200", "Adjustment": "0", "Outstanding": "0", "Advance": "0"}, {"Fees Type": "Examination", "Particulars": "EXAM FEE", "Receivable Amount": "1800", "Received Amount": "1800", "Adjustment": "0", "Outstanding": "0", "Advance": "0"}, {"Fees Type": "Examination", "Particulars": "EXAM FEE", "Receivable Amount": "500", "Received Amount": "500", "Adjustment": "0", "Outstanding": "0", "Advance": "0"}, {"Fees Type": "Examination", "Particulars": "STATEMENT OF MARKS FEE", "Receivable Amount": "150", "Received Amount": "150", "Adjustment": "0", "Outstanding": "0", "Advance": "0"}, {"Fees Type": "Non-Structural Fee", "Particulars": "Admission Processing Fees", "Receivable Amount": "200", "Received Amount": "200", "Adjustment": "0", "Outstanding": "0", "Advance": "0"}]',
            '[{"Fees Type": "Structural Fee", "Particulars": "TUITION FEE [1]", "Receivable Amount": "50000", "Received Amount": "25000", "Adjustment": "0", "Outstanding": "25000", "Advance": "0"}, {"Fees Type": "Structural Fee", "Particulars": "STUDENT ACTIVITY FEE [1]", "Receivable Amount": "50000", "Received Amount": "15000", "Adjustment": "0", "Outstanding": "35000", "Advance": "0"}, {"Fees Type": "Structural Fee", "Particulars": "OTHER ACADEMIC FEES [2]", "Receivable Amount": "8850", "Received Amount": "1000", "Adjustment": "0", "Outstanding": "7850", "Advance": "0"}, {"Fees Type": "Structural Fee", "Particulars": "DEVELOPMENT FEE [2]", "Receivable Amount": "29500", "Received Amount": "3000", "Adjustment": "0", "Outstanding": "26500", "Advance": "0"}, {"Fees Type": "Structural Fee", "Particulars": "STUDENT ACTIVITY FEE [2]", "Receivable Amount": "150", "Received Amount": "150", "Adjustment": "0", "Outstanding": "0", "Advance": "0"}, {"Fees Type": "Structural Fee", "Particulars": "TUITION FEE [2]", "Receivable Amount": "61500", "Received Amount": "8250", "Adjustment": "0", "Outstanding": "53250", "Advance": "0"}, {"Fees Type": "Structural Fee", "Particulars": "TUITION FEE [3]", "Receivable Amount": "95000", "Received Amount": "0", "Adjustment": "0", "Outstanding": "95000", "Advance": "0"}, {"Fees Type": "Examination", "Particulars": "CAP FEE", "Receivable Amount": "200", "Received Amount": "200", "Adjustment": "0", "Outstanding": "0", "Advance": "0"}, {"Fees Type": "Examination", "Particulars": "EXAM FEE", "Receivable Amount": "1800", "Received Amount": "1800", "Adjustment": "0", "Outstanding": "0", "Advance": "0"}, {"Fees Type": "Examination", "Particulars": "EXAM FEE", "Receivable Amount": "500", "Received Amount": "500", "Adjustment": "0", "Outstanding": "0", "Advance": "0"}, {"Fees Type": "Examination", "Particulars": "STATEMENT OF MARKS FEE", "Receivable Amount": "150", "Received Amount": "150", "Adjustment": "0", "Outstanding": "0", "Advance": "0"}, {"Fees Type": "Non-Structural Fee", "Particulars": "Admission Processing Fees", "Receivable Amount": "200", "Received Amount": "100", "Adjustment": "0", "Outstanding": "100", "Advance": "0"}]',
        ]
        return choice(random_fees)
    return fees_json(username, password)

@app.route("/web", methods=["GET", "POST"])
def web():
    """
    A small frontend which lets you view attendance or timetable in a browser
    Returns
    -------

    """
    if request.method == "POST":
        return methods[request.form["page"]](
            request.form["username"], request.form["password"]
        )
    return render_template("login.html")


@app.route("/")
def root():
    """
    Root of the site
    Returns
    -------
    Redirects you to /web
    """
    return redirect(url_for("web"))


if __name__ == "__main__":
    app.run()
