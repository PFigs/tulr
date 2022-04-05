# tulr
turl - track url - is a simple page monitor that communicates events to kafka


## What is the goal of turl?

Turl - **t**rack **url** - is a simple utility that takes a set of urls and fetches key statistics about them, such as response time, status
code and content matching via regular expressions. Information gathered by Turl is sent over kafka and persisted into
storage by a consumer sink.

Latter version of Turl will support more metrics which will be gathered through standard api services, such as
Google's page speed insights.


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

2. Installing from pypi through pip

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
of websites to track.

If the list of websites to track is not given, then turl will wait on a kafka topic to receive its topic configuration.


## Powered by:

* [aiohttp][aiohttp]
* [confluent kafka python][confluent_kafka_python]



[poetry_docs]: https://python-poetry.org/docs/

[aiohttp]: https://docs.aiohttp.org/en/latest/index.html
[confluent_kafka_python]: https://github.com/confluentinc/confluent-kafka-python
