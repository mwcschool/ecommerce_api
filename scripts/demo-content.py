from models import database, Item, User, Address, Order, OrderItem
from faker import Factory
from random import seed, randint


def main():
    database.connect()
    seed(2)

    fake = Factory.create('it_IT')
    fake.seed(99)

    items_list = []
    users_list = []

    for _ in range(10):
        item = Item.create(
            uuid=fake.uuid4(),
            name=fake.word(),
            price=fake.random_int(),
            description=fake.sentence(),
            category=fake.word(),
            )
        items_list.append(item)

    for _ in range(20):
        user = User.create(
            uuid=fake.uuid4(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            password=fake.password(),
            )
        users_list.append(user)

    for user in users_list:
        for x in range(randint(1, 3)):
            Address.create(
                uuid=fake.uuid4(),
                user=user,
                nation=fake.country(),
                city=fake.city(),
                postal_code=fake.postcode(),
                local_address=fake.address(),
                phone=fake.phone_number(),
            )

    for user in users_list:
        # User has three chance on four to make an order
        make_order = randint(0, 4)

        # If use make an order, I insert an order and I iterate the items list
        if make_order != 0:
            order_total_price = 0

            order_item_quantity = 0
            order_item_subtotal = 0

            order = Order.create(
                uuid=fake.uuid4(),
                total_price=order_total_price,
                user=user,
                )

            for item in items_list:
                # If item_quantity == 0, the item isn't counted in the order
                order_item_quantity = randint(0, 3)

                if order_item_quantity != 0:
                    order_item_subtotal = item.price * order_item_quantity
                    order_total_price += order_item_subtotal

                    OrderItem.create(
                        order=order,
                        item=item,
                        quantity=item.price,
                        subtotal=order_item_subtotal,
                        )

            order.total_price = order_total_price
            order.save()


if __name__ == '__main__':
    main()
