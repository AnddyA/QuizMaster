from django.contrib import admin
from .models import Student, Quiz, Question, QuizAnswer, Category, Group, Option 

# Register your models here.
admin.site.register(Student)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(QuizAnswer)
admin.site.register(Category)
admin.site.register(Group)
admin.site.register(Option)

Category.objects.get_or_create(name='Matemáticas')
Category.objects.get_or_create(name='Administración')
Category.objects.get_or_create(name='Realidad')
Category.objects.get_or_create(name='Técnicas éticas')