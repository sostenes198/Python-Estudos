import fitz as PyMuPDF

FILENAME = '1.pdf'

document = PyMuPDF.open(FILENAME)

# ================================================
# 1) Get number of pages
print('# 1) Get number of pages')

# for prop in dir(document):
#     print(prop)

print(f'Number of pages: {document.page_count}')

print()

# ================================================
# 2) Get document info
# https://pymupdf.readthedocs.io/en/latest/
print('# 2) Get document info')

# print(type(document.metadata))
print(document.metadata.keys())

meta = document.metadata
pdfFormat   = meta['format']
pdfTitle    = meta['title']
pdfAuthor   = meta['author']
pdfProducer = meta['producer']

print()

print(f'PDF Format: {pdfFormat}')
print(f'PDF Title: {pdfTitle}')
print(f'PDF Author: {pdfAuthor}')
print(f'PDF Producer: {pdfProducer}')

print()

# Table of Content
pdfTableOfContent = document.get_toc()

for content in pdfTableOfContent:

    level, title, page = content

    print(f'Level: {level}, Title: {title}, Page: {page}')

print()

# ================================================
# 3) Get text from pages
print('# 3) Get text from pages')

# print(dir(document))
# for page in document.pages():

#     # for prop in dir(page):
#     #     print(prop)

#     pageNumber  = page.number + 1
#     pageText    = page.get_text(option= 'text')

#     with open(f'text/p{pageNumber}.txt', 'w', encoding= 'utf8') as fileStream:
#         fileStream.write(pageText)


with open(f'text/all.txt', 'w', encoding='utf8') as fileStream:
    for page in document.pages():
        pageNumber = page.number + 1
        pageText = page.get_text(option='text')

        fileStream.write(f'==>> Page {pageNumber}\n')
        fileStream.write(pageText)

print()

# ================================================
# 4) Get images from pages
print('# 4) Get images from pages')

for page in document.pages():

    images = page.get_images()

    for idx, image in enumerate(images):

        xref = image[0]

        imgData     = document.extract_image(xref)
        imgBytes    = imgData['image']
        imgExt      = imgData['ext']

        pixMap = PyMuPDF.Pixmap(imgBytes)
        pixMap.save(f'images/p{page.number + 1}_{idx}.{imgExt}')

print()

# ================================================
# 5) Get URLs from pages
print('# 5) Get URLs from pages')

hasLinks = document.has_links()

print(f'Document has links? {hasLinks}')

if hasLinks:

    for page in document:

        links = page.get_links()

        for link in links:
            print(f'{page.number + 1}) {link["uri"]}')

print()

# ================================================
# 6) Make images from pages
print('# 6) Make images from pages')

mat = PyMuPDF.Matrix(10, 10)

# for page in document:

#     pixmap = page.get_pixmap()
#     pixmap.save(f'pageImages/p{page.number + 1}.png')

pixmap = document.get_page_pixmap(pno= 7, matrix= mat)
pixmap.save(f'pageImages/page8.png')

page9 = document[8]
pixmap = page9.get_pixmap(dpi= 720)
pixmap.save(f'pageImages/page9.png')

print()

# ================================================
# 7) Scale pages
print('# 7) Scale pages')

rect = PyMuPDF.paper_rect('A4')
rect.x0 = rect.x0 + 30
rect.x1 = rect.x1 - 30

newDocument = PyMuPDF.open()

for page in document:
    newPage = newDocument.new_page()
    newPage.show_pdf_page(rect, document, page.number)

tableOfContent = document.get_toc()
newDocument.set_toc(tableOfContent)

newDocument.save('scale_.pdf')

print()
