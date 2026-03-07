"""Program-wide form style constants.

Change any value here to adjust the default appearance of all forms.
"""

from textual_wtf.types import HelpStyle, LabelStyle

FORM_HELP_STYLE: HelpStyle = "tooltip"
FORM_LABEL_STYLE: LabelStyle = "placeholder"
TEXTAREA_MIN_HEIGHT: int = 4

# App-level CSS applied to all screens for form input contrast.
FORM_INPUT_CSS: str = """
FieldWidget Input,
FieldWidget TextArea,
FieldWidget Select {
    background: $panel;
    border: round $accent;
}
FieldWidget Input:focus,
FieldWidget TextArea:focus,
FieldWidget Select:focus {
    border: round $accent-lighten-2;
    background-tint: $foreground 8%;
}
FormTextArea {
    min-height: 4;
    height: auto;
}
"""
