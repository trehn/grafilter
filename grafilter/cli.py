from subprocess import Popen


def main(*args):
    run()


def run():
    gunicorn = Popen(
        "gunicorn grafilter.flask:app",
        shell=True,
    )
    gunicorn.communicate()
