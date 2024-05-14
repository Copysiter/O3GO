import sys
import docker

from threading import Thread
from dotenv import dotenv_values
from pathlib import Path


def logs(container):
    for log in container.logs(
        stdout=True, stderr=True, timestamps=True, stream=True
    ):
        print(log.decode().strip())


def main():
    client = docker.from_env(use_ssh_client=True)
    environment = dotenv_values(dotenv_path=Path(".env.test"))

    try:
        test_db_container = client.containers.get('test_db')
        test_db_container.stop()
        test_db_container.start()
    except docker.errors.NotFound:
        test_db_container = client.containers.run(
            image='postgres:12',  name='test_db', ports={5432: 5432},
            volumes=['postgres_data:/var/lib/postgresql/data/'],
            environment=environment, detach=True
        )

    try:
        test_app_image = client.images.get('test_app_image')
    except docker.errors.NotFound:
        test_app_image = client.images.build(
            path='.',
            dockerfile='Dockerfile',
            forcerm=True,
            tag='test_app_image'
        )

    try:
        test_app_container = client.containers.get('test_app')
        test_app_container.stop()
        test_app_container.start()
    except docker.errors.NotFound:
        test_app_container = client.containers.run(
            image='test_app_image',  name='test_app',
            ports={8000: 8000}, environment=environment,
            links={'test_db': 'localhost'}, detach=True
        )

    t = Thread(target=logs, args=(test_app_container,), daemon=True)
    t.start()

    result = test_app_container.exec_run(
        'python -m pytest tests',
        stdout=True, stderr=True, stream=True, tty=True
    )

    for r in result.output:
        sys.stdout.write(r.decode())
        sys.stdout.flush()

    test_app_container.stop()
    test_app_container.remove()

    test_db_container.stop()
    test_db_container.remove()

    client.images.remove('test_app_image')


if __name__ == '__main__':
    main()
