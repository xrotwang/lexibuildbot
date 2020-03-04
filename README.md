# lexibuildbot



## setup master.

```shell
python -m venv env
source ./env/bin/activate

git clone https://github.com/SimonGreenhill/lexibuildbot.git
pip install -r lexibuildbot/requirements.txt

buildbot create-master -c lexibot.py lexibuildbot
buildbot start master
````

## setup a worker

```shell
buildbot-worker create-worker worker localhost worker pass
buildbot-worker start worker
```


## open UI

```shell
open http://localhost:8010
```


# Use UI:

* click on "builds -> builders" in left menu.
* select a repository
* click "force" button on top right
* start build

## Building all

* select "release" builder
* click "force" button on top right
* will trigger builds of all other repos


# TODO:

* parsing of errors/warnings?
