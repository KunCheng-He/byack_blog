import threading
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render


# 多线程完成异步发送邮件
class SendMail(threading.Thread):
    def __init__(self, subject, text, email, fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            self.subject, 
            '',
            settings.EMAIL_HOST_USER, 
            [self.email], 
            fail_silently=self.fail_silently,
            html_message=self.text
        )


class Comment(models.Model):
    # 评论对象的创建
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    text = models.TextField()  # 评论内容
    comment_time = models.DateTimeField(auto_now_add=True)  # 评论时间
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)  # 评论的用户

    root = models.ForeignKey('self', related_name='root_comment', null=True, on_delete=models.CASCADE)  # 记录每一条回复是基于哪一条评论开始的
    parent = models.ForeignKey('self', related_name='parent_comment', null=True, on_delete=models.CASCADE)  # 获取上一级的主键值
    reply_to = models.ForeignKey(User, related_name="replies", null=True, on_delete=models.CASCADE)  # 指评论是回复谁的

    def send_mail(self):
        if self.parent is None:
            # 评论我的博客
            subject = 'byack-笔记（查收你的消息了）'
            email = self.content_object.get_email()
        else:
            # 回复评论
            subject = 'byack-笔记（你的评论有回复了）'
            email = self.reply_to.email
        if email != '':
            context = {}
            context['comment_text'] = self.text
            context['url'] = self.content_object.get_url()
            text = render(None, 'comment/send_mail.html', context).content.decode('utf-8')
            send_mail = SendMail(subject, text, email)
            send_mail.start()

    def __str__(self):
        return self.text
