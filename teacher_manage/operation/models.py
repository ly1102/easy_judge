from django.db import models
from datetime import datetime
from django.utils import timezone
# Create your models here.


class Cookies(models.Model):
    name = models.CharField(max_length=500, verbose_name="cookie名")
    value = models.CharField(max_length=500, verbose_name="cookie值")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")


class BonusCategory(models.Model):
    content = models.CharField(max_length=80, verbose_name="加分内容")
    limit = models.CharField(max_length=15, verbose_name="加分限制")
    score = models.FloatField(null=True, verbose_name="默认分值")
    is_changeable = models.BooleanField(default=False, verbose_name="分数是否可改")
    min_score = models.FloatField(null=True, verbose_name="最低分")
    max_score = models.FloatField(null=True, verbose_name="最高分")
    Bonus_type = models.CharField(max_length=10, verbose_name="加分类型:德育/智育")


class UserAccount(models.Model):
    username = models.CharField(max_length=50, verbose_name="学工网账号", unique=True)
    password = models.CharField(max_length=50, verbose_name="学工网密码")
    is_now_use = models.BooleanField(default=False, verbose_name="现在登录的用户")
    last_login = models.DateTimeField(default=datetime.now, verbose_name="上次登录时间")


class BonusDetail(models.Model):
    bonus_category_id = models.ForeignKey(BonusCategory)
    selection = models.CharField(null=True, max_length=80, verbose_name="选项内容")
    score = models.FloatField(verbose_name="分值")
    is_changeable = models.BooleanField(default=False, verbose_name="是否可编辑")
    min_score = models.FloatField(null=True, verbose_name="可编辑最低分")
    max_score = models.FloatField(null=True, verbose_name="可编辑最高分")


class Apply(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, verbose_name="账号")
    apply_url = models.CharField(max_length=500, null=True, verbose_name="详情页链接")
    apply_id = models.IntegerField(verbose_name="申请的id", null=True)
    stu_id = models.IntegerField(verbose_name="学号", null=True)
    view_state = models.TextField(verbose_name="验证参数", null=True)
    view_state_gen = models.CharField(max_length=50, verbose_name="验证参数生成值", null=True)
    small_credit = models.CharField(max_length=10, verbose_name="加分项最低分", null=True)
    big_credit = models.CharField(max_length=10, verbose_name="加分项最高分", null=True)
    stu_name = models.CharField(max_length=10, verbose_name="姓名")
    stu_class = models.CharField(max_length=50, verbose_name="班级")
    apply_type = models.CharField(max_length=10, verbose_name="测评类型")
    apply_year = models.CharField(max_length=30, verbose_name="评测学年")
    is_add_score = models.BooleanField(default=True, verbose_name="是否是加分")
    activity = models.CharField(max_length=500, blank=True)
    bonus_category = models.ForeignKey(BonusCategory, null=True, verbose_name="加分总类别")
    bonus = models.ForeignKey(BonusDetail, null=True, verbose_name="加分详细类别")
    # apply_default_score = models.FloatField(null=True, verbose_name="申请加分数")
    apply_score = models.FloatField(null=True, verbose_name="加分填写数值")
    image = models.ImageField(upload_to="image", max_length=200, null=True, verbose_name="证明材料照片")
    examine_date = models.DateField(auto_now=True, verbose_name="审批日期")
    examine_status = models.CharField(max_length=10, default='等待审批', verbose_name="审批状态")
    examine_content = models.CharField(max_length=200, null=True, verbose_name="审批意见")
    is_examined = models.BooleanField(default=False, verbose_name="是否已经审批")
    is_upload = models.BooleanField(default=False, verbose_name="是否同步到网站")

    class Meta:
        unique_together = (("apply_id", "stu_id"),)

