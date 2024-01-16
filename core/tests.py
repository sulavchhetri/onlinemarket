# Create your tests here, dynamic pagination, http response
from django.test import TestCase,RequestFactory
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User 
from django.conf import settings
from django_countries.fields import Country
from .models import Item, OrderItem, Order, Coupon, ReviewComment,Address
from django.contrib.auth import get_user_model
from .views import CheckoutView, PaymentView, home_view, OrderSummaryView, add_to_cart, remove_from_cart, remove_single_item_from_cart, get_coupon, AddCouponView, RequestRefundView, products, item_detail_view

User = get_user_model()

class ItemModelTest(TestCase):

    def setUp(self):
        # Set up any necessary data for the test case
        self.user = User.objects.create(username='testuser', password='testpassword')
        self.item = Item.objects.create(
            title='Test Item',
            price=19.99,
            discount_price=15.99,
            category='A',
            label='P',
            description='This is a test item.',
            full_description='Full description for the test item.',
            image='test_image.jpg',
        )

    def test_item_creation(self):
        # Test that an Item instance is created correctly
        self.assertEqual(self.item.title, 'Test Item')
        self.assertEqual(self.item.price, 19.99)
        self.assertEqual(self.item.discount_price, 15.99)
        self.assertEqual(self.item.category, 'A')
        self.assertEqual(self.item.label, 'P')
        self.assertEqual(self.item.description, 'This is a test item.')
        self.assertEqual(self.item.full_description, 'Full description for the test item.')
        self.assertEqual(str(self.item), 'Test Item')

    def test_slug_generation(self):
        # Test the correct generation of the slug property
        expected_slug = 'test-item-{}'.format(self.item.id)
        self.assertEqual(self.item.slug, expected_slug)

    def test_absolute_url(self):
        # Test the correct URL generation with get_absolute_url()
        expected_url = reverse('core:product', kwargs={'slug': self.item.slug})
        self.assertEqual(self.item.get_absolute_url(), expected_url)

    def test_add_to_cart_url(self):
        # Test the correct URL generation with get_add_to_cart_url()
        expected_url = reverse('core:add-to-cart', kwargs={'slug': self.item.slug})
        self.assertEqual(self.item.get_add_to_cart_url(), expected_url)

    def test_remove_from_cart_url(self):
        # Test the correct URL generation with get_remove_from_cart_url()
        expected_url = reverse('core:remove-from-cart', kwargs={'slug': self.item.slug})
        self.assertEqual(self.item.get_remove_from_cart_url(), expected_url)

    def test_order_item_methods(self):
        # Test methods in the OrderItem model
        order_item = OrderItem.objects.create(
            user=self.user,
            item=self.item,
            quantity=2
        )
        self.assertEqual(str(order_item), '2 of Test Item')
        self.assertEqual(order_item.get_total_item_price(), 2 * 19.99)
        self.assertEqual(order_item.get_total_discount_item_price(), 2 * 15.99)
        self.assertEqual(order_item.get_amount_saved(), 2 * (19.99 - 15.99))
        self.assertEqual(order_item.get_final_price(), 2 * 15.99)

    def test_order_model_methods(self):
        # Test methods in the Order model
        order = Order.objects.create(
            user=self.user,
            ordered_date=timezone.now(),
            being_delivered=True,
            received=False,
            refund_requested=False,
            refund_granted=False
        )
        order_item = OrderItem.objects.create(user=self.user, item=self.item, quantity=3)
        order.items.add(order_item)
        coupon = Coupon.objects.create(code='TESTCOUPON', amount=5.0)
        order.coupon = coupon
        order.save()

        # Ensure that order.get_total() correctly calculates the total
        self.assertEqual(order.get_total(), (3 * 15.99) - 5.0)


class ReviewCommentModelTest(TestCase):

    def test_create_review_comment(self):
        # Test creating a ReviewComment instance with valid data
        review_comment = ReviewComment.objects.create(
            product_id=1,
            rating=4,
            comment="This is a test comment."
        )
        self.assertEqual(review_comment.product_id, 1)
        self.assertEqual(review_comment.rating, 4)
        self.assertEqual(review_comment.comment, "This is a test comment.")

    def test_default_values(self):
        # Test that the default values are set correctly
        review_comment = ReviewComment.objects.create()
        self.assertIsNone(review_comment.product_id)
        self.assertEqual(review_comment.rating, 5)
        self.assertEqual(review_comment.comment, "")

    def test_null_default_product_id(self):
        # Test creating a ReviewComment with null product_id
        review_comment = ReviewComment.objects.create(
            rating=3,
            comment="Another test comment."
        )
        self.assertIsNone(review_comment.product_id)
        self.assertEqual(review_comment.rating, 3)
        self.assertEqual(review_comment.comment, "Another test comment.")


class AddressModelTest(TestCase):

    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create(username='testuser', password='testpassword')

    def test_create_address(self):
        # Test creating an Address instance with valid data
        address = Address.objects.create(
            user=self.user,
            street_address='123 Main St',
            apartment_address='Apt 4',
            country='US',
            zip='12345',
            address_type='B',  # Assuming 'B' for Billing address
            default=True
        )
        self.assertEqual(address.user, self.user)
        self.assertEqual(address.street_address, '123 Main St')
        self.assertEqual(address.apartment_address, 'Apt 4')
        self.assertEqual(address.country, Country('US'))
        self.assertEqual(address.zip, '12345')
        self.assertEqual(address.address_type, 'B')
        self.assertTrue(address.default)

    def test_max_length_fields(self):
        # Test the max length of street_address and apartment_address fields
        max_length_street_address = Address._meta.get_field('street_address').max_length
        max_length_apartment_address = Address._meta.get_field('apartment_address').max_length

        address = Address.objects.create(
            user=self.user,
            street_address='A' * max_length_street_address,
            apartment_address='B' * max_length_apartment_address,
            country='US',
            zip='12345',
            address_type='B',
            default=True
        )

        self.assertEqual(len(address.street_address), max_length_street_address)
        self.assertEqual(len(address.apartment_address), max_length_apartment_address)

    def test_verbose_name_plural(self):
        # Test the verbose_name_plural attribute
        self.assertEqual(str(Address._meta.verbose_name_plural), 'Addresses')


class CoreViewsTest(TestCase):

    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')

        self.item = Item.objects.create(
            title='Test Item',
            price=10.0,
            category='E',
            label='P',
            description='Test description',
            image='test_image.jpg'
        )

        # Create a client
        self.factory = RequestFactory()

    def test_home_view(self):
        # Test the home view
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')