from models import SignedIntegrityBundle


class SignedIntegrityBundleError(ValueError):
    """Raised when a signed integrity bundle fails validation."""


class SignedIntegrityBundleValidator:
    """Validates alignment across a bundle, signature, key, and verification."""

    def validate(
        self,
        signed_bundle: SignedIntegrityBundle,
    ) -> bool:
        if not isinstance(
            signed_bundle,
            SignedIntegrityBundle,
        ):
            raise TypeError(
                "signed_bundle must be a SignedIntegrityBundle."
            )

        bundle = signed_bundle.bundle
        signature = signed_bundle.signature
        key = signed_bundle.signing_key
        verification = signed_bundle.verification

        if signature.subject_id != bundle.bundle_id:
            raise SignedIntegrityBundleError(
                "Signed integrity bundle contains a signature subject "
                "identity mismatch."
            )

        if signature.subject_type != "RECOVERY_INTEGRITY_BUNDLE":
            raise SignedIntegrityBundleError(
                "Signed integrity bundle contains a signature subject "
                "type mismatch."
            )

        if signature.content_digest != signed_bundle.bundle_digest:
            raise SignedIntegrityBundleError(
                "Signed integrity bundle contains a signature content "
                "digest mismatch."
            )

        if signature.key_id != key.key_id:
            raise SignedIntegrityBundleError(
                "Signed integrity bundle contains a signature key "
                "identity mismatch."
            )

        if signature.signer_id != key.owner_id:
            raise SignedIntegrityBundleError(
                "Signed integrity bundle contains a signature signer "
                "identity mismatch."
            )

        if verification.signature_id != signature.signature_id:
            raise SignedIntegrityBundleError(
                "Signed integrity bundle contains a verification "
                "signature identity mismatch."
            )

        if verification.key_id != key.key_id:
            raise SignedIntegrityBundleError(
                "Signed integrity bundle contains a verification key "
                "identity mismatch."
            )

        if verification.subject_id != bundle.bundle_id:
            raise SignedIntegrityBundleError(
                "Signed integrity bundle contains a verification subject "
                "identity mismatch."
            )

        if (
            verification.subject_type
            != "RECOVERY_INTEGRITY_BUNDLE"
        ):
            raise SignedIntegrityBundleError(
                "Signed integrity bundle contains a verification subject "
                "type mismatch."
            )

        if verification.content_digest != signed_bundle.bundle_digest:
            raise SignedIntegrityBundleError(
                "Signed integrity bundle contains a verification content "
                "digest mismatch."
            )

        if verification.signer_id != signature.signer_id:
            raise SignedIntegrityBundleError(
                "Signed integrity bundle contains a verification signer "
                "identity mismatch."
            )

        if verification.key_owner_id != key.owner_id:
            raise SignedIntegrityBundleError(
                "Signed integrity bundle contains a verification key "
                "owner mismatch."
            )

        if signature.algorithm != key.algorithm:
            raise SignedIntegrityBundleError(
                "Signed integrity bundle contains a signing algorithm "
                "mismatch."
            )

        if verification.algorithm != key.algorithm:
            raise SignedIntegrityBundleError(
                "Signed integrity bundle contains a verification "
                "algorithm mismatch."
            )

        if verification.verified is not True:
            raise SignedIntegrityBundleError(
                "Signed integrity bundle requires verified signature "
                "evidence."
            )

        return True