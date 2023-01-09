# SocialMe
### Video Demo: 
### Description

This final project is my submission for the CS50 edX Harvard course. Please do not blindly copy this, as this violates the honor's code.

## Introduction

SocialMe is a social media web app. People can register their own account, they can write a status update, comment on other people's updates. Furthermore, there are two APIs embedded on the right which show recent news and the current weather. It is also possible to view other people's profiles, which lists their status updates including the comments written. Each user can upload their own profile picture, change their password or email. Each user can also delete their own postings or comments.

The project leaves room for improvement, as more  functionalities can be added or  extended. For example, a possible implementation could be direct messaging between users, adding friends and restricting the view of updates. Another addition could be to make the weather API be more dynamic and not hard coded.

However, even though these improvements show the project can always be extended more, the current version could allow small groups of people to connect on their own social media plattform without too much effort.

## Stack used

SocialMe is a small application run with Python/Flask as backend. It uses sqlite3 as a database, and makes use of HTML, CSS, and JavaScript on the frontend. The project uses Bootstrap for its visual styling and responsiveness, but adds own CSS styling.

## Challenges and design choices

I chose to build a simple web app since I want to focus my career on web development. My main issue was the length of app.py - as the file grew, it was harder to really know what is going on. It would probably be of interest to split the code in smaller parts if the project were to be expanded.

# Set up and running

To run SocialMe, three things are required:

- The database: You can use database.sql to set the database up. You can then register your own account(s) and start posting.
- A [NewsAPI](https://newsapi.org/) API key
- An [OpenWeather](https://openweathermap.org/api) API key

Once you have set up your API keys, export the OpenWeather API key:

`export OPENWEATHER=API_KEY`

Then, export the news API key:

`export NEWS=API_KEY`

Then run flask:

`flask run`

# Files description

## app.py

Most of the backend is written in the app.py file. It uses the Flask routing to enable the different routes. If the project grew and bigger, it could be a consideration to split this file up even more into their single components and import the route implementations.

## helpers.py

The helpers file contains a few functions which are not part of the routing. They help to format the timestamp correctly or check if the uploaded profile picture is not malicious.

## database.sql

Database.sql includes all the required SQL tables needed to run SocialMe.

## static/checkuser.js

When registering a new account, SocialMe utilises checkuser.js to check whether the account fulfills certain criteria, such as the length of the username and if the username isn't taken yet. To do so, we utilise a self-written API, which is just a routing path in app.py and which returns a JSON file. If the username is unavailable, the app displays an error.

However, since this check only occurs on the frontend, we also need to implement it in the backend, because it would be possible to change the DOM manually and then submit user data. This is done in app.py

## static/styles.css

SocialMe only uses one single CSS file, but as the project would grow bigger, it would be advisable to split the code into smaller files to make the app faster.

## static/public/

The public folder contains all the uploaded profile pictures.

## templates/

The templates folder contains all the files we need to display the webpage. The frontend coding is done in these files. I decided to split the code into its components to ensure a better overview, but this would also enable several people to work on the project at the same time.

## templates/layout.html

This is the main templating file, the base construction of the webpage. It uses jinja to include different files, depending on whether the user is logged in.

## templates/error.html

This template can be implemented to display a warning or an error, including a customized message. This is useful for errorchecking.

## templates/Start/

This folder contains the main static files for SocialMe:

- footer.html => Self-explanatory: This files contains the footer with its relevant information.
- login_field.html => The HTML with the form to submit your login.
- login.html => similar to login_field.html, but used in different scenarios.
- navigation.html => This is the navbar at the top of the page. The navigation bar shows different elements, depending whether you are logged in or not.
- register.html => The frontend part to register your own account.

## templates/Feed/

This folder contains the news feed for SocialMe. There are two files:

- feed.html => This file renders the news feed with the comments
- update_header.html => This shows the update field on top of the news feed, where users can input their own status updates.

## templates/Profile/

The profile folder contains all relevant files to display and change the profile.

- profile.html => Displays the profile. If the user is looking at a userID that doens't exist, an error message will be displayed. If the user is looking at his own profile, he can post a status update.
- settings.html => Allows the user to change his settings, such as password, profile picture, or email.

## templates/Sidebar/

The sidebar folder contains the left and right sidebar elements.

- sidebar_profile.html => shows the left sidebar. Currently the weather component sits in here. This file could potentially be expanded with more, dynamic information, if the project gets expanded.
- weather.html => the weather component, displaying the data we got from the API.
- sidebar.html => The overall right sidebar.
- news.html => the news components, processing the data from the API call
