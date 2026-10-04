from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Affiliates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.UUIDField(unique=True, db_index=True)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('coupon_code', models.CharField(max_length=15, unique=True, db_index=True)),
                ('lightning_address', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'db_table': 'affiliates',
            },
        ),
        migrations.AddField(
            model_name='invoice',
            name='affiliate_commission_amount',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='affiliate_commission_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='amount_sats',
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]
