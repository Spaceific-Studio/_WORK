import re
import csv
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog
import docx
from docx import Document

def read_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def parse_document(content):
    data = defaultdict(lambda: defaultdict(list))
    total_quantity = defaultdict(float)
    total_price = defaultdict(float)
    
    pattern = re.compile(r'\*(\d+)\*\s+\*M\*\s+\*([^*]+)\*\s+\*([^*]+)\*\s+\*([^*]+)\*\s+\*([^*]+)\*\s+\*([^*]+)\*\s+\*([^*]+)\*')
    
    for match in pattern.finditer(content):
        _, code, description, unit, quantity, price, _ = match.groups()
        
        vv_lines = content[match.end():].split('\n')
        oznaceni_typu = ''
        oznaceni = ''
        kod_sestavy = ''
        
        for line in vv_lines:
            if '\"označení typu' in line:
                oznaceni_typu = line.split('\"označení typu')[-1].strip()
            elif '\"označení' in line and '\"označení typu' not in line:
                oznaceni = line.split('\"označení')[-1].strip()
            elif '\"kód sestavy' in line:
                kod_sestavy = line.split('\"kód sestavy')[-1].strip()
            if 'F0' in line:
                break
        
        quantity = float(quantity.replace(',', '.'))
        price = float(price.replace(' ', ''))
        
        data[oznaceni_typu][oznaceni].append({
            'Kód sestavy': kod_sestavy,
            'Popis': description,
            'MJ': unit,
            'Množství': quantity,
            'J.cena [CZK]': price
        })
        
        total_quantity[oznaceni_typu] += quantity
        total_price[oznaceni_typu] += quantity * price
    
    return data, total_quantity, total_price

def generate_table(data, total_quantity, total_price, output_file=None):
    headers = ["Označení typu", "Kód sestavy", "Označení", "Popis", "MJ", "Množství", "J.cena [CZK]"]
    rows = []
    
    for oznaceni_typu, oznaceni_dict in data.items():
        for oznaceni, items in oznaceni_dict.items():
            for item in items:
                rows.append([
                    oznaceni_typu,
                    item['Kód sestavy'],
                    oznaceni,
                    item['Popis'],
                    item['MJ'],
                    f"{item['Množství']:.3f}",
                    f"{item['J.cena [CZK]']:.2f}"
                ])
        
        rows.append([
            f"**Total for {oznaceni_typu}**",
            "",
            "",
            "",
            "",
            f"**{total_quantity[oznaceni_typu]:.3f}**",
            f"**{total_price[oznaceni_typu]:.2f}**"
        ])
        rows.append([""] * 7)  # Empty row for separation
    
    if output_file:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(rows)
        print(f"Table has been saved to {output_file}")
    else:
        # Print to console
        print(" | ".join(headers))
        print("-" * (len(" | ".join(headers))))
        for row in rows:
            print(" | ".join(row))

# Main execution
def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Open file dialog
    file_path = filedialog.askopenfilename(title="Select input file", filetypes=[("Word Document", "*.docx"), ("All files", "*.*")])
    
    if not file_path:
        print("No file selected. Exiting.")
        return

    # Read content from the selected file
    try:
        content = read_docx(file_path)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    data, total_quantity, total_price = parse_document(content)

    # Open file dialog for saving CSV
    output_file = filedialog.asksaveasfilename(title="Save CSV file", defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    
    if output_file:
        generate_table(data, total_quantity, total_price, output_file)
    else:
        print("No output file selected. Printing to console:")
        generate_table(data, total_quantity, total_price)

if __name__ == "__main__":
    main()