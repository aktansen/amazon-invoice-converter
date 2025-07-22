
from flask import Flask, request, send_file, render_template_string
import os
import pytesseract
from pdf2image import convert_from_bytes
import pandas as pd
from io import BytesIO

app = Flask(__name__)

HTML_FORM = """
<!doctype html>
<title>Amazon Invoice to TL Excel</title>
<h2>Amazon PDF Fatura Dönüştürücü</h2>
<form method=post enctype=multipart/form-data>
  <label>Kur Seçimi:</label><br>
  <input type=radio name=kur_tipi value=otomatik checked> Nisan 2025 Ort. Kur (₺38.0862)<br>
  <input type=radio name=kur_tipi value=manuel> Manuel Kur:
  <input type=text name=manuel_kur placeholder="Örn: 37.25"><br><br>
  <input type=file name=files multiple><br><br>
  <input type=submit value=Excel_Çıktısı>
</form>
"""

def extract_data_from_pdf(pdf_bytes):
    images = convert_from_bytes(pdf_bytes)
    full_text = ""
    for img in images:
        full_text += pytesseract.image_to_string(img, lang='eng') + "\n"
    try:
        order_number = full_text.split("Order #")[1].split("\n")[0].strip()
        order_date = full_text.split("Order Placed:")[1].split("\n")[0].strip()
        item_name = full_text.split("Items Ordered")[1].split("Sold by:")[0].strip().replace("\n", " ")
        item_price = float(full_text.split("Item(s) Subtotal: $")[1].split("\n")[0])
        shipping = float(full_text.split("Shipping & Handling: $")[1].split("\n")[0])
        import_fees = float(full_text.split("Import Fees Deposit $")[1].split("\n")[0])
        coupon = float("-" + full_text.split("Your Coupon Savings: -$")[1].split("\n")[0]) if "Your Coupon Savings: -$" in full_text else 0.0
        return {
            "Sipariş Numarası": order_number,
            "Sipariş Tarihi": order_date,
            "Ürün Adı": item_name,
            "Ürün Fiyatı (USD)": item_price,
            "Kargo (USD)": shipping,
            "İndirim (USD)": coupon,
            "Gümrük (USD)": import_fees
        }
    except:
        return None

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('files')
        kur_tipi = request.form.get('kur_tipi')
        kur = 38.0862 if kur_tipi == 'otomatik' else float(request.form.get('manuel_kur', '38.0'))

        results = []
        for file in files:
            data = extract_data_from_pdf(file.read())
            if data:
                data["Ürün Fiyatı (TL)"] = round(data["Ürün Fiyatı (USD)"] * kur, 2)
                data["Kargo (TL)"] = round(data["Kargo (USD)"] * kur, 2)
                data["İndirim (TL)"] = round(data["İndirim (USD)"] * kur, 2)
                data["Gümrük (TL)"] = round(data["Gümrük (USD)"] * kur, 2)
                data["Toplam (TL)"] = round(
                    data["Ürün Fiyatı (TL)"] + data["Kargo (TL)"] + data["Gümrük (TL)"] + data["İndirim (TL)"], 2)
                results.append(data)

        df = pd.DataFrame(results)
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return send_file(output, as_attachment=True, download_name="faturalar_tl.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    return render_template_string(HTML_FORM)

if __name__ == '__main__':
    app.run(debug=True)
