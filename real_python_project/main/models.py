# real_python_project/main/models.py

from django.db import models

class DailyUpdate(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    source = models.CharField(max_length=100, default='Unknown')
    received_at = models.DateTimeField() # auto_now_add=True 대신 직접 시간 지정할 수 있도록 수정
    # ***************************************************************
    # 새로 추가하는 필드: original_url
    original_url = models.URLField(max_length=500, blank=True, null=True) # URL 필드, 필수가 아니므로 blank=True, null=True
    # ***************************************************************

    class Meta:
        unique_together = ('title', 'received_at')
        ordering = ['-received_at'] # 기본 정렬을 최신순으로 설정

    def __str__(self):
        return self.title
    

class Post(models.Model):
    CATEGORY_CHOICES = [
        ('free', '자유게시판'),
        ('report', '신고게시판'),
    ]

    GENDER_CHOICES = [
        ('male', '남성'),
        ('female', '여성'),
        ('other', '기타'),
    ]

    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    name     = models.CharField(max_length=100)
    gender   = models.CharField(max_length=10, choices=GENDER_CHOICES)
    age      = models.PositiveIntegerField()
    region   = models.CharField(max_length=100)
    email    = models.EmailField()
    title    = models.CharField(max_length=200)
    content  = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title