"""
Deterministic XAML Generators for UiPath Activities.

These generators produce valid XAML output with:
- Locked enum values (cannot hallucinate)
- Correct XML namespaces
- Proper child element structure
- Valid property names

Usage:
    from generators import gen_sequence, gen_invoke_workflow, gen_log_message

    # Generate a sequence with activities
    xaml = gen_sequence(
        display_name="My Sequence",
        activities=[
            gen_log_message("Starting process", level="Info"),
            gen_invoke_workflow("Business/Step1.xaml"),
        ]
    )
"""

from .core import (
    gen_sequence,
    gen_if,
    gen_if_else,
    gen_foreach,
    gen_while,
    gen_switch,
    gen_trycatch,
    gen_assign,
    gen_multiple_assign,
)

from .logging import (
    gen_log_message,
    gen_add_log_fields,
    gen_remove_log_fields,
    gen_comment,
)

from .invoke import (
    gen_invoke_workflow,
    gen_invoke_workflow_simple,
    gen_invoke_code,
)

from .orchestrator import (
    gen_get_queue_item,
    gen_add_queue_item,
    gen_set_transaction_status,
    gen_get_credential,
    gen_get_asset,
)

from .error_handling import (
    gen_throw,
    gen_rethrow,
    gen_retry_scope,
)

from .ui_automation import (
    gen_nclick,
    gen_ntypeinto,
    gen_ngettext,
    gen_ncheckstate,
    gen_napplication_card,
    gen_ngoto_url,
)

from .data import (
    gen_build_datatable,
    gen_filter_datatable,
    gen_add_data_row,
)

from .helpers import (
    escape_xml,
    generate_guid,
    build_annotation,
)

__all__ = [
    # Core
    "gen_sequence",
    "gen_if",
    "gen_if_else",
    "gen_foreach",
    "gen_while",
    "gen_switch",
    "gen_trycatch",
    "gen_assign",
    "gen_multiple_assign",
    # Logging
    "gen_log_message",
    "gen_add_log_fields",
    "gen_remove_log_fields",
    "gen_comment",
    # Invoke
    "gen_invoke_workflow",
    "gen_invoke_workflow_simple",
    "gen_invoke_code",
    # Orchestrator
    "gen_get_queue_item",
    "gen_add_queue_item",
    "gen_set_transaction_status",
    "gen_get_credential",
    "gen_get_asset",
    # Error handling
    "gen_throw",
    "gen_rethrow",
    "gen_retry_scope",
    # UI Automation
    "gen_nclick",
    "gen_ntypeinto",
    "gen_ngettext",
    "gen_ncheckstate",
    "gen_napplication_card",
    "gen_ngoto_url",
    # Data
    "gen_build_datatable",
    "gen_filter_datatable",
    "gen_add_data_row",
    # Helpers
    "escape_xml",
    "generate_guid",
    "build_annotation",
]
