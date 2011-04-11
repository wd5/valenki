from django.conf.urls.defaults import *

urlpatterns = patterns('',
                      url(r'^$', 'catalog.views.index', name="main-page"),
                      url(r'^cats/(?P<category_slug>[-\w]+)/$', 'catalog.views.show_category', name="catalog-page"),
                      url(r'^products/(?P<product_slug>[-\w]+)/$', 'catalog.views.show_product', name="product-page"),
                      url(r'^about$', 'catalog.views.about', name="about-page"),
                      url(r'^delivery$', 'catalog.views.delivery', name="delivery-page"),
                      url(r'^size$', 'catalog.views.size', name="size-page"),
                      url(r'^buy$', 'catalog.views.buy', name="buy-page"),
                      url(r'^contract$', 'catalog.views.contract', name="contract-page"),
                      url(r'^contacts$', 'catalog.views.contacts', name="contacts-page"),)

