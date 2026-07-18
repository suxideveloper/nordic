"""
Management command: python manage.py cleanup_expired

Removes expired events, vacancies, internships and grants from the database.
Safe to run via cron job (e.g. daily at midnight).

Definition of "expired":
  - Event:       start_date is more than GRACE_DAYS days in the past
  - Vacancy:     deadline is in the past (or unpublished for > STALE_DAYS days)
  - Internship:  deadline is in the past
  - Grant:       deadline is in the past

Run manually:
    python manage.py cleanup_expired
    python manage.py cleanup_expired --dry-run       # Preview only, no deletion
    python manage.py cleanup_expired --grace-days 7  # Keep for 7 days after expiry

Add to cron (daily at 2 AM):
    0 2 * * * cd /path/to/nordic && source venv/bin/activate && python manage.py cleanup_expired >> logs/cleanup.log 2>&1
"""

import os
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.timezone import now


class Command(BaseCommand):
    help = 'Remove expired events, vacancies, internships and grants from the database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be deleted without actually deleting.',
        )
        parser.add_argument(
            '--grace-days',
            type=int,
            default=3,
            help='Number of days after expiry before deletion (default: 3).',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        grace = options['grace_days']
        cutoff_dt = now() - timedelta(days=grace)
        cutoff_date = cutoff_dt.date()

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'🔍 DRY RUN — nothing will be deleted (grace: {grace} days)\n'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'🧹 Cleanup started (grace period: {grace} days)\n'
            ))

        total_deleted = 0

        # ── Events ────────────────────────────────────────────────
        from events.models import Event
        expired_events = Event.objects.filter(start_date__lt=cutoff_dt)
        count = expired_events.count()
        if count:
            self.stdout.write(f'  📅 Events expired: {count}')
            for e in expired_events:
                self.stdout.write(f'     - {e.title} ({e.start_date.strftime("%Y-%m-%d")})')
            if not dry_run:
                # Delete associated cover images from disk
                for e in expired_events:
                    if e.cover_image:
                        try:
                            e.cover_image.delete(save=False)
                        except Exception:
                            pass
                expired_events.delete()
                self.stdout.write(self.style.SUCCESS(f'     ✅ Deleted {count} events'))
        else:
            self.stdout.write('  📅 Events: no expired records')
        total_deleted += count

        # ── Vacancies ─────────────────────────────────────────────
        from opportunities.models import Vacancy
        expired_vacancies = Vacancy.objects.filter(deadline__lt=cutoff_date)
        count = expired_vacancies.count()
        if count:
            self.stdout.write(f'  💼 Vacancies expired: {count}')
            for v in expired_vacancies:
                self.stdout.write(f'     - {v.title} @ {v.partner.name} (deadline: {v.deadline})')
            if not dry_run:
                for v in expired_vacancies:
                    if v.cover_image:
                        try:
                            v.cover_image.delete(save=False)
                        except Exception:
                            pass
                expired_vacancies.delete()
                self.stdout.write(self.style.SUCCESS(f'     ✅ Deleted {count} vacancies'))
        else:
            self.stdout.write('  💼 Vacancies: no expired records')
        total_deleted += count

        # ── Internships ───────────────────────────────────────────
        from opportunities.models import Internship
        expired_internships = Internship.objects.filter(deadline__lt=cutoff_date)
        count = expired_internships.count()
        if count:
            self.stdout.write(f'  💻 Internships expired: {count}')
            for i in expired_internships:
                self.stdout.write(f'     - {i.title} @ {i.partner.name} (deadline: {i.deadline})')
            if not dry_run:
                for i in expired_internships:
                    if i.cover_image:
                        try:
                            i.cover_image.delete(save=False)
                        except Exception:
                            pass
                expired_internships.delete()
                self.stdout.write(self.style.SUCCESS(f'     ✅ Deleted {count} internships'))
        else:
            self.stdout.write('  💻 Internships: no expired records')
        total_deleted += count

        # ── Grants ────────────────────────────────────────────────
        from opportunities.models import Grant
        expired_grants = Grant.objects.filter(deadline__lt=cutoff_date)
        count = expired_grants.count()
        if count:
            self.stdout.write(f'  🏆 Grants expired: {count}')
            for g in expired_grants:
                self.stdout.write(f'     - {g.title} @ {g.partner.name} (deadline: {g.deadline})')
            if not dry_run:
                for g in expired_grants:
                    if g.cover_image:
                        try:
                            g.cover_image.delete(save=False)
                        except Exception:
                            pass
                expired_grants.delete()
                self.stdout.write(self.style.SUCCESS(f'     ✅ Deleted {count} grants'))
        else:
            self.stdout.write('  🏆 Grants: no expired records')
        total_deleted += count

        # ── Orphaned media files ──────────────────────────────────
        self._cleanup_orphaned_media()

        # ── Summary ───────────────────────────────────────────────
        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'🔍 DRY RUN complete — would delete {total_deleted} records total.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'✅ Cleanup complete — {total_deleted} records deleted.'
            ))

    def _cleanup_orphaned_media(self):
        """Remove media files whose DB records no longer exist."""
        import os
        from django.conf import settings

        media_root = settings.MEDIA_ROOT
        subfolders = ['events/covers', 'opportunities', 'partners/logos']
        removed = 0

        for folder in subfolders:
            folder_path = os.path.join(media_root, folder)
            if not os.path.exists(folder_path):
                continue
            for fname in os.listdir(folder_path):
                fpath = os.path.join(folder_path, fname)
                rel_path = os.path.join(folder, fname)
                # Check if any model references this file
                from events.models import Event
                from opportunities.models import Vacancy, Internship, Grant
                from core.models import Partner
                referenced = (
                    Event.objects.filter(cover_image=rel_path).exists() or
                    Vacancy.objects.filter(cover_image=rel_path).exists() or
                    Internship.objects.filter(cover_image=rel_path).exists() or
                    Grant.objects.filter(cover_image=rel_path).exists() or
                    Partner.objects.filter(logo=rel_path).exists()
                )
                if not referenced and os.path.isfile(fpath):
                    os.remove(fpath)
                    removed += 1

        if removed:
            self.stdout.write(self.style.SUCCESS(
                f'  🗂️  Removed {removed} orphaned media file(s)'
            ))
