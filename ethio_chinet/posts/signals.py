from django.db.models.signals import post_save
from django.dispatch import receiver
from posts.models import Post
from ratings.models import DriverRating


@receiver(post_save, sender=Post)
def create_or_update_driver_rating(sender, instance, created, **kwargs):
    """
    Trigger rating ONLY when:
    taken -> finished
    """
    if instance.status != "finished":
        return

    if not instance.driver:
        return

    rating, _ = DriverRating.objects.get_or_create(
        driver=instance.driver
    )

    rating.recalculate()
