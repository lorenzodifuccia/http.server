import os
import logging
import secrets
import tarfile
import zipfile
import datetime
import mimetypes

import humanize
from flask import Flask, render_template, abort, request, session, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict',
)

logger = logging.getLogger("http.server")
logger.setLevel(logging.WARNING)


# Routing

@app.route('/')
@app.route('/<path:element>')
def view(element=""):
    path = os.path.realpath(os.path.join(app.config["FOLDER"], element))
    if (os.path.join(os.path.commonprefix((path, app.config["FOLDER"])), "") != app.config["FOLDER"]) \
            or not os.path.exists(path):
        return abort(404)

    session["CSRF-TOKEN"] = secrets.token_hex()

    if os.path.isdir(path):
        return render_template("listing.template", element=get_element(path, not len(element)))

    elif request.args.get("download"):
        return send_file(path, as_attachment=True)

    elif request.args.get("embed"):
        return send_file(path, as_attachment=False)

    return render_template("file.template", element=get_element(path))


@app.route('/upload', methods=['POST'])
def upload():
    if "CSRF-TOKEN" not in session:
        return {"status": False, "error": "Missing CSRF Token!"}

    file = request.files.get('file')
    path = os.path.realpath(request.form.get('path'))

    if not file or not path:
        return {"status": False, "error": "Missing parameters!"}

    if os.path.join(os.path.commonprefix((path, app.config["FOLDER"])), "") != app.config["FOLDER"]:
        return {"status": False, "error": "Invalid path!"}

    try:
        os.makedirs(path, exist_ok=True)
    except OSError as err:
        return {"status": False, "error": str(err)}

    filename = secure_filename(file.filename)
    file.save(os.path.join(path, filename))
    return {"status": True}


@app.route('/zip', methods=['GET', 'POST'])
def zip_utility():
    if "CSRF-TOKEN" not in session:
        return {"status": False, "error": "Missing CSRF Token!"}

    if request.method == "GET":
        path = os.path.realpath(request.args.get('path'))
        download_entry = request.args.get('entry')

    else:
        path = os.path.realpath(request.form.get('path'))
        download_entry = request.form.get('entry')

    if not path:
        return {"status": False, "error": "Missing parameter!"}

    if (os.path.join(os.path.commonprefix((path, app.config["FOLDER"])), "") != app.config["FOLDER"]) \
            or not os.path.exists(path) or not os.path.isfile(path):
        return {"status": False, "error": "Invalid path/file!"}

    zip_type = mimetypes.guess_type(path)
    try:
        if any(zip_type) and zip_type[0].endswith("tar") or zip_type[1] in ["gzip", "bzip2", "xz"]:
            tar_file = tarfile.open(path)

            if not download_entry:
                return {"status": True, "structure": parse_archive_infolist(tar_file.getmembers(), tar=True)}

            return send_file(tar_file.extractfile(tar_file.getmember(download_entry)),
                             download_name=download_entry, as_attachment=False)

        zip_file = zipfile.ZipFile(path)
        if not download_entry:
            return {"status": True, "structure": parse_archive_infolist(zip_file.infolist())}

        return send_file(zip_file.open(download_entry), download_name=download_entry, as_attachment=False)

    except (zipfile.BadZipFile, ValueError, OSError, Exception) as e:
        return {"status": False, "error": str(e)}


# Jinja Template Filters

@app.template_filter()
def datetime_format(value):
    dt = datetime.datetime.fromtimestamp(value)
    return dt.strftime('%d-%m-%Y %H:%M:%S')


@app.template_filter()
def datetime_humanize(value):
    dt = datetime.datetime.fromtimestamp(value)
    return humanize.naturaltime(dt)


# Functions

def get_element(path: str, is_root_directory=False):
    stat_result = os.stat(path)
    element = dict(name=os.path.basename(path), basedir=path, path=path, isroot=is_root_directory,
                   size=stat_result.st_size, mtime=stat_result.st_mtime,
                   ctime=stat_result.st_birthtime if hasattr(stat_result, "st_birthtime") else stat_result.st_ctime)

    if os.path.isdir(path):
        # Directory
        element.update(dict(children=[], isdir=True))
        children = []

        try:
            dir_list = os.listdir(path)
        except OSError:
            pass  # Ignore errors
        else:
            for child_name in dir_list:
                child_path = os.path.join(path, child_name)
                child_stat_result = os.stat(child_path)
                children.append(dict(name=child_name, path=child_path, isdir=os.path.isdir(child_path),
                                     size=child_stat_result.st_size, mtime=child_stat_result.st_mtime,
                                     ctime=child_stat_result.st_birthtime
                                     if hasattr(child_stat_result, "st_birthtime")
                                     else child_stat_result.st_ctime,
                                     mime=mimetypes.guess_type(child_name)[0]))

        element["children"] = sorted(children, key=lambda y: y["ctime"], reverse=True)

    else:
        # File
        mime = mimetypes.guess_type(path)
        element.update(dict(isdir=False, basedir=os.path.dirname(path), mime=mime[0] if mime[0] else mime[1]))

    return element


def parse_archive_infolist(infolist, tar=False):
    structure = dict()

    for file_info in infolist:
        current_structure = structure
        filename = file_info.filename if not tar else file_info.name
        for element in filename.split("/"):
            if element:
                if element not in current_structure:
                    current_structure[element] = {"_size": 0, "_path": ".", "_isdir": True}

                current_structure = current_structure[element]

        current_structure.update({
            "_size": humanize.naturalsize(file_info.file_size if not tar else file_info.size),
            "_path": filename,
            "_isdir": file_info.is_dir() if not tar else file_info.isdir(),
        })

    return structure


# Output
def after_request(response):
    timestamp = datetime.datetime.now().strftime('[%d-%m-%Y %H:%M:%S]')
    logger.info('%s %s %s %s %s', timestamp, request.remote_addr, request.method, request.full_path, response.status)
    return response


# Main

def main():
    import argparse
    import waitress

    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', default='127.0.0.1', help='Specify bind address [default: 127.0.0.1]')
    parser.add_argument('--port', default=8000, help='Specify server port [default: 8000]')
    parser.add_argument('--folder', default=os.getcwd(), help='Specify which directory to serve '
                                                              '[default: current working directory]')
    mode_args = parser.add_mutually_exclusive_group()
    mode_args.add_argument('--debug', default=False, action="store_true",
                           help='Use "flask.run" in Debug mode instead of "waitress" WSGI server')
    mode_args.add_argument('--no-output', default=False, action="store_true",
                           help='Disable server output (set logging.level >= WARNING)')

    args = parser.parse_args()

    app.secret_key = str(secrets.token_hex())
    app.config["FOLDER"] = os.path.join(os.path.realpath(os.path.expanduser(args.folder)), "")

    if not os.path.exists(app.config["FOLDER"]):
        return parser.error("folder does not exists")

    if args.debug:
        app.run(host=args.bind, port=args.port, debug=True)
        return

    elif not args.no_output:
        waitress_logger = logging.getLogger('waitress')
        waitress_logger.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        app.after_request(after_request)

    waitress.serve(app, host=args.bind, port=args.port, ident="http.server")


if __name__ == "__main__":
    main()
