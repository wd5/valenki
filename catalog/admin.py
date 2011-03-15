from django.contrib import admin

from catalog.models import Product, ProductPhoto, Category, Brand, Section, Feature, FeatureName

class PhotoInline(admin.StackedInline):
    model = ProductPhoto

class FeaturesInline(admin.StackedInline):
    model = Feature

admin.site.register(ProductPhoto)

class ProductsAdmin(admin.ModelAdmin):
    inlines = [PhotoInline, FeaturesInline]
    list_display = ('name', 'price', 'created_at', 'updated_at',)
    list_display_links = ('name',)
    list_per_page = 50
    ordering = ['-created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug' : ('name',)}

admin.site.register(Product, ProductsAdmin)

class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at',)
    list_display_links = ('name',)
    list_per_page = 20
    ordering = ['name']
    search_fields = ['name', 'description',]
    prepopulated_fields = {'slug' : ('name',)}

admin.site.register(Category, CategoriesAdmin)

class BrandsAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('name',)}

admin.site.register(Brand, BrandsAdmin)

class SectionsAdmin(admin.ModelAdmin):
        prepopulated_fields = {'slug' : ('name',)}

admin.site.register(Section, SectionsAdmin)

admin.site.register(FeatureName)
