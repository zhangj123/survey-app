import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("surveys", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="survey",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="owned_surveys",
                to=settings.AUTH_USER_MODEL,
                verbose_name="创建者",
            ),
        ),
        migrations.AddField(
            model_name="survey",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="survey",
            name="is_published",
            field=models.BooleanField(default=False, verbose_name="已发布"),
        ),
    ]
