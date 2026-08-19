from fontTools.feaLib.builder import (
    addOpenTypeFeaturesFromString,
)


def build_ligatures(font):
    addOpenTypeFeaturesFromString(
        font,
        """
        feature liga {
            ...
        } liga;
        """,
        tables=["GSUB"],
    )