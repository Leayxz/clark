from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
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
    ]