from django.db import models


class PostPayment(models.Model):
    post = models.OneToOneField(
        'posts.Post',
        on_delete=models.CASCADE,
        related_name='payment'
    )

    admin = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE
    )

    finished_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.post.post_code}"
