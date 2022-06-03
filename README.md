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


## Powered by:

* [aiohttp][aiohttp]
* [confluent kafka python][confluent_kafka_python]

[poetry_docs]: https://python-poetry.org/docs/

[aiohttp]: https://docs.aiohttp.org/en/latest/index.html
[confluent_kafka_python]: https://github.com/confluentinc/confluent-kafka-python
