# Generated by Django 3.2.6 on 2022-02-08 14:58

import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Наименование')),
                ('version', models.CharField(max_length=32, verbose_name='Версия договора')),
                ('content', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Содержимое')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата последнего обновления')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
            ],
            options={
                'verbose_name': 'Договор',
                'verbose_name_plural': 'Договоры',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='AcceptedContract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField(editable=False, null=True, verbose_name='IP адрес')),
                ('browser_family', models.CharField(editable=False, max_length=255, null=True, verbose_name='Браузер')),
                ('browser_version', models.CharField(editable=False, max_length=255, null=True, verbose_name='Версия браузера')),
                ('os_family', models.CharField(editable=False, max_length=255, null=True, verbose_name='Операционная система')),
                ('os_version', models.CharField(editable=False, max_length=255, null=True, verbose_name='Версия операционной системы')),
                ('device_family', models.CharField(editable=False, max_length=255, null=True, verbose_name='Устройство')),
                ('device_brand', models.CharField(editable=False, max_length=255, null=True, verbose_name='Бренд устройства')),
                ('device_model', models.CharField(editable=False, max_length=255, null=True, verbose_name='Модель устройства')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата последнего обновления')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='partners', to='documents.contract', verbose_name='Договор')),
                ('partner', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='contract', to='base.partner', verbose_name='Партнер')),
            ],
            options={
                'verbose_name': 'Принятый договор',
                'verbose_name_plural': 'Принятые договоры',
                'ordering': ('-id',),
            },
        ),
    ]
