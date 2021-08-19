from fpdf import FPDF

MAIN_TEXT_FONT = "Arial", 12
text = "Example"

pdf = FPDF()

pdf.add_page()
pdf.set_font(MAIN_TEXT_FONT[0], size=MAIN_TEXT_FONT[1])
to_page_2 = pdf.add_link()
pdf.cell(pdf.w - pdf.get_x() * 2, pdf.font_size * 2, txt=text, align='L', ln=1, link=to_page_2)

pdf.add_page()
pdf.set_font(MAIN_TEXT_FONT[0], size=MAIN_TEXT_FONT[1])
pdf.set_link(to_page_2, page=2)
to_page_3 = pdf.add_link()
pdf.cell(pdf.w - pdf.get_x() * 2, pdf.font_size * 2, txt=text + "2", align='L', ln=1, link=to_page_3)

pdf.add_page()
pdf.set_font(MAIN_TEXT_FONT[0], size=MAIN_TEXT_FONT[1])
pdf.set_link(to_page_3, page=3)
pdf.cell(pdf.w - pdf.get_x() * 2, pdf.font_size * 2, txt=text + "3", align='L', ln=1)


 
def simple_table(spacing=1):
    data = [['First Name', 'Last Name', 'email', 'zip'],
            ['Mike', 'Driscoll', 'mike@somewhere.com', '55555'],
            ['John', 'Doe', 'jdoe@doe.com', '12345'],
            ['Nina', 'Ma', 'inane@where.com', '54321']
            ]
 
    pdf.set_font("Arial", size=12)
    pdf.add_page()
 
    col_width = pdf.w / 4.5
    row_height = pdf.font_size
    for row in data:
        for item in row:
            pdf.cell(col_width, row_height*spacing,
                     txt=item, border=1)
        pdf.ln(row_height*spacing)
 

 
if __name__ == '__main__':
    simple_table()

pdf.output('pdf_link.pdf')
