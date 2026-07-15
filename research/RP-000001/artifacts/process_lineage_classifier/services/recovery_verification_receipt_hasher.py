import hashlib
import json

from models import (
    RecoveryVerificationReceipt,
    RecoveryVerificationReceiptHash,
)


class RecoveryVerificationReceiptHashingError(ValueError):
    """Raised when a recovery verification receipt cannot be hashed."""


class RecoveryVerificationReceiptHasher:
    """Produces deterministic SHA-256 hashes for verification receipts."""

    ALGORITHM = "sha256"

    def hash(
        self,
        receipt: RecoveryVerificationReceipt,
    ) -> RecoveryVerificationReceiptHash:
        if not isinstance(receipt, RecoveryVerificationReceipt):
            raise TypeError(
                "receipt must be a RecoveryVerificationReceipt."
            )

        canonical_payload = self._canonicalize(receipt)

        digest_value = hashlib.sha256(
            canonical_payload.encode("utf-8")
        ).hexdigest()

        return RecoveryVerificationReceiptHash(
            receipt_id=receipt.receipt_id,
            algorithm=self.ALGORITHM,
            digest=f"{self.ALGORITHM}:{digest_value}",
            canonical_payload=canonical_payload,
            execution_requested=False,
            side_effects_permitted=False,
        )

    @staticmethod
    def _canonicalize(
        receipt: RecoveryVerificationReceipt,
    ) -> str:
        payload = {
            "receipt_id": receipt.receipt_id,
            "verification_id": receipt.verification_id,
            "replay_id": receipt.replay_id,
            "original_decision_id": (
                receipt.original_decision_id
            ),
            "replay_manifest_id": receipt.replay_manifest_id,
            "replay_manifest_digest": (
                receipt.replay_manifest_digest
            ),
            "audit_chain_id": receipt.audit_chain_id,
            "audit_root_digest": receipt.audit_root_digest,
            "decision_digest": receipt.decision_digest,
            "verified": receipt.verified,
            "issued_at": receipt.issued_at.isoformat(),
            "issuer_id": receipt.issuer_id,
            "execution_requested": receipt.execution_requested,
            "side_effects_permitted": (
                receipt.side_effects_permitted
            ),
        }

        return json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=False,
        )