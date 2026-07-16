import json
import sqlite3
import argparse
import os
from datetime import datetime

# Khởi tạo hoặc kết nối DB
def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vulnerabilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool TEXT,
            severity TEXT,
            name TEXT,
            description TEXT,
            path_or_url TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

def parse_semgrep(file_path, conn):
    if not os.path.exists(file_path):
        print(f"[!] Không tìm thấy file Semgrep: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cursor = conn.cursor()
    count = 0
    for result in data.get('results', []):
        tool = 'Semgrep (SAST)'
        severity = result.get('extra', {}).get('severity', 'UNKNOWN')
        name = result.get('check_id', 'Unknown Check')
        description = result.get('extra', {}).get('message', '')
        path = result.get('path', '')
        
        cursor.execute('''
            INSERT INTO vulnerabilities (tool, severity, name, description, path_or_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (tool, severity, name, description, path))
        count += 1
    
    conn.commit()
    print(f"[+] Đã thêm {count} lỗi từ Semgrep vào database.")

def parse_zap(file_path, conn):
    if not os.path.exists(file_path):
        print(f"[!] Không tìm thấy file ZAP: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cursor = conn.cursor()
    count = 0
    # Cấu trúc ZAP JSON tuỳ thuộc vào version, thường là một mảng alerts hoặc chứa mảng site
    sites = data.get('site', [])
    for site in sites:
        for alert in site.get('alerts', []):
            tool = 'OWASP ZAP (DAST)'
            severity = alert.get('riskdesc', alert.get('riskcode', 'UNKNOWN'))
            name = alert.get('name', alert.get('alert', 'Unknown Alert'))
            description = alert.get('desc', '')
            url = ""
            if alert.get('instances') and len(alert['instances']) > 0:
                url = alert['instances'][0].get('uri', '')
            
            cursor.execute('''
                INSERT INTO vulnerabilities (tool, severity, name, description, path_or_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (tool, severity, name, description, url))
            count += 1
    
    conn.commit()
    print(f"[+] Đã thêm {count} lỗi từ OWASP ZAP vào database.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse SAST/DAST results into Data Lake (SQLite)')
    parser.add_argument('--semgrep', type=str, help='Đường dẫn tới file JSON của Semgrep', default='semgrep-report.json')
    parser.add_argument('--zap', type=str, help='Đường dẫn tới file JSON của ZAP', default='zap-report.json')
    parser.add_argument('--db', type=str, help='Đường dẫn tới SQLite Database', default='../data-lake/vuln_data.db')
    
    args = parser.parse_args()
    
    db_path = os.path.abspath(args.db)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    print(f"[*] Đang sử dụng database tại: {db_path}")
    conn = init_db(db_path)
    
    parse_semgrep(args.semgrep, conn)
    parse_zap(args.zap, conn)
    
    conn.close()
    print("[*] Hoàn tất!")
