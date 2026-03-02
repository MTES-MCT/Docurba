from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0008_alter_communeprocedure_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="communeprocedure",
            options={"verbose_name": "Périmètre"},
        ),
        migrations.AlterModelOptions(
            name="event",
            options={"ordering": ("-date_evenement",)},
        ),
        migrations.AlterModelOptions(
            name="procedure",
            options={},
        ),
    ]
