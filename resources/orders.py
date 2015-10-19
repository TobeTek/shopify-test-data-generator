import random
import shopify

import config

from faker import Factory


class Orders:

    def __init__(self, limit_sample_size):

        self.products = shopify.Product.find(limit=limit_sample_size)

        return

    def generate(self, number_products):

        # these lists will be added to a data file after creation
        orders_created = []
        customers_created = []

        print("Total Products Sampling From: {}\n".format(len(self.products)))

        # create our factory for generating fake customer names
        fake = Factory.create('en_CA')

        for counter in range(number_products):

            print("Generating Order: " + str(counter))
            new_order = shopify.Order()
            new_order.customer = dict(first_name=fake.first_name(), last_name=fake.last_name())
            new_order.line_items = self.line_items_generate()

            success = new_order.save()

            if success:
                orders_created.append(str(new_order.id))
                customers_created.append(str(new_order.customer.id))

            if new_order.errors:
                # something went wrong!
                print(new_order.errors.full_messages())

        # Write our created data to file. This is required for simple deletion later using this same tool.
        # If these files do not exist, you will have to delete the data manually through the Shopify dashboard.
        with open('sdg-orders.csv', mode='a', encoding='utf-8') as order_file:
            order_file.write('\n'.join(orders_created) + '\n')

        with open('sdg-customers.csv', mode='a', encoding='utf-8') as customers_file:
            customers_file.write('\n'.join(customers_created) + '\n')

        return

    def line_items_generate(self):
        settings = config.settings['orders']
        line_items = []

        # how many different products can a single customer order?
        sample_size = random.randint(1, int(settings['MAX_LINE_ITEMS']))

        # get a random # of products (aka line_items) for this purchase.
        products = random.sample(self.products, sample_size)
        print("Total Products Purchased In Order: {}\n".format(len(products)))

        for product in products:
            if len(product.variants) < int(settings['MAX_VARIANTS']):
                variants = product.variants
            else:
                # generate a random seed to how big our sample size should be
                sample_size = random.randint(1, int(settings['MAX_VARIANTS']))
                variants = random.sample(product.variants, sample_size)

            for variant in variants:
                line_items.append(
                    dict(id=product.id, variant_id=variant.id,
                         quantity=random.randint(1, int(settings['MAX_QUANTITY'])))
                )

        return line_items
