from django.db import models

class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('student', 'Student'),
    ]

    dni = models.CharField(max_length=10, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student'
    )
    profile_pic = models.ImageField(
        upload_to='profile/',
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"


class Group(models.Model):
    id = models.CharField(max_length=5, primary_key=True, unique=True)
    name = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField(User, blank=True)

    def member_count(self):
        return self.members.count()

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    statement = models.TextField()
    image = models.ImageField(upload_to='preguntas/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.image:
            self.image = 'preguntas/default.png'   # poner la subcarpeta
        super().save(*args, **kwargs)

    def __str__(self):
        return self.statement


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class Quiz(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0)

class QuizAnswer(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.SET_NULL, null=True, blank=True)
