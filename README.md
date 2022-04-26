# tulr
turl - track url - is a simple page monitor that communicates events to kafka


## What is the goal of turl?

Turl - **t**rack **url** - is a simple utility that takes a set of urls and fetches key statistics about them, such as response time, status
code and content matching via regular expressions. Information gathered by Turl is sent over kafka and persisted into
storage by a consumer sink.


## How to install and run turl?

1. Installing from git

Clone the repository and make sure you have poetry installed. You can do that by typying in the command line

```shell
    poetry --version
```

and you should see the following output __Poetry version X.Y.Z__. If the command fails, please [install poetry according
to the package's documentation][poetry_docs].

If poetry is already installed run

```shell
    poetry install
```

You can start the tool through a script entrypoint, using the run command and providing a configuration file


```shell
    poetry run turl --configuration ./path/to/config/file.yaml
```

2. Installing from pypi through pip (to be added)

Open your shell and type

```shell
    pip install turl
```

The package will install turl's entrypoint on your shell which you can invoke using


```shell
    turl --configuration ./path/to/config/file.yaml
```

## Configuration

Turl's configuration consists of a simple yaml file where you provide a kafka broker address and optionally a list
of websites to track [(see an example from turl.yam)](./turl.yaml).

## Sinks

Turl's results can be written to a storage engine through a turl sink. Currently only postgres is supported.

### Launching postgresql sink

The postgresql sink is available through a shell entrypoint. Ensure that turl is installed and then launch the
sink using

```shell
    turl_pg_sink --configuration ./path/to/config/file.yaml
```

The configuration file will need to have the necessary details on how to access pg, including user, database, host
and password. Turl also expects the [schema to be pre-populated on your database](./services/postgres).


## Connecting to Aiven

When connecting to Aiven you need to make sure the encryption options are set correctly and that you have your
secrets locally available (this repo expects them to be added inside a folder called secrets on the repo's root).

When connecting to kafka on aive using certificates, ensure that the host address is set to aiven and that
the path to the keys and certificate files is correct

```yaml
    bootstrap.servers: host.at.aiven:port
    security.protocol: "SSL"
    ssl.certificate.location: "/secrets/service.cert"
    ssl.key.location: "/secrets/service.key"
    ssl.ca.location: "/secrets/ca.pem"
```

The postgres sink should also have the user, password and host updated accordingly.


## Services

The repo contains several compositions under the [services folder](./services) which allow you to start postgres, kafka
and helpers to help you interface with them, such as adminer and akhq.

To launch each service point docker-compose at the compose file inside the service folder and start it with the **up**
command. In some services, the base image is customized to fit the needs of the project and for that you should also
build the image.

Here's an example on how to launch and build the postgres service

```
    docker-compose -f service/postgres/docker-compose.yaml up -d --build
```

As a shortcut you can launch all services and turl's tracker and sink by executing the [launch.sh file](./launch.sh).


## Future work

The idea of Turl is something I came up when reading the assignment for the first time. I wanted to show with it that I
often like  to think how can I make my software easy and ready to use by others. I really enjoy having the
possibility to clone and  run the infrastructure end to end.

I also wanted to take this opportunity to learn something new and that was the main reason I took in use asyncio. It
is something I have not used a lot in Python and wanted to get a feel of where it stands these days. Similarly,
some choices with pg were also done to recall some concepts, such as triggers despite not being the most ideal
solution for the problem (eg, wasteful url replicated all the time).

As it was requested to not spend too much time on build scripts and whatnot I tried not to put too much work on that, but
in the repo you can find compositions to launch all the infra pieces on the developers' machine with minimal effort. These
are also key for ensuring good tests of the framework.

I have added some basic ci/cd checks that run the turl tests and pre-commit actions against all files. Much more could
be done towards code coverage, quality analysis, among others.

The end to end test should have a kafka consumer which tracks the messages that the sink should be writting. These messages
should be asserted from the db. At the moment I did not have the async loop exposed to the consumer, thus making it a
bit more difficult to instanciate and run the turl's consumer from the tests. Regardless of that, improving the test
case with that functionality would make the test much more reliable.

## Powered by:

* [aiohttp][aiohttp]
* [confluent kafka python][confluent_kafka_python]

[poetry_docs]: https://python-poetry.org/docs/

[aiohttp]: https://docs.aiohttp.org/en/latest/index.html
[confluent_kafka_python]: https://github.com/confluentinc/confluent-kafka-python
