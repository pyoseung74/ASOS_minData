import pandas as pd
import os
#import schedule
#import time

# 파일 경로 설정
base_directory = r'C:/Users/home/Downloads'

def get_latest_file():
    files = [f for f in os.listdir(base_directory) if (f.startswith('OBS_AWS_TIM') or f.startswith('OBS_AWS_MI') or f.startswith('OBS_ASOS')) and f.endswith('.csv')]
    if not files:
        print("CSV 파일을 찾을 수 없습니다.")
        return None
    latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(base_directory, x)))
    return os.path.join(base_directory, latest_file)

def process_file():
    file_path = get_latest_file()
    if file_path is None:
        return

    # CSV 파일 불러오기
    try:
        data = pd.read_csv(file_path, encoding='euc-kr')
    except UnicodeDecodeError:
        print("파일을 불러오는데 실패했습니다. 인코딩을 확인해주세요.")
        return

    # 날짜 추출 및 파일 이름 생성
    date_str = pd.to_datetime(data['일시'].iloc[0]).strftime('%m%d')
    if '1분 강수량(mm)' in data.columns:
        output_file = os.path.join(base_directory, f'AWS_MIN_{date_str}.xlsx')
    elif '누적강수량(mm)' in data.columns:
        output_file = os.path.join(base_directory, f'ASOS_MIN_{date_str}.xlsx')
    else:
        if 'AWS' in file_path:
            output_file = os.path.join(base_directory, f'AWS_HR_{date_str}.xlsx')
        elif 'ASOS' in file_path:
            output_file = os.path.join(base_directory, f'ASOS_HR_{date_str}.xlsx')

    # 지역별 시트를 나누고 파일 저장
    regions = data['지점명'].unique()

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for region in regions:
            region_data = data[data['지점명'] == region]
            region_data.to_excel(writer, sheet_name=region, index=False)

    print(f"엑셀 파일이 생성되었습니다: {output_file}")

get_latest_file()
process_file()