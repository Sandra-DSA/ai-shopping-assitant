# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Data Science Academy Pvt. Ltd.

import pandas as pd

from data.clean_products import generate_pros_cons


def test_preserves_existing_pros_and_cons():
    df = pd.DataFrame({
        "product_name": ["Test Phone"],
        "description": ["A smartphone with a large display."],
        "pros": ["Good display"],
        "cons": ["Expensive"],
    })

    result = generate_pros_cons(df)

    assert result.loc[0, "pros"] == "Good display"
    assert result.loc[0, "cons"] == "Expensive"


def test_skips_when_description_is_missing():
    df = pd.DataFrame({
        "product_name": ["Test Phone"],
        "pros": [""],
        "cons": [""],
    })

    result = generate_pros_cons(df)

    assert result.equals(df)


import pandas as pd
from unittest.mock import MagicMock, patch

from data.clean_products import generate_pros_cons


@patch("config.GEMINI_API_KEY", "test-key")
def test_generates_missing_pros_and_cons():
    df = pd.DataFrame({
        "product_name": ["Test Phone"],
        "description": ["A smartphone with an OLED display and a 5000mAh battery."],
        "pros": [""],
        "cons": [""],
    })

    mock_response = MagicMock()
    mock_response.text = (
        '{"products": [{"row_id": "0", '
        '"pros": ["OLED display", "Large battery"], '
        '"cons": ["Heavy design"]}]}'
    )

    with patch("google.genai.Client") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.models.generate_content.return_value = mock_response

        result = generate_pros_cons(df)

    assert result.loc[0, "pros"] == "OLED display; Large battery"
    assert result.loc[0, "cons"] == "Heavy design"
    mock_client.models.generate_content.assert_called_once()
