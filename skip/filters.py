from django_filters import rest_framework as filters


class AlertFilter(filters.FilterSet):
    cone_search = filters.CharFilter(method='filter_cone_search', label='Cone Search', 
                                     help_text='RA, Dec, Radius (degrees)')
    alert_timestamp = filters.DateTimeFromToRangeFilter()
    role = filters.CharFilter()
    ordering = filters.OrderingFilter(
        fields=(
            ('alert_timestamp', 'alert_timestamp')
        )
    )

    def filter_cone_search(self, queryset, name, value):
        """
        Executes cone search by annotating each target with separation distance from either the specified RA/Dec or
        the RA/Dec of the specified target. Formula is from Wikipedia: https://en.wikipedia.org/wiki/Angular_distance
        The result is converted to radians.

        Cone search is preceded by a square search to reduce the search radius before annotating the queryset, in
        order to make the query faster.
        """
        if name == 'cone_search':
            ra, dec, radius = value.split(',')
        elif name == 'target_cone_search':
            target_name, radius = value.split(',')
            targets = Target.objects.filter(
                Q(name__icontains=target_name) | Q(aliases__name__icontains=target_name)
            ).distinct()
            if len(targets) == 1:
                ra = targets[0].ra
                dec = targets[0].dec
            else:
                return queryset.filter(name=None)

        ra = float(ra)
        dec = float(dec)

        double_radius = float(radius) * 2
        queryset = queryset.filter(ra__gte=ra - double_radius, ra__lte=ra + double_radius,
                                   dec__gte=dec - double_radius, dec__lte=dec + double_radius)

        separation = ExpressionWrapper(
            180 * ACos(
                (Sin(radians(dec)) * Sin(Radians('dec'))) +
                (Cos(radians(dec)) * Cos(Radians('dec')) * Cos(radians(ra) - Radians('ra')))
            ) / Pi(), FloatField()
        )

        return queryset.annotate(separation=separation).filter(separation__lte=radius)
