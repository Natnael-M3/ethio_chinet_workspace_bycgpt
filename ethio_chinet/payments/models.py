from django.db import models
from users.models import User
from posts.models import Post


class Payment(models.Model):
    post = models.OneToOneField(
        Post,
        on_delete=models.CASCADE,
        related_name='payment'
    )
    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'admin'}
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.post.post_code}"
