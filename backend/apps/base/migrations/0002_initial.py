# Generated by Django 3.2.6 on 2022-02-08 14:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='increasedpercentage',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='percentages', to='base.client', verbose_name='Клиент'),
        ),
        migrations.AddField(
            model_name='increasedpercentage',
            name='trigger',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='percentages', to='base.trigger', verbose_name='Триггерная рассылка'),
        ),
        migrations.AddField(
            model_name='employee',
            name='partner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='base.partner', verbose_name='Партнер'),
        ),
        migrations.AddField(
            model_name='employee',
            name='permissions',
            field=models.ManyToManyField(blank=True, related_name='employees', to='base.Permission', verbose_name='Доступы к разделам'),
        ),
        migrations.AddField(
            model_name='employee',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='company',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='companies', to='base.city', verbose_name='Город'),
        ),
        migrations.AddField(
            model_name='clienttransaction',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transactions', to='base.client', verbose_name='Клиент'),
        ),
        migrations.AddField(
            model_name='client',
            name='partner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='clients', to='base.partner', verbose_name='Партнер'),
        ),
        migrations.AddField(
            model_name='client',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clients', to='base.status', verbose_name='Статус карты'),
        ),
        migrations.AddField(
            model_name='client',
            name='wallet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='clients', to='base.wallet', verbose_name='Карта'),
        ),
        migrations.AddField(
            model_name='cert',
            name='partner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='certs', to='base.partner', verbose_name='Партнер'),
        ),
        migrations.AddField(
            model_name='bonus',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='t_bonuses', to='base.client', verbose_name='Клиент'),
        ),
        migrations.AddField(
            model_name='bonus',
            name='transaction',
            field=models.ForeignKey(blank=True, help_text='Если выбрана транзакция клиента, а так-же выбран тип операции: Списание, то клиенту будут начислены баллы.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='t_transactions', to='base.clienttransaction', verbose_name='Транзакция клиента'),
        ),
        migrations.AddField(
            model_name='audience',
            name='wallet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='audiences', to='base.wallet', verbose_name='Карта'),
        ),
        migrations.AddConstraint(
            model_name='wallet',
            constraint=models.UniqueConstraint(fields=('partner', 'name'), name='unique_wallet_by_partner'),
        ),
        migrations.AddConstraint(
            model_name='status',
            constraint=models.UniqueConstraint(fields=('wallet', 'name'), name='unique_status_by_wallet'),
        ),
        migrations.AddConstraint(
            model_name='servicecategory',
            constraint=models.UniqueConstraint(fields=('wallet', 'name'), name='unique_service_category'),
        ),
        migrations.AddConstraint(
            model_name='service',
            constraint=models.UniqueConstraint(fields=('category', 'name'), name='unique_service'),
        ),
        migrations.AddConstraint(
            model_name='productcategory',
            constraint=models.UniqueConstraint(fields=('wallet', 'name'), name='unique_product_category'),
        ),
        migrations.AddConstraint(
            model_name='product',
            constraint=models.UniqueConstraint(fields=('category', 'name'), name='unique_product'),
        ),
        migrations.AddConstraint(
            model_name='client',
            constraint=models.UniqueConstraint(fields=('wallet', 'phone'), name='unique_client_for_wallet'),
        ),
        migrations.AddConstraint(
            model_name='cert',
            constraint=models.UniqueConstraint(fields=('partner', 'name'), name='unique_cert_by_partner'),
        ),
    ]
