# http.server 
A (_beautiful_) replacement for the `http.server` Python3 module.  

Features:
- File download 🤷‍♂️
- File **upload** 🤩
- **Preview** (pdf, text, image, music, **video**) 🧐
- List files in `.zip` and `.tar` archives remotely, with the ability to **view** or **download** a single entry 😮
- **Mobile-friendly** 🤳


## Example
<p align="middle"><img src="https://github.com/lorenzodifuccia/cloudflare/raw/master/Images/http.server/listing.png" title="Directory listing" width="80%" /></p>

- **Preview**:
<p align="middle"><img src="https://github.com/lorenzodifuccia/cloudflare/raw/master/Images/http.server/preview.gif" title="Preview" width="80%" /></p>

- **Mobile**:
<p align="middle"><img src="https://github.com/lorenzodifuccia/cloudflare/raw/master/Images/http.server/mobile.gif" title="Mobile" height="600px" /></p>

<br/><br/>

> _Dev Tips_: force to view a zip-like file by passing `#zip` in the URL 😉
<p align="middle"><img src="https://github.com/lorenzodifuccia/cloudflare/raw/master/Images/http.server/zip-like.gif" title="Listing" width="80%" /></p>

<br/>

## Usage
After installation (`pip3 install http-server`, see below), run:
```bash
$ # to serve current working directory, on 127.0.0.1:8000
$ http.server

$ http.server --bind 0.0.0.0 --port 8080 --folder ~/Downloads

$ http.server -h
usage: http.server [-h] [--bind BIND] [--port PORT] [--folder FOLDER]
                   [--debug | --no-output]

optional arguments:
  -h, --help       show this help message and exit
  --bind BIND      Specify bind address [default: 127.0.0.1]
  --port PORT      Specify server port [default: 8000]
  --folder FOLDER  Specify which directory to serve [default: current working
                   directory]
  --debug          Use "flask.run" in Debug mode instead of "waitress" WSGI
                   server
  --no-output      Disable server output (set logging.level >= WARNING)
```

> ### **ATTENTION**: this program is meant to be run locally, do not expose on Internet!

<br/>

## Installation
As easy as:
```bash
$ pip3 install http-server
```

Otherwise:
```bash
$ # (Optional)
$ virtualenv venv && source venv/bin/activate

$ git clone https://www.github.com/lorenzodifuccia/http.server
$ cd http.server
$ pip install .

$ python3 -m http_server ...
OR
$ http.server ...
```

This project has the following dependencies:
- Python3 (see [`requirements.txt`](requirements.txt))
    - Flask [[link](https://flask.palletsprojects.com/en/2.2.x/)]
    - Waitress [[link](https://docs.pylonsproject.org/projects/waitress/en/stable/index.html)]
    - Humanize [[link](https://github.com/python-humanize/humanize)]
- HTML5
    - Bootstrap 5 (CSS + JS) [[link](https://getbootstrap.com/docs/5.2/getting-started/introduction/)]
    - Bootstrap Icons [[link](https://icons.getbootstrap.com/)]

<br/>

## Future
Known issues:
- HTML5 and Browsers do not fully support `.mkv` files

<br/>

Made with <3 by [me](https://www.github.com/lorenzodifuccia)
