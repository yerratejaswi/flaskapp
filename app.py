from flask import Flask,Response,jsonify, render_template ,logging,request,send_file
app = Flask(__name__)
import sys
import os
from flask_cors import CORS
import requests
from datetime import datetime, timedelta
import pandas as pd
from pandas import DataFrame, Series


import github3, json
import numpy as np

import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for non-interactive environments
import matplotlib.pyplot as plt

# Initilize flask app
app = Flask(__name__)
# Handles CORS (cross-origin resource sharing)
CORS(app)

# Add response headers to accept all types of  requests
def build_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods",
                         "PUT, GET, POST, DELETE, OPTIONS")
    return response

# Modify response headers when returning to the origin
def build_actual_response(response):
    response.headers.set("Access-Control-Allow-Origin", "*")
    response.headers.set("Access-Control-Allow-Methods",
                         "PUT, GET, POST, DELETE, OPTIONS")
    return response

github_token = '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'
repos = ["openai/openai-cookbook", "openai/openai-python", "elastic/elasticsearch",
         "milvus-io/pymilvus", "sebholstein/angular-google-maps"]

@app.route('/')
def home():
    return {"message": 'Hello world!'}

#returns the Forks and Stars from the list of repos given through Github API
@app.route('/forksandstars')
def get_github_forks_and_stars_count():

    forks_and_stars = []

    for repo_string in repos:
        repo_split = repo_string.split('/')
        owner = repo_split[0]
        repo = repo_split[1]
        base_url = f"https://api.github.com/repos/{owner}/{repo}"

        # Set up headers with authentication token
        headers = {'Authorization': f'token {github_token}'}

        # Get repository information (forks, stars)
        repo_response = requests.get(base_url, headers=headers)
        repo_info = repo_response.json()

        info = {
        'repository': repo_string,
        'forks': repo_info['forks_count'],
        'stars': repo_info['stargazers_count']
        }
        forks_and_stars.append(info)

        #converting the json response to dataframe for plotting charts
        df = pd.DataFrame(forks_and_stars)

        #plot bar chart for forks
        plt.bar(df['repository'], df['forks'], color=['red', 'yellow', 'blue', 'purple', 'green', 'pink', 'orange'])
        plt.xlabel('Repository')
        plt.ylabel('Number of Forks')
        plt.title('Number of Forks for Each Repository')
        plt.xticks(rotation=90)
        plt.savefig('images/forks.png', bbox_inches='tight', pad_inches=0.1)

        #plot bar chart for stars
        plt.bar(df['repository'], df['stars'], color=['red', 'yellow', 'blue', 'purple', 'green', 'pink', 'orange'])
        plt.xlabel('Repository')
        plt.ylabel('Number of Stars')
        plt.title('Number of Stars for Each Repository')
        plt.xticks(rotation=90)
        plt.savefig('images/stars.png', bbox_inches='tight', pad_inches=0.1)


    return jsonify(forks_and_stars), 200

@app.route('/fetch/forks')
def fetch_forks():
    # Specify the path to your image file
    image_path = 'images/req-4.png'

    # Return the image as a response
    return send_file(image_path, mimetype='image/png')

@app.route('/fetch/stars')
def fetch_stars():
    # Specify the path to your image file
    image_path = 'images/req-3.png'

    # Return the image as a response
    return send_file(image_path, mimetype='image/png')

@app.route('/fetch/issuesline')
def fetch_issuesline():
    # Specify the path to your image file
    image_path = 'images/req-1.png'

    # Return the image as a response
    return send_file(image_path, mimetype='image/png')

@app.route('/fetch/issues/created/repo=<int:repo>')
def fetch_issues_created(repo):
    # Specify the path to your image file
    image_path = f'images/req-2.{repo}.png'

    # Return the image as a response
    return send_file(image_path, mimetype='image/png')

@app.route('/fetch/issues/closed/repo=<int:repo>')
def fetch_issues_closed(repo):
    # Specify the path to your image file
    image_path = f'images/req-5.{repo}.png'

    # Return the image as a response
    return send_file(image_path, mimetype='image/png')

@app.route('/fetch/issues/stacked')
def fetch_issues_stacked():
    # Specify the path to your image file
    image_path = f'images/req-6.png'

    # Return the image as a response
    return send_file(image_path, mimetype='image/png')

@app.route('/importissues')
def import_issues():
    main_data = {}
    gh = github3.login(token=github_token)

    f = open('issues.json', 'w')

    # two_months_ago = datetime.now() - timedelta(days=60)

    for repo_url in repos:
        repo_split = repo_url.split("/")
        repo_owner = repo_split[0]
        repo_name = repo_split[1]
        for issue in gh.search_issues(repo_owner, repo_name):          # Find issues from given Repo
            label_name=[]
            data={}
            current_issue = issue.as_json()
            current_issue = json.loads(current_issue)
            data['issue_number']=current_issue["number"]                          # Get issue number
            data['created_at']= current_issue["created_at"][0:10]                 # Get created date of issue
            if current_issue["closed_at"] == None:
                data['closed_at']= current_issue["closed_at"]
            else:
                data['closed_at']= current_issue["closed_at"][0:10]               # Get closed date of issue
            for label in current_issue["labels"]:
                label_name.append(label["name"])                                  # Get label name of issue
            data['labels']= label_name
            data['State'] = current_issue["state"]                                # It gives state of issue like closed or open
            data['Author'] = current_issue["user"]["login"]                       # Get Author of issue
            out=json.dumps(data)# save this all information to a JSON file
            # main_data = data
            # print(main_data)
            f.write(out+ '\n')
    f.close()
    return {"message": "successfully imported"}, 200

# get: /importissues must be executed before this API is called
@app.route('/getlasttwomonthissues')
def getlasttwomonthissues():
    list_of_issues_dict_data = [json.loads(line) for line in open('issues.json')]
    issues_df = DataFrame(list_of_issues_dict_data)
    wrangled_issues_df = issues_df[['repository','Author','State','closed_at','created_at','issue_number','labels']]
    wrangled_issues_df.loc[0:len(wrangled_issues_df), 'OriginationPhase']= np.NaN
    wrangled_issues_df.loc[0:len(wrangled_issues_df),'DetectionPhase']= np.NaN
    wrangled_issues_df.loc[0:len(wrangled_issues_df),'Category']= np.NaN
    wrangled_issues_df.loc[0:len(wrangled_issues_df),'Priority']= np.NaN
    wrangled_issues_df.loc[0:len(wrangled_issues_df),'Status']= np.NaN
    for i in range(0, len(wrangled_issues_df)):
        if wrangled_issues_df.iloc[i]['labels']:
            for label in wrangled_issues_df.iloc[i]['labels']:
                if len(label.split(':')) == 2:
                    label_name= (label.split(':'))[0]
                    label_value= (label.split(':'))[1]
                    wrangled_issues_df.loc[i, label_name]=label_value
    wrangled_issues_df['closed_at'] = pd.to_datetime(wrangled_issues_df['closed_at'])

    # Get the current date and the date 2 months ago
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)

    #Filter the DataFrame based on the 'closed_at' column
    filtered_df = wrangled_issues_df[(wrangled_issues_df['closed_at'] >= start_date) & (wrangled_issues_df['closed_at'] <= end_date)]

    return filtered_df.to_json(orient='records'), 200

@app.route('/weeklyclosedissues')
def weekly_closed_issues():
    GITHUB_URL = f"https://api.github.com/"
    headers = {
        "Authorization": f'token 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'
    }
    params = {
        "state": "closed"
    }

    today = date.today()

    issues_reponse = []
    # Iterating to get issues for every week for the past 8 weeks
    for i in range(8):
        issues_closed_data = []
        current_week_end = today
        for repo in repos:
            last_month = current_week_end + dateutil.relativedelta.relativedelta(weeks=-1)
            types = 'type:issue'
            repo = 'repo:' + repo
            ranges = 'closed:' + str(last_month) + '..' + str(current_week_end)
            per_page = 'per_page=100'
            search_query = types + ' ' + repo + ' ' + ranges

            query_url = GITHUB_URL + "search/issues?q=" + search_query + "&" + per_page
            search_issues = requests.get(query_url, headers=headers, params=params)
            search_issues = search_issues.json()
            issues_items = []
            try:
                issues_items = search_issues.get("items")
            except KeyError:
                error = {"error": "Data Not Available"}
                resp = Response(json.dumps(error), mimetype='application/json')
                resp.status_code = 500
                return resp
            if issues_items is None:
                continue
            for issue in issues_items:
                label_name = []
                data = {}
                current_issue = issue
                data['issue_number'] = current_issue["number"]
                data['created_at'] = current_issue["created_at"][0:10]
                if current_issue["closed_at"] is None:
                    data['closed_at'] = current_issue["closed_at"]
                else:
                    data['closed_at'] = current_issue["closed_at"][0:10]
                for label in current_issue["labels"]:
                    label_name.append(label["name"])
                data['labels'] = label_name
                data['State'] = current_issue["state"]
                data['Author'] = current_issue["user"]["login"]
                issues_reponse.append(data)

            issues_closed_data.append({'repository': repo, 'issues_closed_count': len(issues_reponse)})

        today = last_month
        weekly_issues_df = pd.read_json('./issues_closed_weekly.json')
        for week in range(8):
            repositories = []
            closed_issues_count = []
            for repo in range(15):
                repositories.append(weekly_issues_df[repo][week]['repository'])
                closed_issues_count.append(weekly_issues_df[repo][week]['issues_closed_count'])
            #plot barchart:
            plt.bar(repositories, closed_issues_count, color=['red', 'yellow', 'blue', 'purple', 'green', 'pink', 'orange'])
            plt.xlabel('Repository')
            plt.ylabel('Number of Issues Closed')
            plt.title(f'Week 1: {dates[week][0]} to {dates[week][1]}')
            plt.xticks(rotation=90)
            plt.savefig(f'images/issue_closed_week{week+1}.png', bbox_inches='tight', pad_inches=0.1)

@app.route('/monthlycreatedissues')
def monthly_created_issues():
    GITHUB_URL = f"https://api.github.com/"
    headers = {
        "Authorization": f'token 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'
    }
    params = {
        "state": "open"
    }
    repository_url = GITHUB_URL + "repos/" + repo_name
    # Fetch GitHub data from GitHub API
    repository = requests.get(repository_url, headers=headers)
    # Convert the data obtained from GitHub API to JSON format
    repository = repository.json()

    today = date.today()

    issues_reponse = []
    # Iterating to get issues for every month for the past 12 months
    for i in range(2):
        last_month = today + dateutil.relativedelta.relativedelta(months=-1)
        issues_reponse = []
        repositories = []
        issues_created_count = []
        # print(f'Month {i+1}: {str(last_month)} to {str(today)}')
        yaxis_title = f'Month {i+1}: {str(today)} to {str(last_month)}'
        for repo_link in repos:
            types = 'type:issue'
            repo = 'repo:' + repo_link
            ranges = 'created:' + str(last_month) + '..' + str(today)
            # By default GitHub API returns only 30 results per page
            # The maximum number of results per page is 100
            # For more info, visit https://docs.github.com/en/rest/reference/repos 
            per_page = 'per_page=100'
            # Search query will create a query to fetch data for a given repository in a given time range
            search_query = types + ' ' + repo + ' ' + ranges

            # Append the search query to the GitHub API URL 
            query_url = GITHUB_URL + "search/issues?q=" + search_query + "&" + per_page
            # requsets.get will fetch requested query_url from the GitHub API
            search_issues = requests.get(query_url, headers=headers, params=params)
            # Convert the data obtained from GitHub API to JSON format
            search_issues = search_issues.json()
            issues_items = []
            try:
                # Extract "items" from search issues
                issues_items = search_issues.get("items")
            except KeyError:
                error = {"error": "Data Not Available"}
                resp = Response(json.dumps(error), mimetype='application/json')
                resp.status_code = 500
                return resp
            if issues_items is None:
                continue
            for issue in issues_items:
                label_name = []
                data = {}
                current_issue = issue
                # Get issue number
                data['issue_number'] = current_issue["number"]
                # Get created date of issue
                data['created_at'] = current_issue["created_at"][0:10]
                if current_issue["closed_at"] == None:
                    data['closed_at'] = current_issue["closed_at"]
                else:
                    # Get closed date of issue
                    data['closed_at'] = current_issue["closed_at"][0:10]
                for label in current_issue["labels"]:
                    # Get label name of issue
                    label_name.append(label["name"])
                data['labels'] = label_name
                # It gives state of issue like closed or open
                data['State'] = current_issue["state"]
                # Get Author of issue
                data['Author'] = current_issue["user"]["login"]
                issues_reponse.append(data)
            repositories.append(repo_link)
            issues_created_count.append(len(issues_reponse))
            # print('repo name created: ', len(issues_reponse))

        today = last_month
        #plot barchart:
        plt.bar(repositories, issues_created_count, color=['red', 'yellow', 'blue', 'purple', 'green', 'pink', 'orange'])
        plt.xlabel('Repository')
        plt.ylabel('Number of Issues Created')
        plt.title(yaxis_title)
        plt.xticks(rotation=90)
        plt.savefig(f'issue_created_month{i+1}.png', bbox_inches='tight', pad_inches=0.1)
        plt.show()
    return issues_reponse

#line chart for issues closed:
@app.route('/linechartissuesclosed')
def linechartissuesclosed():
    url = f'https://api.github.com/repos/{repo_name}/issues'
    headers = {
        'Authorization': f'token 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',
        'Accept': 'application/vnd.github.v3+json'
    }

    total_issues = 0
    page = 1

    while True:
        params = {'page': page, 'per_page': 500}  # Adjust per_page as needed
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            issues_data = response.json()
            if not issues_data:
                break  # No more issues, exit the loop
            total_issues += len(issues_data)
            page += 1
        else:
            print(f"Error: {response.status_code}")
            return None
    plt.plot(repos, issues_count, marker='o', linestyle='-')

    # Adding labels and title
    plt.xlabel('Repository')
    plt.ylabel('Number of Issues')
    plt.title('Issues Count by Repository')

    # Rotating x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    plt.savefig(f'issues_line_chart.png', bbox_inches='tight', pad_inches=0.1)
    return issues_data, 200

#run server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
