import collections

from github import Github

from buildbot.plugins import *

exclude = ['pylexibank', 'lexibank']


def iter_repos(org):
    return Github().get_organization(org).get_repos()


def get_name(repo):
    return repo.split("/")[-1].replace(".git", "")


repos = [r.clone_url for r in iter_repos('lexibank')]
repos = collections.OrderedDict(
    sorted([(get_name(r), r) for r in repos if get_name(r) not in exclude]))


# This is the dictionary that the buildmaster pays attention to. We also use
# a shorter alias to save typing.
c = BuildmasterConfig = {}
c['buildbotNetUsageData'] = None

####### WORKERS

# The 'workers' list defines the set of recognized workers. Each element is
# a Worker object, specifying a unique worker name and password.  The same
# worker name and password must be configured on the worker.
c['workers'] = [worker.Worker("worker", "pass")]

# 'protocols' contains information about protocols which master will use for
# communicating with workers. You must define at least 'port' option that workers
# could connect to your master with this protocol.
# 'port' must match the value configured into the workers (with their
# --master option)
c['protocols'] = {'pb': {'port': 9989}}

####### CHANGESOURCES

# the 'change_source' setting tells the buildmaster how it should find out
# about source code changes.  Here we point to the buildbot version of a python hello-world project.

c['change_source'] = [
    changes.GitPoller(
        repo,
        workdir='workdir.%s' % name,
        branch='master',
        pollInterval=300
   ) for name, repo in repos.items()]

####### SCHEDULERS

# Configure the Schedulers, which decide how to react to incoming changes.
c['schedulers'] = [
    schedulers.Triggerable(name="release", builderNames=[get_name(repo) for repo in repos]),
    schedulers.ForceScheduler(name="release-force", builderNames=['release'])
]

for name, repo in repos.items():
    c['schedulers'].extend([
        schedulers.SingleBranchScheduler(
            name=name,
            change_filter=util.ChangeFilter(branch='master'),
            treeStableTimer=None,
            builderNames=[name]
        ),
        schedulers.ForceScheduler(name="%s-force" % name, builderNames=[name]),
    ])

####### BUILDERS

# The 'builders' list defines the Builders, which tell Buildbot how to perform a build:
# what steps, and which workers can execute them.  Note that any particular build will
# only take place on one worker.

factory = util.BuildFactory()

c['builders'] = []

release = util.BuildFactory()
release.addStep(steps.Trigger(schedulerNames=['release'], waitForFinish=False))
c['builders'].append(util.BuilderConfig(name='release', workernames=["worker"], factory=release))

for name, repo in repos.items():
    factory = util.BuildFactory()

    # check out the source
    factory.addStep(steps.Git(repourl=repo, mode='full', method="fresh"))

    # install and upgrade
    factory.addStep(
        steps.ShellCommand(
            command=["pip", "install", "--upgrade", "."],
            workdir="build",
            env={"PYTHONPATH": "."},
            name="install dataset"
        )
    )
    factory.addStep(
        steps.ShellCommand(
            command=["pip", "install", "--upgrade", "pytest", "pytest-cldf"],
            workdir="build",
            env={"PYTHONPATH": "."},
            name="install tools"
        )
    )

    # make cldf
    # TODO.. need glottolog and concepticon
    # cldfbench lexibank.makecldf --glottolog-version v4.1 --concepticon-version v2.2.1 "${1}"
    #factory.addStep(
    #    steps.ShellCommand(
    #        command=["cldfbench", "lexibank.makecldf", "cldf/cldf-metadata.json"],
    #        workdir="build",
    #        env={"PYTHONPATH": "."},
    #        name="validate"
    #    )
    #)

    # validate
    factory.addStep(
        steps.ShellCommand(
            command=["cldf", "validate", "cldf/cldf-metadata.json"],
            workdir="build",
            env={"PYTHONPATH": "."},
            name="validate"
        )
    )
    # run tests
    factory.addStep(
        steps.ShellCommand(
            command=["pytest"], workdir="build",
            env={"PYTHONPATH": "."},
            name="pytest"
        )
    )

    # run checkss
    factory.addStep(
        steps.ShellCommand(
            command=["cldfbench", "--log-level", "WARN", "lexibank.check", name],
            workdir="build",
            env={"PYTHONPATH": "."},
            name="lexicheck"
        )
    )

    # add builder
    c['builders'].append(
        util.BuilderConfig(name=name, workernames=["worker"], factory=factory)
    )

####### BUILDBOT SERVICES

# 'services' is a list of BuildbotService items like reporter targets. The
# status of each build will be pushed to these targets. buildbot/reporters/*.py
# has a variety to choose from, like IRC bots.

c['services'] = []

####### PROJECT IDENTITY

# the 'title' string will appear at the top of this buildbot installation's
# home pages (linked to the 'titleURL').

c['title'] = "Lexibot"
c['titleURL'] = "https://lexibot.github.io/"

# the 'buildbotURL' string should point to the location where the buildbot's
# internal web server is visible. This typically uses the port number set in
# the 'www' entry below, but with an externally-visible host name which the
# buildbot cannot figure out without some help.

c['buildbotURL'] = "http://localhost:8010/"

# minimalistic config to activate new web UI
c['www'] = dict(
    port=8010,
    plugins=dict(waterfall_view={}, console_view={}, grid_view={})
)

####### DB URL

c['db'] = {
    # This specifies what database buildbot uses to store its state.
    # It's easy to start with sqlite, but it's recommended to switch to a dedicated
    # database, such as PostgreSQL or MySQL, for use in production environments.
    # http://docs.buildbot.net/current/manual/configuration/global.html#database-specification
    'db_url': "sqlite:///state.sqlite",
}
