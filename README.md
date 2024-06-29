---

<div align="center">
    
# UniChat - Your All-in-One Messaging Solution
<img src="https://github.zhaw.ch/UniChat/UniChat/blob/main/src/images/icons/unichat_logo.png">
    
</div>

---

We all know the feeling of having to use multiple messaging clients for communicating with friends and family. Currently a typical user uses applications like SMS, iMessage, WhatsApp, Signal, Threema, Telegram, Instagram the list goes on. The project proposal is to implement a WebClient, Desktop or mobile application to combine all these apps.

---

<h2>Table of Content</h2>
<ol>
    <li><a href=#introduction>Introduction</li>
    <li><a href=#installation>Installation</li>
    <li><a href=#integration>Integration of Chat Services</li>
        <ol>
            <li><a href=#whatsapp> WhatsApp Client Documentation</a></li>
            <li><a href=#instagram>Instagram Client Documentation</li>
        </ol>    
    <li><a href=#contribution>Contribution Guidelines</li>
    <li><a href=#done>Definition of Done</li>
    <li><a href=#code>Code Guidelines</li>
    <li><a href=#continous>Continuous Integration</li>
    <li><a href=#future>Roadmap / Future Development</li>
</ol>

---

<a id="introduction"></a><h2>Introduction</h2>
 
UniChat is a messaging solution developed using Python, designed to streamline communication by integrating various chat services into a single platform. With UniChat, users can access and manage multiple messaging platforms from one convenient application.

### User Guide / Current state

UniChat offers the following features:

**Login with phone number:**

<img align="left" src="https://github.zhaw.ch/UniChat/UniChat/blob/development/images/README/dummy1.PNG">

When you run the app, you will need to enter your phone number in the command line, as seen in the picture on the left, to log into the asynchronous Telegram client located in src/telegram_client.py. This asynchronous client is used by the Telethon event loop and will notify the main thread when a message is received from Telegram.

Additionally, the app creates a directory outside of UniChat at ~/unichat_user_data. This directory will store data from the Selenium component as well as the following Telethon and UniChat files:

* telethon_async.session (and telethon_async.session-journal)
* telethon_sync.session (and telethon_sync.session-journal)
* unichat.db

The Telethon session files and unichat.db should be kept private as they contain your Telegram session and personal messages. If you delete these session files, you will need to log into Telethon again. If you delete unichat.db, you will lose all data stored by the UniChat app.

**App Login Window:**

<img align="right" width="400" src="https://github.zhaw.ch/UniChat/UniChat/blob/development/images/README/dummy2.PNG">

After logging into the asynchronous Telegram client, the main app will start. It presents a Python QT window where you can sign up by entering your name to create an account, as shown in the picture on the right.

Currently, a web browser window will also appear due to Selenium, but this may be removed in a future update.

<br style="clear:both;"><br>

**Login with Telegram:**

<img align="left" src="https://github.zhaw.ch/UniChat/UniChat/blob/development/images/README/dummy3.PNG">

After signing up, you will see your account on the left and an empty window on the right. When you click on your account, two tabs will appear: one for Telegram and one for WhatsApp (WhatsApp is not functional at the moment).

You can log in to Telegram, as shown in the picture on the left. Once logged in, you will see your Telegram profile picture, and you can start adding contacts.

<br style="clear:both;"><br>

**Adding new contacts in UniChat:**

<img align="right" src="https://github.zhaw.ch/UniChat/UniChat/blob/development/images/README/dummy5.PNG">
<img align="right" src="https://github.zhaw.ch/UniChat/UniChat/blob/development/images/README/dummy4.PNG">

You can press the 'Add Contact' button and enter a name for the new contact. Each name can only be used once. After adding a new contact, you can link it to a Telegram contact.

When you press the Init Chat button, a list of your Telegram contacts will appear (currently, only those with whom you have active chats). After linking the contact, the contact's Telegram profile picture will be shown, and you will be ready to chat.

The messages you send and receive from this client will be stored in the database. Currently, the messages are not displayed in the correct order, but this issue is easy to fix.


**Messaging contacts:**

<img align="left"  width="500" height="416" src="https://github.zhaw.ch/UniChat/UniChat/blob/development/images/README/dummy6.PNG">

In the photo, the entire UniChat app is visible while chatting with a contact. On the left, all active contacts are displayed. When you click on one of the contacts, the chat with that contact opens. Above the chat window, you can choose which messaging app you want to use to chat with the contact. Sending and receiving messages works just like in the well-known messaging apps.

<br style="clear:both;"><br>
<br style="clear:both;"><br>
<br style="clear:both;"><br>
<br style="clear:both;"><br>
<br style="clear:both;"><br>
<br style="clear:both;"><br>

When you want to start over, you should delete everything except the 'telethon_async.session' file. Otherwise, you will have to log in from the command line again.

---

<a id="installation"></a><h2>Installation</h2>

This section describes how to set up the project and run it from the Bash Terminal. The same process can be used in the PyCharm IDE, which typically will automatically use the created virtual environment.

In PyCharm, you can go to 'Configure Interpreter,' then select the created virtual environment and the path to the script: src/main.py.

It is assumed that the most recent version of Python and other packages are used. The command 'python' refers to Python 3, and on older systems, you may need to use 'python3' instead of 'python'.

This app depends on Telegram Developer credentials, which should be stored in:

## Telethon setup

```
~/UniChat/.env

The file must contain two lines:

API_ID=1234
API_HASH='1234'

There should be no whitespaces around the equality symbol, an integer for the ID, and a string for the HASH. These credentials can be obtained here:
```
https://my.telegram.org/auth

## App setup with Bash Terminal 

```
cd ~/UniChat
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

## Chrome driver for selenium

The Chrome driver is essential because we are utilizing Selenium, which will be explained in more detail later on. The Chrome driver facilitates interaction between Selenium and the Chrome browser, enabling automated testing and web scraping functionalities.
The Chrome driver can be downloaded [here](https://developer.chrome.com/docs/chromedriver/downloads?hl=de).

## Testing

There is a directory ~/UniChat/private_tests with tests that require user credentials. These tests cannot be part of the continuous integration. The normal tests reside in ~/UniChat/tests and currently consist of Python unittest tests.
* Write code with testability in mind, using small functions and separation of concerns.
* Integration Tests?
* Acceptance Tests?

## Testing Setup
There is a bash script 'local_ci.sh' where you can execute the steps that will be executed on AppVeyor. If you just want to run the tests, you can use the following setup:
### Terminal Setup
Because the tests are not in the 'src' directory, we need to export the path to 'src/'. Nothing else is required, and the test files can use the same import statements as the files in 'src'.
```angular2html
cd ~/UniChat
export PYTHONPATH='src/'
python -m unittest discover -s tests
```
### Pycharm setup
Next to the green 'Run' button, go to 'Edit Configurations.' There, you can add a new configuration for "Python Unittests." Then you need to select:
* Target: `~/UniChat/tests`
* Working directory: `~/UniChat`
* Mark the 'src' directory as source root

This setup works on my machine and on AppVeyor. If it does not work on your machine, please double-check that you have set up everything correctly.

Common issues include:
* The name of the .env file: .env.txt instead of .env
* Using Python version 3.6 instead of 3.12

## GUI
Renamed dialog widgets from 'name_widget.py' to 'name_dialog.py' to indicate their use as widgets. Dialogs now use the accept/reject functionality.
```
if example_dialog.exec():
    print('dialog was accepted')
```

---

<a id="integration"></a> <h2>Integration of Chat Services</h2>

<img align="right" src="https://github.zhaw.ch/UniChat/UniChat/blob/development/images/README/WhatsAppLogo.png">

<a  id="whatsapp"></a>  <h3>WhatsApp Client Documentation</h3>

#### Basic Functionality

Our WhatsApp Client utilizes [the Selenium WebDriver](https://www.selenium.dev/) to scrape the [WhatsApp web client](https://web.whatsapp.com/) and perform the following functions in UniChat:

* Read all messages from a chat
* Send a message within a chat
* Retrieve all active chat names

#### Detecting HTML elements

In order to e.g. detect the messages or scroll through a chat to retrieve older messages, the UniChat WhatsApp Client uses the HTML class names of the required elements. This allows Selenium to find and interact with these elements. Currently, the class names of these elements are manually detected and stored inside the WhatsApp Client config file *`src.Selenium.WhatsApp.config`.

#### Login into WhatsApp web client

The WhatsApp web client uses a QR-Code as the login method, which needs to be scanned by the user's phone. Fortunately, the WhatsApp web client stores the QR-Code data reference inside the HTML, allowing the Selenium WebDriver to retrieve this code.

#### Persistent session

To keep the user logged into the WhatsApp web client, the browser session/User Data of the Selenium WebDriver is stored inside UniChat's data directory: `~/Unichat/User Data`

#### Navigating to a contact

The UniChat WhatsApp Client implementation uses the WhatsApp web client's search function to navigate between the chats. To achieve this, chat names are used as identifiers. These identifiers are stored inside a metadata JSON file within a UniChat contact's data directory: `~/UniChat/Chats/<contact name>/WhatsApp/metadata.json`

#### Reading older messages

To read older messages within a chat, a `scroll_to_top` function was implemented to automatically scroll as far up as possible. This continues until either the beginning of the chat history is reached or until older messages need to be downloaded from the phone. This ensures that the whole chat history is stored inside the HTML.

#### Current limitations

* The class-names of the HTML elements can change whenever the WhatsApp web client receives an update. **This will break the whole UniChat WhatsApp Client implementation!** The config file needs to be manually updated with the new class names.
* The UniChat WhatsApp Client implementation currently relies on ChromeDriver for the Selenium WebDriver. **Chrome needs to be installed in order to use the ChromeDriver.** Additionally, the ChromeDriver must be of the same major version as the installed Chrome. To address this issue, a DriverManager was implemented, which automatically downloads the correct ChromeDriver version.
* Currently, only non-Media messages are being detected by the UniChat WhatsApp Client implementation.

---

<img align="right" src="https://github.zhaw.ch/UniChat/UniChat/blob/development/images/README/InstaLogo.jpg">

<a id="instagram"></a> <h3>Instagram Client Documentation</h3>

#### Basic Functionality

Our Instagram Client utilizes [the Selenium WebDriver](https://www.selenium.dev/) to scrape the [Instagram Homepage](https://instagram.com/) and perform the following functions in UniChat:

* Read all messages from a chat
* Send a message within a chat
* Retrieve all active chat names

The Instagram Client operates in headless mode, similar to our WhatsApp Client implementation. Selenium enables us to simulate human actions, allowing the client to perform tasks as a human user would.

#### Login into Instagram Webpage

Our Selenium function loads the Instagram login page and dismisses any pop-ups. It then enters the login credentials into the appropriate fields and submits the form. Once Selenium detects a successful login, it returns the browser window with the user logged in. We save the browser data to provide more functionality to the user and reduce the need for repeated logins.

### Current Limitations

Instagram does not provide the exact timestamps for when messages are sent or delivered. Therefore, we must estimate the timeframe for these events.

Accessing elements on Instagram has proven more complex compared to WhatsApp, likely because messaging is not Instagram's primary focus.

### Detecting HTML Elements

We have designed our system to be easily maintainable. The necessary Instagram styling tags required to access the correct elements are stored in a config.py file. This file contains the relevant data needed to locate the appropriate elements on the interface.

---

<a id="contribution"></a> <h2>Contribution Guidelines</h2>

- **Branching:** Ensure you create a new branch for each feature or bugfix.

- **Commit Messages:** Use meaningful commit messages and follow any provided commit message conventions.

### Meaningful Conventions Guide

#### 1. Branching

Create a new branch for each Jira issue using the integrated Jira Git Integration. **Always ensure to branch from the [development-branch](https://github.zhaw.ch/UniChat/UniChat/tree/development)**. The integration will automatically create a branch with the following naming convention:

**Naming Conventions:**

- Feature Branches: `feature/UN-${issuekey}-${summary}`
- Bug Fix Branches: `bugfix/UN-${issuekey}-${summary}`
- Documentation Branches: `doc/UN-${issuekey}-${summary}`

**Examples:**

- `feature/UN-42-implement-whatsapp-client`
- `bugfix/UN-50-fix-config-in-whatsapp-client`
- `documentation/UN-69-write-pr-guidelines`

**Best Practices:**

- <ins>**Only merge back to the development branch upon completion and code review.**</ins>
- Keep branches focused—work on a single feature or fix per branch.

#### 2. Commit Messages

Commit messages should be concise yet comprehensive, reflecting the changes in a manner that allows other developers (or future-you) to comprehend the evolution of the project at a glance.

**Message Structure:**

- **Title**: A brief, straightforward summary of the changes, limited to 50 characters.
- **Body**: More detailed explanatory text, if necessary, separated from the title by a blank line and wrapped at 72
  characters.

**Commit Message Format:**

`<type>: <title>`

**Examples:**

- **feat**: implement user authentication
- **fix**: resolve data fetching issue #123
- **docs**: update the API endpoints section
- **test**: add unit tests for user login

**Commit Message Best Practices:**

- **Title**: Use the imperative, present tense: "add" not "added" nor "adds".
- Do not capitalize the first letter of the title.
- Do not end the title with a period.
- Use the body to explain the "what" and "why" of the commit, not "how".

---

<a id="done"></a> <h2>Definition of Done</h2>

The following guidelines ensure all tasks are completed to an acceptable standard:

### Code Implementation:
- All code implementation should follow the <a href=#code>Code Guidelines</a>.
- All implementations must undergo a code review conducted by a team member **who has not been directly involved in the implementation process**.
- After a user story has been implemented, a Pull-Request needs to be opened to merge the implementation into the `development` branch. **Any merge conflicts need to be resolved by the assignee**.

### Unit Testing:
- Unit tests need to **cover all testable function**.
- All Unit tests pass without errors or failures.
- If a function is deemed "**untestable**", it should be documented inside the User Story **with an explanation**.

### Documentation Tasks:
- All documentation tasks need to be checked and approved by either the Non-Tech-Lead ([Colin Vlahinkov](https://github.zhaw.ch/vlahkcol)), the Product Owner ([Philipp Marock](https://github.zhaw.ch/marocphi)) or the 
Scrum Master ([Aathavan Sivasothilinam](https://github.zhaw.ch/sivasaat)).

### Quality Assurance:
- After the code as been merged into the `development` branch, QA testing is performed to identify and address any defects or issues.
- A QA sign-off needs to be obtained in order to consider the user story complete.

### Product Owner Acceptance:
-   The user story is demonstrated to the Product Owner ([Philipp Marock](https://github.zhaw.ch/marocphi)).
-   The Product Owner confirms that acceptance criteria are met and approves the user story for release.

---

<a id="code"></a> <h2>Code Guidelines</h2>

### Naming Conventions
* **Class Names**: Use camel case (e.g., class NewClass)
* **Function Names**: Use lower case with underscores (e.g., def new_cool_function())
* **Constants**: Use all capital letters with underscores (e.g., TOTAL_MESSAGES = 32)

Note: There are exceptions to these rules. For instance, class HTTPServer is preferable to class HttpServer. Additionally, some libraries, particularly older ones, may use Java-style naming.

### Blank Lines
* Surround top-level function and class definitions with two blank lines.
* Surround method definitions inside a class with a single blank line.
* Use blank lines sparingly within functions to indicate logical sections.
* Ensure there is one blank line at the end of a Python file.
 
### Comments
Use docstrings for every function and class to enhance code readability and maintainability:
```
class Test:
    """ This is just an example """
    def __init__(self):
        pass

def test_function(n: int) -> bool:
    """ tests if n is even """
    return n % 2 == 0
```

### Type annotations
Always use type annotations to improve code clarity and assist static code analysis tools:
```
def divide_number(n: int) -> float:
    return n / 3
```
Instead of:
```
def divide_number(n): 
    return n / 3
```
Using type annotations helps programmers and static code analysis tools detect errors more effectively, similar to a compiled language.

### Code Style
* **Indentation:** 4 spaces
* **Maximal Line Length:** 79 characters
* **String Quotes:** Use single quotes ('this is a string') rather than double quotes ("this is another one")

Use this style:
```
if foo is not None:
    pass
```
Instead of:
```
if not foo is None:
    pass
```

Try to use string functions for common string operations:
```
foo = '_'.join(['word0', 'bar', 'yo'])
```
Instead of:
```
foo = 'word0' + '_' + 'bar' + '_' + 'yo'
```
Or:
```
if foo.startswith('f'):
    pass
```
Instead of:
```
if foo[0] == 'f':
    pass
```

from https://peps.python.org/pep-0008/

---

<a id="continous"></a> <h2>Continuous Integration</h2>

### Appveyor with yaml config

The YAML file needs to be in the root directory of the project and is used to configure the build process.

### Pylint for Checking Code Guidelines / Clean Code Principles

Pylint is a static code analysis tool for Python and can be configured with the file pylintrc.

### Testing

There is a pytest-qt tool for testing GUIs and pytest/unittest for unit tests.

### Sonarqube

http://160.85.252.61:9000/projects
Sonarqube is used for code quality and security checks. Login needs to be requested.

---

<a id="future"></a> <h2>Roadmap / Future Development</h2>

### Current State with Telegram:
* Incoming messages (received by UniChat) are stored in the database and loaded when the user restarts the app.
* Outgoing messages (sent from UniChat) are also stored and loaded.
* Messages sent from the phone/desktop client are currently ignored.

## Telethon

* Contact list is retrieved only once instead of loading it for every contact.
* Considerations for group chats and channels need to be addressed.

## GUI
* Contact items should move to the top when selected.
* Owners should be able to select a profile picture.
* The entire GUI should have a more polished appearance.
* Retrieve the contact list only once instead of loading it for every contact.
* Implement different themes.

## General
* Ensure information hiding: Users should only need input/output knowledge, not implementation details.
* Separate database and chat client code for a cleaner interface.
* Explore how Selenium clients can be effectively integrated and used.
* Address numerous unhandled exceptions (e.g., incorrect password).
* Implement pop-up error messages for better user feedback.
* Python path considerations (I primarily use the terminal; how does this work on Windows?) Ensure clear and effective setup solutions for demonstrations and reviews.

We welcome contributions from interested individuals who wish to further develop this project or implement new features. Feel free to share your ideas or additions with us.

### Get Involved

If you're interested in contributing to UniChat or have ideas for improvement, please don't hesitate to reach out to us. You can contact us via:

- Email: [UniChat](mailto:unichat_dev@hotmail.com)
- GitHub: [UniChat Repository](https://github.zhaw.ch/UniChat/UniChat)

---
