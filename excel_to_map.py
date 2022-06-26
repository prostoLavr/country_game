from openpyxl import load_workbook
import os
import pickle
read_file = input('Excel file: ').strip()
write_file = os.path.join('maps', input('Map name: ').strip() + ".pickle")
wb = load_workbook(read_file)
ws = wb.active
map_list = [[cell.value for cell in row] for row in ws.iter_rows()]
with open(write_file, 'wb') as mapfile:
    pickle.dump(map_list, mapfile)
print('Файл сохранён')

