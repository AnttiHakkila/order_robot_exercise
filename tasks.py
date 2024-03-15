from RPA.PDF import PDF
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.Archive import Archive
from robocorp import browser
from robocorp.tasks import task


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    orders = get_orders()
    open_robot_order_website()
    for order in orders.data:
        fill_the_form(order)
    archive_receipts()

def open_robot_order_website():
    browser.goto('https://robotsparebinindustries.com/#/robot-order')

def get_orders():
    http = HTTP()
    http.download('https://robotsparebinindustries.com/orders.csv', 'orders.csv', overwrite=True)
    table = Tables()
    data = table.read_table_from_csv('orders.csv', header=True)
    print(data)
    return data

def close_annoying_modal():
    page = browser.page()
    if page.is_visible('//div[@class="modal-content"]'):
        page.click('text=OK')

def fill_the_form(order):
    num, head, body, legs, address = order
    close_annoying_modal()
    page = browser.page()
    page.select_option('[id="head"]', head)
    # page.select_option('//select[@id="head"]', int(head))
    page.check(f'id=id-body-{body}')
    page.fill('//label["text()=\'3. Legs:\'"]/../input', legs)
    page.fill('id=address', address)
    page.click('id=preview')
    for _ in range(5):
        page.click('id=order')
        if page.is_visible('id=order-another'):
            break
    receipt_file = store_receipt_as_pdf(num)
    screenshot_file = screenshot_robot(num)
    embed_screenshot_to_receipt(screenshot_file, receipt_file)
    page.click('id=order-another')

def store_receipt_as_pdf(order_number):
    filename = f'output/receipt_{order_number}.pdf'
    page = browser.page()
    receipt_html = page.locator('id=receipt').inner_html()

    pdf = PDF()
    pdf.html_to_pdf(receipt_html, filename)
    return filename

def screenshot_robot(order_number):
    filename = f'output/robot_{order_number}.png'
    page = browser.page()
    page.locator('id=robot-preview-image').screenshot(path=filename)
    # page.screenshot(path=filename, element='id=robot-preview-image')
    return filename

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf([pdf_file, screenshot], pdf_file)

def archive_receipts():
    archive = Archive()
    archive.archive_folder_with_zip('./output', './output/receipts.zip', include='*.pdf' )
