# import pandas as pd
# import datetime
# import os
# import platform
# import binascii
# import subprocess

# def hex_to_ascii(hex_list):
#     chars = []
#     for h in hex_list:
#         try:
#             byte_data = binascii.unhexlify(h)
#             ascii_str = byte_data.decode('ascii', errors='replace')
#             chars.append(ascii_str)
#         except:
#             chars.append('?')
#     return ''.join(chars).strip()

# def decode_signed_16bit(hex_str, bits=16):
#     val = int(hex_str, 16)
#     if val & (1 << (bits - 1)):
#         val -= 1 << bits
#     return val

# def decode_float_from_hex(hex_str):
#     try:
#         val = decode_signed_16bit(hex_str)
#         return round(val / 1000.0, 3)
#     except:
#         return None

# def dms_to_angle(d, m, s):
#     try:
#         deg = decode_signed_16bit(d)
#         min_ = decode_signed_16bit(m)
#         sec = decode_signed_16bit(s)

#         if deg < 0:
#             return f"-{abs(deg)}°{abs(min_)}'{abs(sec)}?"
#         elif min_ < 0:
#             return f"{abs(deg)}°-{abs(min_)}'{abs(sec)}?"
#         elif sec < 0:
#             return f"{abs(deg)}°{abs(min_)}'-{abs(sec)}?"
#         else:
#             return f"{deg}°{min_}'{sec}?"
#     except:
#         return "Invalid"

# def get_date_time_from_hex(hex7, hex8, hex9):
#     try:
#         hex7 = hex7.zfill(4)
#         hex8 = hex8.zfill(4)
#         hex9 = hex9.zfill(4)

#         year = int(hex7[:2]) + 2000  
#         month = int(hex7[2:])    
#         day = int(hex8[:2])
#         hour = int(hex8[2:])
#         minute = int(hex9[:2])
#         second = int(hex9[2:])

#         date_str = f"{day:02d}/{month:02d}/{year}"
#         time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
#         return date_str, time_str
#     except:
#         return "Invalid Date", "Invalid Time"

# def judge_flag(row):
#     try:
#         val_36 = row[36].upper()
#         val_37 = row[37].upper()
#         if val_36 == "80FF" and val_37 == "80C0":
#             return "OK"
#         else:
#             return "NG"
#     except:
#         return "NG"

# def decode_buff_status(val):
#     val = val.upper()
#     if val == "0003":
#         return "OK"
#     elif val == "0002":
#         return "NG"
#     elif val == "0001":
#         return "Pass"
#     else:
#         return "NG"

# def process_row(row):
#     row = [str(cell).zfill(4).upper() for cell in row if pd.notna(cell)]
#     if len(row) < 80:
#         raise ValueError("Incomplete row - skipping")

#     lot_data = hex_to_ascii(row[0:5])
#     car_type = hex_to_ascii(row[40:43])
#     repair_code = hex_to_ascii(row[73:80])

#     date_str, time_str = get_date_time_from_hex(row[7], row[8], row[9])

#     toe_l    = dms_to_angle(row[10],  row[11],  row[12])
#     cam_l    = dms_to_angle(row[13],  row[14],  row[15])
#     toe_r    = dms_to_angle(row[16],  row[17],  row[18])
#     cam_r    = dms_to_angle(row[19],  row[20],  row[21])
#     toe_add  = dms_to_angle(row[22],  row[23],  row[24])
#     toe_sub  = dms_to_angle(row[25],  row[26],  row[27])
#     cam_add  = dms_to_angle(row[28],  row[29],  row[30])
#     cam_sub  = dms_to_angle(row[31],  row[32],  row[33])

#     hub_l  = decode_float_from_hex(row[48])
#     boss_l = decode_float_from_hex(row[49])
#     seat_l = decode_float_from_hex(row[51])
#     hub_r  = decode_float_from_hex(row[52])
#     seat_r = decode_float_from_hex(row[55])

#     buff1 = decode_buff_status(row[70])
#     buff2 = decode_buff_status(row[71])

#     line_no = int(row[72], 16)
#     if line_no == 0:
#         line_no = "None"

#     judge_final = judge_flag(row)

#     return [
#         lot_data, repair_code, date_str, time_str, car_type,
#         toe_l, cam_l, toe_r, cam_r, toe_add, toe_sub,
#         cam_add, cam_sub, boss_l, seat_l, seat_r, hub_l, hub_r,
#         buff1, buff2, line_no, judge_final
#     ]

# def main():
#     input_file = "robot_hex_data.csv"
#     timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#     output_file_all = f"decoded_robot_data_{timestamp}.csv"
#     output_file_ok = f"decoded_robot_data_OK_{timestamp}.csv"
#     output_file_ng = f"decoded_robot_data_NG_{timestamp}.csv"

#     try:
#         df = pd.read_csv(input_file, header=None)
#     except FileNotFoundError:
#         print(f"File not found: {input_file}")
#         return

#     df.dropna(how='all', inplace=True)
#     decoded_rows = []
#     total_rows = len(df)

#     for i in range(0, total_rows, 8):
#         try:
#             block = df.iloc[i:i+8]
#             combined_row = block.values.flatten().tolist()
#             decoded = process_row(combined_row)
#             decoded_rows.append(decoded)
#         except Exception as e:
#             print(f"⚠️ Error processing rows {i}-{i+7}: {e}")

#     decoded_rows.reverse()  # Optional: reverse to keep last input on top

#     headers = [
#         "Lot data", "Repair Code", "Date", "Time", "Car Type",
#         "TOE L", "CAM L", "TOE R", "CAM R", "TOE-ADD", "TOE-SUB",
#         "CAM-ADD", "CAM-SUB", "BOSS-L[mm]", "SEAT-L[mm]", "SEAT-R[mm]",
#         "HUB MT-L[mm]", "HUB MT-R[mm]", "BUFF 1", "BUFF 2", "Line No.", "Judge"
#     ]

#     output_df = pd.DataFrame(decoded_rows, columns=headers)
#     output_df.to_csv(output_file_all, index=False, encoding='utf-8-sig')

#     df_ok = output_df[output_df["Judge"] == "OK"]
#     df_ng = output_df[output_df["Judge"] == "NG"]

#     df_ok.to_csv(output_file_ok, index=False, encoding='utf-8-sig')
#     df_ng.to_csv(output_file_ng, index=False, encoding='utf-8-sig')

#     print(f"\nAll data saved to: {output_file_all}")
#     print(f"OK data saved to: {output_file_ok}")
#     print(f"NG data saved to: {output_file_ng}")

#     output_files = [output_file_all, output_file_ok, output_file_ng]

#     if platform.system() == "Windows":
#         for file in output_files:
#             os.startfile(file)
#     elif platform.system() == "Darwin":  # macOS
#         for file in output_files:
#             subprocess.call(["open", file])
#     elif platform.system() == "Linux":
#         for file in output_files:
#             subprocess.call(["xdg-open", file])
#     else:
#         print("Unsupported OS")

# if __name__ == "__main__":
#     main()

import pandas as pd
import datetime
import os
import platform
import binascii
import subprocess

def hex_to_ascii(hex_list):
    chars = []
    for h in hex_list:
        try:
            byte_data = binascii.unhexlify(h)
            ascii_str = byte_data.decode('ascii', errors='replace')
            chars.append(ascii_str)
        except:
            chars.append('?')
    return ''.join(chars).strip()

def decode_signed_16bit(hex_str, bits=16):
    val = int(hex_str, 16)
    if val & (1 << (bits - 1)):
        val -= 1 << bits
    return val

def decode_float_from_hex(hex_str):
    try:
        val = decode_signed_16bit(hex_str)
        return round(val / 1000.0, 3)
    except:
        return None

def dms_to_angle(d, m, s):
    try:
        deg = decode_signed_16bit(d)
        min_ = decode_signed_16bit(m)
        sec = decode_signed_16bit(s)

        return f"{deg}°{min_}'{sec}?"
    except:
        return "Invalid"

def get_date_time_from_hex(hex7, hex8, hex9):
    try:
        hex7, hex8, hex9 = hex7.zfill(4), hex8.zfill(4), hex9.zfill(4)
        year, month = int(hex7[:2]) + 2000, int(hex7[2:])
        day, hour = int(hex8[:2]), int(hex8[2:])
        minute, second = int(hex9[:2]), int(hex9[2:])

        date_str = f"{day:02d}/{month:02d}/{year}"
        time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
        return date_str, time_str
    except:
        return "Invalid Date", "Invalid Time"

def judge_flag(row):
    try:
        return "OK" if row[36].upper() == "80FF" and row[37].upper() == "80C0" else "NG"
    except:
        return "NG"

def decode_buff_status(val):
    return {"0003": "OK", "0002": "NG", "0001": "Pass"}.get(val.upper(), "NG")

def process_row(row):
    row = [str(cell).zfill(4).upper() for cell in row if pd.notna(cell)]
    if len(row) < 80:
        raise ValueError("Incomplete row - skipping")

    lot_data = hex_to_ascii(row[0:5])
    car_type = hex_to_ascii(row[40:43])
    repair_code = hex_to_ascii(row[73:80])
    date_str, time_str = get_date_time_from_hex(row[7], row[8], row[9])

    angles = [dms_to_angle(row[i], row[i+1], row[i+2]) for i in range(10, 34, 3)]
    hub_l, boss_l, seat_l = decode_float_from_hex(row[48]), decode_float_from_hex(row[49]), decode_float_from_hex(row[51])
    hub_r, seat_r = decode_float_from_hex(row[52]), decode_float_from_hex(row[55])
    buff1, buff2 = decode_buff_status(row[70]), decode_buff_status(row[71])
    line_no = int(row[72], 16) if int(row[72], 16) != 0 else "None"
    judge_final = judge_flag(row)

    return [lot_data, repair_code, date_str, time_str, car_type] + angles + [boss_l, seat_l, seat_r, hub_l, hub_r, buff1, buff2, line_no, judge_final]

def main():
    input_file = "robot_hex_data.csv"
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_all = f"decoded_robot_data_{timestamp}.csv"
    output_file_ok = f"decoded_robot_data_OK_{timestamp}.csv"
    output_file_ng = f"decoded_robot_data_NG_{timestamp}.csv"

    try:
        df = pd.read_csv(input_file, header=None).dropna(how='all')
    except FileNotFoundError:
        print(f"File not found: {input_file}")
        return

    decoded_rows = []
    for i in range(0, len(df), 8):
        try:
            block = df.iloc[i:i+8].values.flatten().tolist()
            decoded_rows.append(process_row(block))
        except Exception as e:
            print(f"⚠️ Error processing rows {i}-{i+7}: {e}")

    headers = [
        "Lot data", "Repair Code", "Date", "Time", "Car Type",
        "TOE L", "CAM L", "TOE R", "CAM R", "TOE-ADD", "TOE-SUB",
        "CAM-ADD", "CAM-SUB", "BOSS-L[mm]", "SEAT-L[mm]", "SEAT-R[mm]",
        "HUB MT-L[mm]", "HUB MT-R[mm]", "BUFF 1", "BUFF 2", "Line No.", "Judge"
    ]

    output_df = pd.DataFrame(decoded_rows, columns=headers)
    output_df.to_csv(output_file_all, index=False, encoding='utf-8-sig')

    output_df[output_df["Judge"] == "OK"].to_csv(output_file_ok, index=False, encoding='utf-8-sig')
    output_df[output_df["Judge"] == "NG"].to_csv(output_file_ng, index=False, encoding='utf-8-sig')

    print(f"\nAll data saved to: {output_file_all}")
    print(f"OK data saved to: {output_file_ok}")
    print(f"NG data saved to: {output_file_ng}")

    output_files = [output_file_all, output_file_ok, output_file_ng]
    open_files(output_files)

def open_files(files):
    if platform.system() == "Windows":
        for file in files:
            os.startfile(file)
    elif platform.system() == "Darwin":  # macOS
        for file in files:
            subprocess.call(["open", file])
    elif platform.system() == "Linux":
        for file in files:
            subprocess.call(["xdg-open", file])
    else:
        print("Unsupported OS")

if __name__ == "__main__":
    main()





