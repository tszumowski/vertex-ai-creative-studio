import mesop as me

NUMBER_OF_IMAGES_OPTIONS = [
    me.SelectOption(label="1", value="1"),
    me.SelectOption(label="2", value="2"),
    me.SelectOption(label="3", value="3"),
    me.SelectOption(label="4", value="4"),
]

COMPOSITION_OPTIONS = [
    me.SelectOption(label="None", value="None"),
    me.SelectOption(label="Closeup", value="Closeup"),
    me.SelectOption(label="Knolling", value="Knolling"),
    me.SelectOption(label="Landscape photography", value="Landscape photography"),
    me.SelectOption(
        label="Photographed through window", value="Photographed through window"
    ),
    me.SelectOption(label="Shallow depth of field", value="Shallow depth of field"),
    me.SelectOption(label="Shot from above", value="Shot from above"),
    me.SelectOption(label="Shot from below", value="Shot from below"),
    me.SelectOption(label="Surface detail", value="Surface detail"),
    me.SelectOption(label="Wide angle", value="Wide angle"),
]

LIGHTING_OPTIONS = [
    me.SelectOption(label="None", value="None"),
    me.SelectOption(label="Backlighting", value="Backlighting"),
    me.SelectOption(label="Dramatic light", value="Dramatic light"),
    me.SelectOption(label="Golden hour", value="Golden hour"),
    me.SelectOption(label="Long-time exposure", value="Long-time exposure"),
    me.SelectOption(label="Low lighting", value="Low lighting"),
    me.SelectOption(label="Multiexposure", value="Multiexposure"),
    me.SelectOption(label="Studio light", value="Studio light"),
    me.SelectOption(label="Surreal lighting", value="Surreal lighting"),
]

COLOR_AND_TONE_OPTIONS = [
    me.SelectOption(label="None", value="None"),
    me.SelectOption(label="Black and white", value="Black and white"),
    me.SelectOption(label="Cool tone", value="Cool tone"),
    me.SelectOption(label="Golden", value="Golden"),
    me.SelectOption(label="Monochromatic", value="Monochromatic"),
    me.SelectOption(label="Muted color", value="Muted color"),
    me.SelectOption(label="Pastel color", value="Pastel color"),
    me.SelectOption(label="Toned image", value="Toned image"),
]

CONTENT_TYPE_OPTIONS = [
    me.SelectOption(label="None", value="None"),
    me.SelectOption(label="Photo", value="Photo"),
    me.SelectOption(label="Art", value="Art"),
]

ASPECT_RATIO_OPTIONS = [
    me.SelectOption(label="1:1", value="1:1"),
    me.SelectOption(label="3:4", value="3:4"),
    me.SelectOption(label="4:3", value="4:3"),
    me.SelectOption(label="16:9", value="16:9"),
    me.SelectOption(label="9:16", value="9:16"),
]
