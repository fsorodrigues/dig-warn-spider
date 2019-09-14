# Contents
## `./chromedriver`
Selenium depends on this file. I usually keep it in the root folder of every project, but you could set it up elsewhere as long as you change the path in the script (line 52).

## `./email_utils`, `./object_utils`, `./extract_utils`
Utility functions I decided to spinoff into a separate files.

## `./scraper.py`
The scraper itself.

Honestly, it's quite long and there are more actions that could be turned into functions to reduce redundancy.

See Selenium [documentation](https://selenium-python.readthedocs.io) for additional information.  

## `./.env`  
Sets environment variables that will loaded with `dotenv`.

## `./run-scraper.sh` (optional)
I use a bash script be able to call the script as a cronjob from a Python virtual environment. It would look somewhat like this:
```bash
#!/bin/bash
cd /absolute/path/to/root
PATH=$PATH:/absolute/path/to/virtual/env/bin/
export PATH
python ./scraper.py
```
Remember you're probably going to have to make the scripts executable with `chmod +x path/to/script`.
