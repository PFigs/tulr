FROM postgres:14.2-alpine
ENV POSTGRES_DB=turl
ENV POSTGRES_USER=turl
RUN mkdir -p /docker-entrypoint-initdb.d
COPY ./*.sql /docker-entrypoint-initdb.d/
