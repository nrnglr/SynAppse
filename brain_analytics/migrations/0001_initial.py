# Generated by Django 4.2.23 on 2025-07-30 11:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BrainHealthScore",
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
                (
                    "frequency_score",
                    models.FloatField(
                        default=0.0, help_text="Daily exercise frequency (7-day window)"
                    ),
                ),
                (
                    "performance_score",
                    models.FloatField(default=0.0, help_text="Average overall scores"),
                ),
                (
                    "consistency_score",
                    models.FloatField(
                        default=0.0,
                        help_text="Score consistency (lower std dev = higher score)",
                    ),
                ),
                (
                    "improvement_score",
                    models.FloatField(default=0.0, help_text="Linear regression trend"),
                ),
                (
                    "exercise_variety_bonus",
                    models.FloatField(
                        default=0.0,
                        help_text="Bonus for doing different exercise types",
                    ),
                ),
                (
                    "difficulty_bonus",
                    models.FloatField(
                        default=0.0, help_text="Bonus for harder exercises"
                    ),
                ),
                (
                    "streak_bonus",
                    models.FloatField(
                        default=0.0, help_text="Bonus for consecutive days"
                    ),
                ),
                (
                    "brain_health_score",
                    models.FloatField(
                        default=0.0, help_text="Final calculated score (0-10)"
                    ),
                ),
                ("total_exercises", models.IntegerField(default=0)),
                ("analysis_period_days", models.IntegerField(default=7)),
                ("memory_exercises", models.IntegerField(default=0)),
                ("word_bridge_exercises", models.IntegerField(default=0)),
                ("problem_chain_exercises", models.IntegerField(default=0)),
                ("last_calculated", models.DateTimeField(auto_now=True)),
                ("is_cache_valid", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="brain_health",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Brain Health Score",
                "verbose_name_plural": "Brain Health Scores",
                "db_table": "brain_health_scores",
            },
        ),
        migrations.CreateModel(
            name="DailyAnalytics",
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
                ("exercises_completed", models.IntegerField(default=0)),
                ("average_score", models.FloatField(blank=True, null=True)),
                ("memory_count", models.IntegerField(default=0)),
                ("word_bridge_count", models.IntegerField(default=0)),
                ("problem_chain_count", models.IntegerField(default=0)),
                ("best_score", models.FloatField(blank=True, null=True)),
                ("total_time_spent", models.IntegerField(default=0)),
                ("easy_exercises", models.IntegerField(default=0)),
                ("medium_exercises", models.IntegerField(default=0)),
                ("hard_exercises", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="daily_analytics",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "daily_analytics",
                "ordering": ["-date"],
                "indexes": [
                    models.Index(
                        fields=["user", "date"], name="daily_analy_user_id_f9ea6c_idx"
                    ),
                    models.Index(fields=["date"], name="daily_analy_date_14b7ba_idx"),
                ],
                "unique_together": {("user", "date")},
            },
        ),
        migrations.CreateModel(
            name="AnalyticsCache",
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
                ("cache_key", models.CharField(db_index=True, max_length=200)),
                ("cache_data", models.JSONField()),
                ("expires_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="analytics_cache",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "analytics_cache",
                "indexes": [
                    models.Index(
                        fields=["cache_key", "expires_at"],
                        name="analytics_c_cache_k_afe5b0_idx",
                    ),
                    models.Index(
                        fields=["user", "cache_key"],
                        name="analytics_c_user_id_af88ff_idx",
                    ),
                ],
                "unique_together": {("user", "cache_key")},
            },
        ),
    ]
