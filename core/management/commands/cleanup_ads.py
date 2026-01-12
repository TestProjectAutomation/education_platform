from django.core.management.base import BaseCommand
from django.utils import timezone
from advertisements.models import Advertisement
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clean up expired ads and deactivate old ones'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days after expiration to deactivate ads'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        # العثور على الإعلانات المنتهية والتي ما زالت نشطة
        expired_ads = Advertisement.objects.filter(
            end_date__lt=cutoff_date,
            active=True
        )
        
        count = expired_ads.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would deactivate {count} ads expired more than {days} days ago'
                )
            )
            for ad in expired_ads[:5]:  # عرض أول 5 فقط
                self.stdout.write(f'  - {ad.title} (expired: {ad.end_date})')
            if count > 5:
                self.stdout.write(f'  ... and {count - 5} more')
        else:
            updated = expired_ads.update(active=False)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deactivated {updated} ads expired more than {days} days ago'
                )
            )
            logger.info(f'Deactivated {updated} expired ads')
        
        # أيضاً، يمكننا حذف الإعلانات القديمة جداً
        if not dry_run:
            old_cutoff = timezone.now() - timezone.timedelta(days=365)  # سنة
            old_inactive_ads = Advertisement.objects.filter(
                end_date__lt=old_cutoff,
                active=False,
                impressions=0,
                clicks=0
            )
            deleted_count, _ = old_inactive_ads.delete()
            
            if deleted_count:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Deleted {deleted_count} old inactive ads with no impressions/clicks'
                    )
                )
                logger.info(f'Deleted {deleted_count} old inactive ads')
