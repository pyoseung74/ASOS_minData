import pandas as pd
import os

# 파일 경로 설정
input_directory = r'C:/Users/pyose/Desktop/rainfall/before'  # 입력 경로
output_directory = r'C:/Users/pyose/Desktop/rainfall/after'  # 출력 경로

def get_target_files():
    # 대상 파일 필터링
    files = [f for f in os.listdir(input_directory) if (f.startswith('OBS_AWS_TIM') or f.startswith('OBS_AWS_MI') or f.startswith('OBS_ASOS')) and f.endswith('.csv')]
    if not files:
        print("CSV 파일을 찾을 수 없습니다.")
        return []
    return [os.path.join(input_directory, f) for f in files]

def process_file(file_path):
    # CSV 파일 불러오기
    try:
        data = pd.read_csv(file_path, encoding='euc-kr')
    except UnicodeDecodeError:
        print(f"파일을 불러오는데 실패했습니다. 인코딩을 확인해주세요: {file_path}")
        return

    # 날짜 추출 및 파일 이름 생성
    date_str = pd.to_datetime(data['일시'].iloc[0]).strftime('%m%d')
    if '1분 강수량(mm)' in data.columns:
        output_file = os.path.join(output_directory, f"AWS_MIN_{date_str}.xlsx")
    elif '누적강수량(mm)' in data.columns:
        output_file = os.path.join(output_directory, f"ASOS_MIN_{date_str}.xlsx")
    else:
        if 'AWS' in file_path:
            output_file = os.path.join(output_directory, f"AWS_HR_{date_str}.xlsx")
        elif 'ASOS' in file_path:
            output_file = os.path.join(output_directory, f"ASOS_HR_{date_str}.xlsx")

    # 지역별 시트를 나누고 파일 저장
    regions = data['지점명'].unique()

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for region in regions:
            region_data = data[data['지점명'] == region]
            region_data.to_excel(writer, sheet_name=region, index=False)

    print(f"엑셀 파일이 생성되었습니다: {output_file}")

def process_all_files():
    files = get_target_files()
    if not files:
        return
    for file_path in files:
        process_file(file_path)

# 모든 파일 처리 실행
process_all_files()
