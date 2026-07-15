from models import AuditHashChain


class AuditHashChainError(ValueError):
    """Raised when an audit hash chain fails integrity validation."""


class AuditHashChainValidator:
    """Validates continuity and identity across an audit hash chain."""

    def validate(
        self,
        chain: AuditHashChain,
    ) -> bool:
        if not isinstance(chain, AuditHashChain):
            raise TypeError(
                "chain must be an AuditHashChain."
            )

        self._validate_contiguous_sequence(chain)
        self._validate_link_continuity(chain)
        self._validate_linker_consistency(chain)
        self._validate_issuer_alignment(chain)

        return True

    @staticmethod
    def _validate_contiguous_sequence(
        chain: AuditHashChain,
    ) -> None:
        sequence_numbers = tuple(
            link.sequence_number
            for link in chain.links
        )

        expected_sequence = tuple(
            range(1, len(sequence_numbers) + 1)
        )

        if sequence_numbers != expected_sequence:
            raise AuditHashChainError(
                "Audit hash-chain sequence must remain contiguous."
            )

    @staticmethod
    def _validate_link_continuity(
        chain: AuditHashChain,
    ) -> None:
        for previous_link, current_link in zip(
            chain.links,
            chain.links[1:],
        ):
            if (
                current_link.previous_event_id
                != previous_link.event_id
            ):
                raise AuditHashChainError(
                    "Audit hash chain contains a previous event "
                    "identity mismatch."
                )

            if (
                current_link.previous_digest
                != previous_link.current_digest
            ):
                raise AuditHashChainError(
                    "Audit hash chain contains a previous digest "
                    "mismatch."
                )

    @staticmethod
    def _validate_linker_consistency(
        chain: AuditHashChain,
    ) -> None:
        linker_ids = {
            link.linker_id
            for link in chain.links
        }

        if len(linker_ids) != 1:
            raise AuditHashChainError(
                "Audit hash-chain linker identity must remain consistent."
            )

    @staticmethod
    def _validate_issuer_alignment(
        chain: AuditHashChain,
    ) -> None:
        linker_id = chain.links[0].linker_id

        if linker_id != chain.issuer_id:
            raise AuditHashChainError(
                "Audit hash-chain linker must match the chain issuer."
            )