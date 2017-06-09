import click
from models import database
from models import User
import uuid
from views.user import crypt_password


@click.command()
@click.option('--email', prompt=True, help='New superuser email')
@click.option('--password', prompt=True, hide_input=True, help='New superuser password')
def create_superuser(email, password):
    database.connect()

    User.create(
        uuid=uuid.uuid4(),
        first_name='',
        last_name='',
        email=email,
        password=(crypt_password(password)),
        superuser=True,
    )

    database.close()


if __name__ == '__main__':
    create_superuser()
