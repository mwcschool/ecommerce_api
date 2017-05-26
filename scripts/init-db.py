from models import database, Item, User, Address, Order, OrderItem


def drop_tables():
    database.connect()

    # Initialize db by deleting all tables
    Item.drop_table(fail_silently=True)
    User.drop_table(fail_silently=True)
    Address.drop_table(fail_silently=True)
    Order.drop_table(fail_silently=True)
    OrderItem.drop_table(fail_silently=True)
    Picture.drop_table(fail_silently=True)

    database.close()


def create_tables():
    database.connect()

    # Create new table with the same name
    Item.create_table()
    User.create_table()
    Address.create_table()
    Order.create_table()
    OrderItem.create_table()
    Picture.create_table()

    database.close()


def main():
    drop_tables()
    create_tables()


if __name__ == '__main__':
    main()
