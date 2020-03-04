# lexibuildbot


## setup master.

```shell
python -m venv env
source ./env/bin/activate
pip install 'buildbot[bundle]'

buildbot create-master master

cp lexibot.cfg master/master.cfg

buildbot start master
````

## setup a worker

```shell
# either in this venv or a new one.
pip install buildbot-worker
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



# TODO:

* write code to get all repositories and load into lexibot.cfg
* parsing of errors/warnings?
* figure out how to run all at once rather than manually. 
