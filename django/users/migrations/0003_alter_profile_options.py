from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_add_column_departements"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="profile",
            options={"verbose_name": "profil"},
        ),
    ]
