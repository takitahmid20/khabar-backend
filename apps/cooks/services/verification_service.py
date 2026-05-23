from django.db import transaction

from apps.cooks.models import CookVerification
from shared.enums.core import VerificationStatus


class VerificationService:
    @staticmethod
    @transaction.atomic
    def submit_documents(user, nid_front, nid_back, selfie) -> CookVerification:
        verification, _ = CookVerification.objects.get_or_create(user=user)
        verification.nid_front = nid_front
        verification.nid_back = nid_back
        verification.selfie = selfie
        verification.status = VerificationStatus.PENDING_REVIEW
        verification.save()
        return verification
