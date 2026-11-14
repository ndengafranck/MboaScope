"""Study configuration. Owner: Processing. Values come from docs/SCIENCE.md."""

START_YEAR = 2001
END_YEAR = 2025  # set to 2024 if the December 2025 granule is not published
ALPHA = 0.05
HEADLINE_BOX = "box_3x3"

# Bounds order: [south, north, west, east]. Edges sit on 0.1 degree cell edges.
REGION = [3.6, 4.5, 9.3, 10.2]

BOXES = {
    "box_1x1": {"label": "Single cell, 1 x 1 (about 11 km)", "bounds": [4.0, 4.1, 9.7, 9.8]},
    "box_3x3": {"label": "Douala box, 3 x 3 cells (about 33 km)", "bounds": [3.9, 4.2, 9.6, 9.9]},
    "box_5x5": {"label": "Wide box, 5 x 5 cells (about 55 km)", "bounds": [3.8, 4.3, 9.5, 10.0]},
}

DATASET = {
    "name": "GPM IMERG Final Precipitation L3 1 month 0.1 degree x 0.1 degree V07",
    "short_name": "GPM_3IMERGM",
    "version": "07",
    "doi": "10.5067/GPM/IMERG/3B-MONTH/07",
    "variable": "precipitation",
    "label": "IMERG V07",
}
