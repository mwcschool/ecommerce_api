from models import database, Item, User, Address, Order, OrderItem, Picture


def drop_tables():
    database.connect()

    # Initialize db by deleting all tables
    Item.drop_table(fail_silently=True, cascade=True)
    User.drop_table(fail_silently=True, cascade=True)
    Address.drop_table(fail_silently=True, cascade=True)
    Order.drop_table(fail_silently=True, cascade=True)
    OrderItem.drop_table(fail_silently=True, cascade=True)
    Picture.drop_table(fail_silently=True, cascade=True)

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
