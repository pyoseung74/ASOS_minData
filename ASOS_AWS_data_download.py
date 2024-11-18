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

def determine_file_prefix(data, file_path):
    # 데이터에 따라 파일 접두사 결정
    if '누적강수량(mm)' in data.columns:
        return "ASOS_MIN" if "ASOS" in os.path.basename(file_path) else None
    elif '강수량(mm)' in data.columns:
        return "ASOS_HR" if "ASOS" in os.path.basename(file_path) else "AWS_HR" if "AWS" in os.path.basename(file_path) else None
    elif '1분 강수량(mm)' in data.columns:
        return "AWS_MIN" if "AWS" in os.path.basename(file_path) else None
    else:
        return None

def process_file(file_path):
    # CSV 파일 불러오기
    try:
        data = pd.read_csv(file_path, encoding='euc-kr')
    except UnicodeDecodeError:
        print(f"파일을 불러오는데 실패했습니다. 인코딩을 확인해주세요: {file_path}")
        return

    # '일시' 열을 날짜 형식으로 변환
    data['일시'] = pd.to_datetime(data['일시'])

    # 파일 접두사 결정
    file_prefix = determine_file_prefix(data, file_path)
    if not file_prefix:
        print(f"적절한 파일 접두사를 결정할 수 없습니다: {file_path}")
        return

    # 날짜별로 그룹화
    grouped = data.groupby(data['일시'].dt.date)

    # 날짜별로 데이터를 저장
    for date, group in grouped:
        date_str = date.strftime('%Y%m%d')  # YYYYMMDD 형식
        output_file = os.path.join(output_directory, f"{file_prefix}_{date_str}.csv")
        
        # 지역별로 파일 저장
        regions = group['지점명'].unique()
        for region in regions:
            region_data = group[group['지점명'] == region]
            region_file = os.path.join(output_directory, f"{file_prefix}_{date_str}_{region}.csv")
            region_data.to_csv(region_file, index=False, encoding='utf-8-sig')

        print(f"CSV 파일이 생성되었습니다: {output_file}")

def process_all_files():
    files = get_target_files()
    if not files:
        return
    for file_path in files:
        process_file(file_path)

# 모든 파일 처리 실행
process_all_files()
