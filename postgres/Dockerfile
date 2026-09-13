FROM public.ecr.aws/docker/library/postgres:16

# Copy init script
COPY init.sql /docker-entrypoint-initdb.d/

# Default environment (overridden by compose)
ENV POSTGRES_DB=nia
ENV POSTGRES_USER=nia_user
