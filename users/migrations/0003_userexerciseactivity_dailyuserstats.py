# Generated by Django 4.2.23 on 2025-07-29 08:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("users", "0002_alter_userprofile_options_userprofile_avatar_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserExerciseActivity",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "exercise_type",
                    models.CharField(
                        choices=[
                            ("memory", "Hafıza Egzersizi"),
                            ("word_bridge", "Kelime Köprüsü"),
                            ("problem_chain", "Problem Zinciri"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "difficulty",
                    models.CharField(
                        choices=[
                            ("easy", "Kolay"),
                            ("medium", "Orta"),
                            ("hard", "Zor"),
                        ],
                        max_length=10,
                    ),
                ),
                (
                    "session_id",
                    models.CharField(
                        help_text="Original exercise session ID", max_length=100
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("started", "Başlatıldı"),
                            ("completed", "Tamamlandı"),
                            ("abandoned", "Yarıda Bırakıldı"),
                        ],
                        default="started",
                        max_length=20,
                    ),
                ),
                (
                    "scores",
                    models.JSONField(
                        blank=True, help_text="Exercise specific scores", null=True
                    ),
                ),
                ("overall_score", models.FloatField(blank=True, null=True)),
                (
                    "completion_time",
                    models.IntegerField(
                        blank=True, help_text="Time in seconds", null=True
                    ),
                ),
                (
                    "exercise_data",
                    models.JSONField(
                        blank=True,
                        help_text="Exercise specific responses/answers",
                        null=True,
                    ),
                ),
                ("started_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="exercise_activities",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "user_exercise_activities",
                "ordering": ["-started_at"],
                "indexes": [
                    models.Index(
                        fields=["user", "exercise_type"],
                        name="user_exerci_user_id_bb3570_idx",
                    ),
                    models.Index(
                        fields=["user", "started_at"],
                        name="user_exerci_user_id_c3c66a_idx",
                    ),
                    models.Index(
                        fields=["status", "started_at"],
                        name="user_exerci_status_38862c_idx",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="DailyUserStats",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("total_exercises", models.IntegerField(default=0)),
                ("memory_exercises", models.IntegerField(default=0)),
                ("word_bridge_exercises", models.IntegerField(default=0)),
                ("problem_chain_exercises", models.IntegerField(default=0)),
                ("average_score", models.FloatField(default=0.0)),
                ("best_score", models.FloatField(default=0.0)),
                ("total_time_spent", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="daily_stats",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "daily_user_stats",
                "ordering": ["-date"],
                "unique_together": {("user", "date")},
            },
        ),
    ]
