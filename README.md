How to setup
===============================
1. ## get git repo
    1. ###### navigate to where repo will live
        `cd /path/to/project/folder`

   2. ###### pull repo
        `git pull https://github.com/BLCtbc/WORK_WORK`

2. ## selenium setup
    1. ###### download latest [chromedriver](https://chromedriver.chromium.org/downloads)
        make sure to put it in same folder/path as the git repo

    2. ###### create a folder where user profile will live
        `mkdir /path/to/project/folder/selenium`

3. ## setup virtual environment
    1. ###### ensure python 3.7.x is installed
        `which python3.7`

    2. ###### setup virtual environment:
        `python3.7 -m venv venv`

    3. ###### add required credentials/variables to source file [^1]
        - `$ echo "EXPORT SITE1_USERNAME=myusername" >> venv/bin/activate`
        - `$ echo "EXPORT SITE1_PASS=mys3cr3tp4$$w0rd" >> venv/bin/activate`

        [^1]: do for each website where a login is required

    4. ###### run the virtual environment:
        `source venv/bin/activate`

    5. ###### install requirements
        `pip install -r requirements.txt`

4. ## [setup google api credentials](https://developers.google.com/workspace/guides/create-credentials)
    - [create project](console.cloud.google.com/)
    - enable api(s)
    - [create credentials](https://console.cloud.google.com/apis/credentials/wizard) within project
    - download credentials file local project folder, name it 'credentials.json'
