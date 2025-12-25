from flask import Flask, jsonify, request
import csv
import os

app = Flask(__name__)

def search_vergi(isim=None, ilce=None, vergi_dairesi=None, limit=50):
    """CSV'de vergi kayıtlarını ara"""
    results = []
    count = 0
    
    with open('289kivd.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        for row in reader:
            if len(row) >= 7:
                # CSV yapısı: ID, İsim, ?, Vergi Dairesi, İlçe, Adres, Vergi No
                match = True
                
                if isim and isim.upper() not in row[1].upper():
                    match = False
                    
                if ilce and ilce.upper() not in row[4].upper():
                    match = False
                    
                if vergi_dairesi and vergi_dairesi.upper() not in row[3].upper():
                    match = False
                
                if match:
                    # Vergi numarasını temizle
                    vergi_no = row[6].replace('\\', '').strip() if len(row) > 6 else ''
                    
                    results.append({
                        'id': row[0],
                        'isim': row[1],
                        'kodu': row[2],
                        'vergi_dairesi': row[3],
                        'ilce': row[4],
                        'adres': row[5],
                        'vergi_no': vergi_no
                    })
                    count += 1
                    
                    if count >= limit:
                        break
    
    return results

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>289K Vergi API</title><meta charset="utf-8"></head>
    <body>
        <h1>🏛️ 289K Vergi/Maliye Veritabanı API</h1>
        <p><strong>Kurucu:</strong> @sukazatkinis</p>
        <p><strong>Telegram:</strong> @f3system</p>
        <p><strong>API Endpoint'leri:</strong></p>
        <ul>
            <li><code>/f3system/api/vergi?isim=RAMAZAN</code></li>
            <li><code>/f3system/api/vergi?ilce=MERKEZ&vergi_dairesi=VERGİ</code></li>
            <li><code>/f3system/api/vergi?vergi_no=11338465102</code></li>
            <li><code>/f3system/api/vergi?limit=10</code></li>
        </ul>
    </body>
    </html>
    """

@app.route('/f3system/api/vergi')
def vergi_api():
    isim = request.args.get('isim', '')
    ilce = request.args.get('ilce', '')
    vergi_dairesi = request.args.get('vergi_dairesi', '')
    vergi_no = request.args.get('vergi_no', '')
    limit = min(int(request.args.get('limit', 50)), 100)
    
    results = search_vergi(isim=isim, ilce=ilce, vergi_dairesi=vergi_dairesi, limit=limit)
    
    # Vergi numarasına göre filtrele
    if vergi_no:
        filtered = []
        for kayit in results:
            if vergi_no in kayit['vergi_no']:
                filtered.append(kayit)
        results = filtered
    
    return jsonify({
        'sorgu': {'isim': isim, 'ilce': ilce, 'vergi_dairesi': vergi_dairesi, 'vergi_no': vergi_no},
        'bulunan': len(results),
        'sonuclar': results,
        'kurucu': '@sukazatkinis',
        'telegram': '@f3system',
        'aciklama': '289.000 vergi/maliye verisi - Sadece eğitim amaçlıdır'
    })

@app.route('/f3system/api/vergi/<int:kayit_id>')
def vergi_by_id(kayit_id):
    with open('289kivd.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == str(kayit_id):
                vergi_no = row[6].replace('\\', '').strip() if len(row) > 6 else ''
                
                return jsonify({
                    'id': row[0],
                    'isim': row[1],
                    'kodu': row[2],
                    'vergi_dairesi': row[3],
                    'ilce': row[4],
                    'adres': row[5],
                    'vergi_no': vergi_no,
                    'kurucu': '@sukazatkinis',
                    'telegram': '@f3system'
                })
    
    return jsonify({'error': 'Kayıt bulunamadı'}), 404

# Vergi numarasına göre arama
@app.route('/f3system/api/vergi/numara/<vergi_no>')
def vergi_by_number(vergi_no):
    results = []
    with open('289kivd.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > 6 and vergi_no in row[6]:
                results.append({
                    'id': row[0],
                    'isim': row[1],
                    'vergi_dairesi': row[3],
                    'ilce': row[4],
                    'vergi_no': row[6].replace('\\', '').strip()
                })
                if len(results) >= 10:
                    break
    
    return jsonify({
        'vergi_no': vergi_no,
        'bulunan': len(results),
        'sonuclar': results
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
