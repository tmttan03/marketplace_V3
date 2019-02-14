# Generated by Django 2.1.7 on 2019-02-14 09:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0041_group_collection_permissions_verbose_name_plural'),
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='featured_section',
            field=models.ForeignKey(blank=True, help_text='Third featured section for the homepage. Will display up to six child items.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.Page', verbose_name='Featured section'),
        ),
    ]