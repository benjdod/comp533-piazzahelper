# COMP 533 Piazza Helper

This is a helper script that attempts to automate creating and updating your Piazza diary for COMP 533 with Selenium. 

## Some Notes

 - ℹ️ this driver has only been tested on Google Chrome. It can be modified to use a different browser pretty easily but results may vary.

 - ⚠️ make a backup of your diary before using this script. Although it has been tested and worked on, I can make no guarantees for your data's safety, so better safe than sorry!


## Getting Started

#### Your First Time

0. (optional) activate your favorite python virtual environment
1. Run `pip install -r requirements.txt` to install Selenium
2. Download a driver for your web browser (here's [Chrome's driver](https://chromedriver.chromium.org/downloads))
3. Create a new file in the root directory called `config.json` and fill out with the fields in `example-config.json`. I've included my config file as an example.
4. Run `helper.py import` to backup and import your current diary to your machine. After this step, inspect the files in your class directory to make sure there were no errors, and fix any that may have arose. 

#### Before Class

 - Run `helper.py maketoday` to generate a new file where you write your QAs for the day's class

#### After Class

 - Run `helper.py commit` to push all your local classes to Piazza. 

## How It Works

The script imports your diary and splits it into a series of files for each class day. Each file is a text file where each pair of lines represents a question-answer pair, like the following:

```
What is the meaning of life, the universe and everything?

42

Can you answer this question?

No I have no idea
```

So when you do `import`, the script parses your diary and splits it out into these files by day. And when you `commit` to your diary, the script uses these files to write the QA pairs with proper formatting and stuff. 