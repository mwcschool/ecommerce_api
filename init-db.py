from models import database, Item, User, Order, OrderItem

database.connect()


# Inizializzo il db cancellando tutte le tabelle
Item.drop_table(fail_silently=True)
User.drop_table(fail_silently=True)
Order.drop_table(fail_silently=True)
OrderItem.drop_table(fail_silently=True)


# Ricreo le tabelle nel db
Item.create_table(fail_silently=True)
User.create_table(fail_silently=True)
Order.create_table(fail_silently=True)
OrderItem.create_table(fail_silently=True)


database.close()
