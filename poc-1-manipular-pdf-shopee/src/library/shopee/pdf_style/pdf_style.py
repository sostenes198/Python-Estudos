from reportlab.lib import colors
from reportlab.platypus import TableStyle


class PdfStyle:
    __TABLE_STYLE: TableStyle = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Borders throughout the table
        # ('BACKGROUND', (0, 0), (-1, 0), colors.white),  # Header line background
        # ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center the text
        # ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Align vertically in the middle
        # ('FONTSIZE', (0, 0), (-1, -1), 55),  # Setting the font size
        # ('FONTNAME', (0, 0), (-1, -1), 'Courier-Bold'),  # Define font type
    ])

    @classmethod
    def table_style(cls) -> TableStyle:
        return cls.__TABLE_STYLE
