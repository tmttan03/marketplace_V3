# Generated by Django 2.1.7 on 2019-02-15 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20190214_0710'),
    ]

    operations = [
        migrations.AddField(
            model_name='postcategory',
            name='slug',
            field=models.SlugField(default=1),
            preserve_default=False,
        ),
    ]
