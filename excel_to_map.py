from openpyxl import load_workbook
import os
import pickle



def main():
    read_file = input('Excel file: ').strip()
    if not os.path.isfile(read_file):
        return 'File is not found'


    wb = load_workbook(read_file)
    ws = wb.active
    map_list = [[cell.value for cell in row] for row in ws.iter_rows()]

    if not map_list:
        return 'File is empty' 

    map_name = input('Map name: ').strip().replace('_', '-')

    def formating(i, j):
        return os.path.join('maps', f'{map_name}_{i}_{j}.pickle')

    for i in range(len(map_list) // 9):
        for j in range(len(map_list[0]) // 16):
            write_file = formating(i, j)
             
            with open(write_file, 'wb') as mapfile:
                pickle.dump(map_list[i * 9:(i+1) * 9][j * 16:(j+1) * 16], mapfile)

            print(f'File {write_file} saved')

    return ''


if __name__ == "__main__":
    while (res := main()) != '':
        print(f'\n{res}\nRETRY\n') 
    print('Success!')

