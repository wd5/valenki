          # -*- coding: utf-8 -*-
from models import CartItem, Client
from catalog.models import *
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
import threading, urllib2, urllib
from hashlib import md5
import decimal
import random
import settings

CART_ID_SESSION_KEY = 'cart_id'

def _cart_id(request):
    """ get the current user's cart id, sets new one if blank;
    Note: the syntax below matches the text, but an alternative,
    clearer way of checking for a cart ID would be the following:

    if not CART_ID_SESSION_KEY in request.session:

    """
    if request.session.get(CART_ID_SESSION_KEY,'') == '':
        request.session[CART_ID_SESSION_KEY] = _generate_cart_id()
    return request.session[CART_ID_SESSION_KEY]

def _generate_cart_id():
    """ function for generating random cart ID values """
    cart_id = ''
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()'
    cart_id_length = 50
    for y in range(cart_id_length):
        cart_id += characters[random.randint(0, len(characters)-1)]
    return cart_id

def get_cart_items(request):
    """ return all items from the current user's cart """
    return CartItem.objects.filter(cart_id=_cart_id(request))

def add_to_cart(request):
    """ function that takes a POST request and adds a product instance to the current customer's shopping cart """
    postdata = request.POST.copy()
    # get product slug from post data, return blank if empty
    product_slug = postdata.get('product_slug','')
    # get quantity added, return 1 if empty
#    quantity = postdata.get('quantity',1)
    quantity = 1
    # fetch the product or return a missing page error
    p = get_object_or_404(Product, slug=product_slug)
    #get products_image in cart
    cart_products = get_cart_items(request)
    product_in_cart = False
    # check to see if item is already in cart
    for cart_item in cart_products:
        if cart_item.product.id == p.id:
            # update the quantity if found
            cart_item.augment_quantity(quantity)
            product_in_cart = True
    if not product_in_cart:
        # create and save a new cart item
        ci = CartItem()
        ci.product = p
        ci.quantity = quantity
        ci.cart_id = _cart_id(request)
        ci.save()

# returns the total number of items in the user's cart
def cart_distinct_item_count(request):
    return get_cart_items(request).count()

def get_single_item(request, item_id):
    return get_object_or_404(CartItem, id=item_id, cart_id=_cart_id(request))

# update quantity for single item
def update_cart(request):
    postdata = request.POST.copy()
    item_id = postdata['item_id']
    quantity = postdata['quantity']
    cart_item = get_single_item(request, item_id)
    if cart_item:
        if int(quantity) > 0:
            cart_item.quantity = int(quantity)
            cart_item.save()
        else:
            remove_from_cart(request)

# remove a single item from cart
def remove_from_cart(request):
    postdata = request.POST.copy()
    item_id = postdata['item_id']
    cart_item = get_single_item(request, item_id)
    if cart_item:
        cart_item.delete()

# gets the total cost for the current cart
def cart_subtotal(request):
    cart_total = decimal.Decimal('0.00')
    cart_products = get_cart_items(request)
    for cart_item in cart_products:
        cart_total += cart_item.product.price * cart_item.quantity
    return cart_total

def save_client(request, form):
    cart_id = _cart_id(request)

    ci = Client()
    ci.cart = cart_id
    ci.referer = request.META.get('HTTP_REFERER')

    ci.name = form.cleaned_data['name']
    ci.surname = form.cleaned_data['surname']
    ci.patronymic = form.cleaned_data['patronymic']
    ci.city = form.cleaned_data['city']
    ci.postcode = form.cleaned_data['postcode']
    ci.phone = form.cleaned_data['phone']
    ci.address = form.cleaned_data['address']
    ci.email = form.cleaned_data['email']
    ci.save()

def send_admin_email(request, cart_items, form, cart_subtotal):
    products_for_email = ""
    for item in cart_items:
        products_for_email += u"%s %s:%s шт  http://kupit-valenki.ru%s\n" % (item.product.brand,
                                              item.product.name, item.quantity, item.product.get_absolute_url())
    t = threading.Thread(target= send_mail, args=[
        u'Заказ от %s %s' % (form.cleaned_data['name'], form.cleaned_data['surname'] ),
        u'Имя: %s %s %s \nГород: %s\nИндекс: %s\nТелефон: %s\nАдрес: %s\nEmail: %s\n\n%s\nВсего на сумму: %s руб\nПришел с: %s'
        % (form.cleaned_data['surname'], form.cleaned_data['name'], form.cleaned_data['patronymic'],
        form.cleaned_data['city'], form.cleaned_data['postcode'], form.cleaned_data['phone'],
        form.cleaned_data['address'], form.cleaned_data['email'], products_for_email, cart_subtotal, request.COOKIES.get('REFERRER', None)),
        settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], 'fail_silently=False'])
    t.setDaemon(True)
    t.start()

def send_client_email(cart_items, form, cart_subtotal):
    products_for_email = ""
    for item in cart_items:
        products_for_email += u"%s %s:%s шт  http://kupit-valenki.ru%s\n" % (item.product.brand,
                                              item.product.name, item.quantity, item.product.get_absolute_url())
    t = threading.Thread(target= send_mail, args=[
        u'Ваш заказ от Купить-валенки.ру',
        u'Здравствуйте %s,\n\nВы оформили у нас заказ на:\n%s\nВсего на сумму: %s руб\n\nВ ближайшее время наш менеджер с вами свяжется.\nС Уважением, kupit-valenki.ru' %
        (form.cleaned_data['name'], products_for_email, cart_subtotal ),
        settings.EMAIL_HOST_USER, [form.cleaned_data['email']], 'fail_silently=False'])
    t.setDaemon(True)
    t.start()

def send_sms(cart_items, form):
    login = 'east.belle88@gmail.com'
    password = 'nscrfrren'
    phones = ["79274544472", "79033887085"]
    from_phone = form.cleaned_data['phone']
    products = ""
    for item in cart_items:
        products += "%sx%s" % (item.product.slug, item.quantity)
    msg = "%s,%s %s" % (form.cleaned_data['name'], form.cleaned_data['city'], products)
    msg = urllib.urlencode({'msg': msg.encode('cp1251')})
    for to_phone in phones:
        urllib2.urlopen('http://sms48.ru/send_sms.php?login=%s&to=%s&%s&from=%s&check2=%s' % (login, to_phone, msg.encode('cp1251'), from_phone, md5(login + md5(password).hexdigest() + to_phone).hexdigest()) )
