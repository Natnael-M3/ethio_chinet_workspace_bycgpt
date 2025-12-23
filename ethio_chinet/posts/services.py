import math
def change_post_status(post, admin, new_status):
    if post.assigned_admin and post.assigned_admin != admin:
        raise PermissionError("Not allowed")

    post.post_status = new_status

    if new_status == 'Taken':
        post.assigned_admin = admin
    elif new_status == 'Posted':
        post.assigned_admin = None

    post.save()


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Distance between two lat/lon points in KM
    """
    R = 6371  # Earth radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

