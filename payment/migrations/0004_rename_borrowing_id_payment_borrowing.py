# Generated by Django 5.1.2 on 2024-10-20 09:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0003_alter_payment_session_url"),
    ]

    operations = [
        migrations.RenameField(
            model_name="payment",
            old_name="borrowing_id",
            new_name="borrowing",
        ),
    ]
