from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('affiliate', '0004_alter_affiliate_promotion_description'),
        ('authentication', '0002_alter_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='affiliate',
            name='id',
            field=models.CharField(max_length=32, primary_key=True, editable=False),
        ),
    ]