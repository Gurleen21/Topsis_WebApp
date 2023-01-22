import smtplib

from flask import Flask, render_template, request
import pandas as pd
import math as math
import sys

app = Flask(__name__, template_folder='templateFiles',
            static_folder='staticFiles')


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():  # put application's code here
    res = request.values.to_dict()
    file = request.files['file']
    file.save(file.filename)

    def main(path, weights, impacts, returnPath):
        df = pd.read_csv(path)
        _, c = df.shape
        if c < 3:
            print('Incorrect File: Columns less than 3')
            return -6
        weights = weights
        impacts = impacts
        if check_parameters(weights, (c - 1)) < 0:
            print("Incorrect Number of Weights")
            return -3
        if check_parameters(impacts, (c - 1)) < 0:
            print("Incorrect Number of Impacts")
            return -4
        return_path = returnPath
        if get_file(return_path) != -1:
            print("Return File already exists")
            return -5
        df = topsis(path, weights, impacts)
        df.to_csv(return_path)

    def check_parameters(parameters, paralen):
        try:
            if (len(parameters.split(',')) != paralen):
                # print("Incorrect number of Parameters!")
                return -1
            else:
                return 1
        except:
            if (len(parameters) != paralen):
                # print("Incorrect number of Parameters!")
                return -1
            else:
                return 1

    def get_file(path):
        try:
            test_dataset = pd.read_csv(path)
            return 1
        except:
            return -1

    def calc_score(df, weight, impacts):
        rows = len(df)
        cols = len(df[0])
        rss = [0] * cols
        sum_val = [0] * cols
        best = [0] * cols
        worst = [0] * cols

        for j in range(cols):
            for i in range(rows):
                sum_val[j] += df[i][j] ** 2
            rss[j] = math.sqrt(sum_val[j])

        for j in range(cols):
            for i in range(rows):
                df[i][j] /= rss[j]

        temp_max = float('-inf')
        temp_min = float('inf')

        for j in range(cols):
            for i in range(rows):
                if df[i][j] > temp_max:
                    temp_max = df[i][j]
                if df[i][j] < temp_min:
                    temp_min = df[i][j]
            if impacts[j] == '+':
                best[j] = temp_max
                worst[j] = temp_min
            elif impacts[j] == '-':
                best[j] = temp_min
                worst[j] = temp_max
            else:
                print("Inappropriate Impacts!")
                return -1

        # dataset S+ + S- = sum_p
        sum_p = [0] * rows
        # dataset S+ = eb
        eb = [0] * rows
        for i in range(rows):
            sum_val = 0
            for j in range(cols):
                sum_val += (best[j] - df[i][j]) ** 2
            eb[i] = math.sqrt(sum_val)

        # dataset S- = ew
        ew = [0] * rows
        for i in range(rows):
            sum_val = 0
            for j in range(cols):
                sum_val += (worst[j] - df[i][j]) ** 2
            ew[i] = math.sqrt(sum_val)
            sum_p[i] = eb[i] + ew[i]

        score = [0] * rows
        for i in range(rows):
            score[i] = ew[i] / sum_p[i]

        return score

    def calc_rank(score):
        temp = [0] * len(score)
        rank = [0] * len(score)
        for i in range(len(score)):
            temp[i] = score[i]
        temp.sort()
        for i in range(len(score)):
            for j in range(len(temp)):
                if score[i] == temp[j]:
                    rank[i] = (len(rank) - (j))
        return rank

    def topsis(path, weights, impacts):
        # 'C:/Users/HP/Downloads/data.csv'
        df = pd.read_csv(path)
        weights = [float(w) for w in weights.split(',')]
        impacts = [i for i in impacts.split(',')]
        score = calc_score((df.iloc[:, 1:].values.tolist()), weights, impacts)
        df['Score'] = score
        rank = calc_rank(score)
        df['Rank'] = rank
        return df

    def mailME(result):
        gmail_user = 'parikabhandari@gmail.com'
        gmail_password = 'wstelywbtmhyrkrn'

        sent_from = gmail_user
        to = [res['email']]
        subject = 'Topsis Result'
        body = result

        email_text = """\
        From: %s
        To: %s
        Subject: %s

        %s
        """ % (sent_from, ", ".join(to), subject, body)

        try:
            smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtp_server.ehlo()
            smtp_server.login(gmail_user, gmail_password)
            smtp_server.sendmail(sent_from, to, email_text)
            smtp_server.close()
            print("Email sent successfully!")
        except Exception as ex:
            print("Something went wrong….", ex)

    weights = str(res['weights'])
    impacts = str(res['impacts'])
    main(file.filename, weights, impacts, 'result-file.csv')
    df = pd.read_csv('result-file.csv')
    mailME(df)
    return str(res)


if __name__ == '__main__':
    app.run(debug=True)
