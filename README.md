# Palestine Israel Twitter and Media Analysis

Expert.ai hackathon submission which uses Twitter data to interpret Palestine-Israel sentiment and opinion. At the time 
of submission this site can be found deployed on [AWS](http://18.169.146.101).

This website relies on data being mined and processed, but I have purposefully excluded this data from 
the repository to keep it small and comply with the terms and conditions of my Twitter API application.

## Getting Started

All `pip` requirements are found in `requirements.txt`. GeckoDriver needs to be installed for web scraping websites that
use JavaScript. 

To run the Dash application, one can simply run `python3 app.py` although this may not work for you unless you have
mined and analyzed the data.

## Structure

The code is categorized by function in separate packages:

* `analyis` covers all code that cleans the data and analyzes it by calling the expert.ai endpoints.
* `components` is where Dash figures are created.
* `scraping` is all the code that scrapes media article URLs and pulls Twitter data.
* `text` contains all the Dash website text paragraphs

`config.template` needs to be copied to a file called `config.py` to become effectively used by the application.