from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_auto_20240307_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='msclkid',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]
