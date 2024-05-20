from django.contrib import admin
from .models import *

admin.site.register(MyUser)
admin.site.register(Article)
admin.site.register(Term)
admin.site.register(Vacancy)
admin.site.register(Review)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)

# Register your models here.
