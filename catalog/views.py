          # -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404, render_to_response
from django.core import urlresolvers
from django.template import RequestContext
from catalog.models import Category, Product
from catalog.forms import ProductAddToCartForm
from django.http import HttpResponseRedirect
from cart import cart

def index(request):
    # На главную отдаю только последние 3 тавара со спец ценой
    special_prices = Product.objects.filter(is_special_price=True)[0:3]
    # На главную отдаю только последние 3 тавара бестселлера
    bestsellers = Product.objects.filter(is_bestseller=True)[0:3]
    page_title = "topDJshop - интернет магазин аудио оборудования"
    meta_keywords = page_title
    meta_description = "Наушники - для DJ, топовые модели Топовые наушники по доступным ценам. Dr.dre Beats, Pioneer HDJ, Bose."
    return render_to_response('main/index.html', locals(), context_instance=RequestContext(request))

def show_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = category.product_set.filter(is_active=True)
    page_title = "%s %s" % (category.section, category)
    meta_keywords = page_title
    return render_to_response("main/catalog.html", locals(), context_instance=RequestContext(request))

def show_product(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    photos = product.productphoto_set.all()
    features = product.feature_set.all()
    page_title = u"%s %s" % (product.brand, product)
    meta_keywords = page_title
    meta_description = "%s - %s" % (page_title, product.mini_description)

    # evaluate the HTTP method, change as needed
    if request.method == 'POST':
        #create the bound form
        postdata = request.POST.copy()
        form = ProductAddToCartForm(request, postdata)
        #check if posted data is valid
        if form.is_valid():
            #add to cart and redirect to cart page
            cart.add_to_cart(request)
            # if test cookie worked, get rid of it
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            url = urlresolvers.reverse('show_cart')
            return HttpResponseRedirect(url)
    else:
        #create the unbound form. Notice the request as a keyword argument
        form = ProductAddToCartForm(request=request, label_suffix=':')
    # assign the hidden input the product slug
    form.fields['product_slug'].widget.attrs['value'] = product_slug
    # set test cookie to make sure cookies are enabled
    request.session.set_test_cookie()
    return render_to_response("main/tovar.html", locals(), context_instance=RequestContext(request))

def about(request):
    page_title = "О нас"
    return render_to_response('main/about.html', locals(), context_instance=RequestContext(request))

def blog(request):
    page_title = "Блог"
    return render_to_response('main/blog.html', locals(), context_instance=RequestContext(request))

def delivery(request):
    page_title = "Доставка и оплата"
    return render_to_response('main/delivery.html', locals(), context_instance=RequestContext(request))
