"""
Modern UI Automation generators (NClick, NTypeInto, etc.).

These use the modern UIAutomationNext activities with Version="V5".
CRITICAL: Version must be V5 - V3/V4 crash Studio.
"""

from typing import Optional, Dict
from .helpers import escape_xml, generate_guid


def _gen_target(
    selector: str,
    obj_repo: Optional[Dict] = None,
    indent: str = ""
) -> str:
    """
    Generate Target element for UI activities.

    Args:
        selector: UiPath selector string
        obj_repo: Optional Object Repository reference {reference, content_hash, guid}
    """
    if obj_repo:
        # Object Repository binding
        return f"""{indent}<uix:Target>
{indent}  <uix:TargetAnchorableModel
{indent}    Reference="{obj_repo['reference']}"
{indent}    ContentHash="{obj_repo['content_hash']}"
{indent}    Guid="{obj_repo.get('guid', generate_guid())}">
{indent}    <uix:TargetAnchorableModel.FallbackSelector>
{indent}      <uix:SelectorModel Selector="{escape_xml(selector)}" />
{indent}    </uix:TargetAnchorableModel.FallbackSelector>
{indent}  </uix:TargetAnchorableModel>
{indent}</uix:Target>"""
    else:
        # Direct selector
        return f"""{indent}<uix:Target>
{indent}  <uix:TargetAnchorableModel>
{indent}    <uix:TargetAnchorableModel.Selector>
{indent}      <uix:SelectorModel Selector="{escape_xml(selector)}" />
{indent}    </uix:TargetAnchorableModel.Selector>
{indent}  </uix:TargetAnchorableModel>
{indent}</uix:Target>"""


def gen_nclick(
    selector: str,
    click_type: str = "Single",
    input_mode: str = "Simulate",
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    timeout: int = 30000,
    obj_repo: Optional[Dict] = None,
    indent: str = ""
) -> str:
    """
    Generate an NClick activity (modern UI).

    Args:
        selector: UiPath selector
        click_type: Single, Double, or Down/Up
        input_mode: Simulate, HardwareEvents, ChromiumApi, WindowMessages
        timeout: Timeout in ms
        obj_repo: Optional Object Repository reference
    """
    # Validate enums
    valid_click_types = {"Single", "Double", "Down", "Up"}
    if click_type not in valid_click_types:
        raise ValueError(f"Invalid click_type '{click_type}'. Use: {valid_click_types}")

    valid_input_modes = {"Simulate", "HardwareEvents", "ChromiumApi", "WindowMessages"}
    if input_mode not in valid_input_modes:
        raise ValueError(f"Invalid input_mode '{input_mode}'. Use: {valid_input_modes}")

    name = display_name or f"Click"
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    scope_id = generate_guid()[:8]
    target_xml = _gen_target(selector, obj_repo, indent + "  ")

    return f"""{indent}<uix:NClick
{indent}  DisplayName="{escape_xml(name)}"{ann_attr}
{indent}  ClickType="{click_type}"
{indent}  InputMode="{input_mode}"
{indent}  Version="V5"
{indent}  ScopeIdentifier="{scope_id}"
{indent}  Timeout="{timeout}">
{indent}  <uix:NClick.Target>
{target_xml}
{indent}  </uix:NClick.Target>
{indent}</uix:NClick>"""


def gen_ntypeinto(
    selector: str,
    text: str,
    is_secure: bool = False,
    empty_field_mode: str = "SingleLine",
    click_before_mode: str = "Single",
    input_mode: str = "Simulate",
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    timeout: int = 30000,
    obj_repo: Optional[Dict] = None,
    indent: str = ""
) -> str:
    """
    Generate an NTypeInto activity (modern UI).

    Args:
        selector: UiPath selector
        text: VB.NET expression for text to type
        is_secure: Use SecureText instead of Text (for passwords)
        empty_field_mode: SingleLine, MultiLine, or None
        click_before_mode: None, Single, or Double
        input_mode: Simulate, HardwareEvents, ChromiumApi, WindowMessages
    """
    # Validate enums - CRITICAL for avoiding LLM hallucinations
    valid_empty_modes = {"SingleLine", "MultiLine", "None"}
    if empty_field_mode not in valid_empty_modes:
        raise ValueError(f"Invalid empty_field_mode '{empty_field_mode}'. Use: {valid_empty_modes}")

    valid_click_modes = {"None", "Single", "Double"}
    if click_before_mode not in valid_click_modes:
        raise ValueError(f"Invalid click_before_mode '{click_before_mode}'. Use: {valid_click_modes}")

    valid_input_modes = {"Simulate", "HardwareEvents", "ChromiumApi", "WindowMessages"}
    if input_mode not in valid_input_modes:
        raise ValueError(f"Invalid input_mode '{input_mode}'. Use: {valid_input_modes}")

    name = display_name or "Type Into"
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    scope_id = generate_guid()[:8]
    target_xml = _gen_target(selector, obj_repo, indent + "  ")

    # Text attribute
    if not text.startswith("["):
        text = f"[{text}]"

    text_attr = f'SecureText="{text}"' if is_secure else f'Text="{text}"'

    return f"""{indent}<uix:NTypeInto
{indent}  DisplayName="{escape_xml(name)}"{ann_attr}
{indent}  {text_attr}
{indent}  ActivateBefore="True"
{indent}  ClickBeforeMode="{click_before_mode}"
{indent}  EmptyFieldMode="{empty_field_mode}"
{indent}  InputMode="{input_mode}"
{indent}  Version="V5"
{indent}  ScopeIdentifier="{scope_id}"
{indent}  Timeout="{timeout}">
{indent}  <uix:NTypeInto.Target>
{target_xml}
{indent}  </uix:NTypeInto.Target>
{indent}</uix:NTypeInto>"""


def gen_ngettext(
    selector: str,
    result_variable: str,
    use_full_text: bool = False,
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    timeout: int = 30000,
    obj_repo: Optional[Dict] = None,
    indent: str = ""
) -> str:
    """
    Generate an NGetText activity (modern UI).

    Args:
        selector: UiPath selector
        result_variable: Variable to store extracted text
        use_full_text: Use FullText extraction method
    """
    name = display_name or "Get Text"
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    scope_id = generate_guid()[:8]
    target_xml = _gen_target(selector, obj_repo, indent + "  ")

    full_text_attr = ' UseFullText="True"' if use_full_text else ""

    return f"""{indent}<uix:NGetText
{indent}  DisplayName="{escape_xml(name)}"{ann_attr}
{indent}  Value="[{result_variable}]"
{indent}  Version="V5"
{indent}  ScopeIdentifier="{scope_id}"
{indent}  Timeout="{timeout}"{full_text_attr}>
{indent}  <uix:NGetText.Target>
{target_xml}
{indent}  </uix:NGetText.Target>
{indent}</uix:NGetText>"""


def gen_ncheckstate(
    selector: str,
    result_variable: Optional[str] = None,
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    timeout: int = 30000,
    obj_repo: Optional[Dict] = None,
    indent: str = ""
) -> str:
    """
    Generate an NCheckState activity (modern UI).

    Used to verify element state (visible, enabled, etc.).

    Args:
        selector: UiPath selector
        result_variable: Optional variable to store state result
    """
    name = display_name or "Check App State"
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    scope_id = generate_guid()[:8]
    target_xml = _gen_target(selector, obj_repo, indent + "  ")

    result_attr = f'\n{indent}  Result="[{result_variable}]"' if result_variable else ""

    return f"""{indent}<uix:NCheckState
{indent}  DisplayName="{escape_xml(name)}"{ann_attr}
{indent}  Version="V5"
{indent}  ScopeIdentifier="{scope_id}"
{indent}  Timeout="{timeout}"{result_attr}>
{indent}  <uix:NCheckState.Target>
{target_xml}
{indent}  </uix:NCheckState.Target>
{indent}</uix:NCheckState>"""


def gen_napplication_card(
    url: str,
    body_activities: list,
    open_mode: str = "Always",
    attach_mode: str = "SingleWindow",
    browser_type: str = "Chrome",
    is_incognito: bool = True,
    out_uielement: Optional[str] = None,
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    indent: str = ""
) -> str:
    """
    Generate an NApplicationCard activity (modern browser scope).

    Args:
        url: VB.NET expression for URL
        body_activities: Activities inside the browser scope
        open_mode: Always, IfNotOpen, or Never
        attach_mode: SingleWindow or AllWindows
        browser_type: Chrome, Edge, Firefox
        is_incognito: Open in incognito/private mode
        out_uielement: Variable to store browser UiElement
    """
    # Validate enums
    valid_open_modes = {"Always", "IfNotOpen", "Never"}
    if open_mode not in valid_open_modes:
        raise ValueError(f"Invalid open_mode '{open_mode}'. Use: {valid_open_modes}")

    valid_attach_modes = {"SingleWindow", "AllWindows"}
    if attach_mode not in valid_attach_modes:
        raise ValueError(f"Invalid attach_mode '{attach_mode}'. Use: {valid_attach_modes}")

    name = display_name or f"Use Application/Browser"
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    if not url.startswith("["):
        url = f"[{url}]"

    incognito_attr = ' IsIncognito="True"' if is_incognito else ""
    out_elem_attr = f'\n{indent}  OutUiElement="[{out_uielement}]"' if out_uielement else ""

    from .helpers import indent_xml
    body_content = "\n".join(indent_xml(a, 6) for a in body_activities)

    return f"""{indent}<uix:NApplicationCard
{indent}  DisplayName="{escape_xml(name)}"{ann_attr}
{indent}  OpenMode="{open_mode}"
{indent}  AttachMode="{attach_mode}"
{indent}  BrowserType="{browser_type}"{incognito_attr}
{indent}  Url="{url}"{out_elem_attr}>
{indent}  <uix:NApplicationCard.Body>
{indent}    <ActivityAction x:TypeArguments="uix:IUiObjectSource">
{indent}      <ActivityAction.Argument>
{indent}        <DelegateInArgument x:TypeArguments="uix:IUiObjectSource" Name="body" />
{indent}      </ActivityAction.Argument>
{indent}      <Sequence DisplayName="Body">
{body_content}
{indent}      </Sequence>
{indent}    </ActivityAction>
{indent}  </uix:NApplicationCard.Body>
{indent}</uix:NApplicationCard>"""


def gen_ngoto_url(
    url: str,
    display_name: Optional[str] = None,
    annotation: Optional[str] = None,
    timeout: int = 30000,
    indent: str = ""
) -> str:
    """
    Generate an NGoToUrl activity (navigate browser).

    Args:
        url: VB.NET expression for URL
    """
    name = display_name or "Navigate To URL"
    ann_attr = f'\n{indent}  sap2010:Annotation.AnnotationText="{escape_xml(annotation)}"' if annotation else ""

    if not url.startswith("["):
        url = f"[{url}]"

    return f"""{indent}<uix:NGoToUrl
{indent}  DisplayName="{escape_xml(name)}"{ann_attr}
{indent}  Url="{url}"
{indent}  Timeout="{timeout}" />"""
