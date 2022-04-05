from .pg.postgres_sink import main as pg_main
from .turl import main as turl_main


def entrypoint_turl():
    turl_main()


def entrypoint_pg_sink():
    pg_main()


if __name__ == "__main__":
    turl_main()
