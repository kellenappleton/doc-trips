from django.db import models
from django.db.models import Q

from fyt.applications.managers import pks


class AttendeeManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related(
            'volunteer', 'volunteer__applicant')

    def trainable(self, trips_year):
        """
        All volunteers can be trained this year.
        """
        return self.filter(
            trips_year=trips_year
        ).filter(
            volunteer__status__in=self.model.TRAINABLE_STATUSES
        )

    def first_aid_complete(self, trips_year):
        """
        All volunteers with first aid certifications.
        """
        return self.filter(
            trips_year=trips_year
        ).exclude(
            Q(fa_cert='') & Q(fa_other='')
        )

    def first_aid_incomplete(self, trips_year):
        """
        All volunteers missing first aid certifications.
        """
        return self.filter(
            trips_year=trips_year
        ).filter(
            fa_cert='', fa_other=''
        )

    def training_complete(self, trips_year):
        """
        All volunteers who have finished their training.
        """
        qs = self.filter(trips_year=trips_year)

        from .models import Training
        for training in Training.objects.filter(trips_year=trips_year):
            qs = qs.filter(complete_sessions__training=training)

        return qs

    def training_incomplete(self, trips_year):
        """
        All volunteers who have not completed their training.
        """
        return self.filter(
            trips_year=trips_year
        ).exclude(
            pk__in=pks(self.training_complete(trips_year))
        )
