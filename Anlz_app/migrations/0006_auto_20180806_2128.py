# Generated by Django 2.0.7 on 2018-08-06 15:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Anlz_app', '0005_quiz_quiz_total_questions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='level',
            field=models.IntegerField(default=1, validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)], verbose_name='Level'),
        ),
    ]