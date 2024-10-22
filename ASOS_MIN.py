from urllib.request import urlopen
from urllib.parse import urlencode, unquote, quote_plus
import urllib
import json
from xml.etree.ElementTree import parse
import xmltodict

import pandas as pd
import numpy as np
import time
import os
from datetime import datetime

class ASOS():
    def __init__(self,std: list, # Area_code
                 start_year: str, # YYYY ex) 2021
                 end_year: str, # YYYY ex) 2022
                 start_date: str= '0101', # MMDD
                 end_date: str= '1231', # MMDD
                 startMm: str= '00', # MM
                 endMm: str= '59', # MM
                 url: str= 'http://apis.data.go.kr/1360000/AsosMinuteInfoService/getWthrDataList'): # Updated URL for minute data
        self.std = std
        self.start_year = start_year
        self.end_year = end_year
        self.start_date = start_date
        self.end_date = end_date
        self.startMm = startMm
        self.endMm = endMm
        self.url = url
        self.flagmax = 10

        self.keys = []

    # key 추가
    def add_keys(self,key: str) -> None:
        self.keys.append(key)

    # 지역 추가
    def add_std(self,std: int) -> None:
        self.std.append(std)

    # ASOS 데이터 가져오기
    def Crwal(self) -> None:
        for std in self.std:
            df = pd.DataFrame()
            print(f'지점번호 {std} 시작 -- {datetime.now().time()}')
            breaker = False
            for year in range(int(self.start_year),int(self.end_year)+1,1):
                print(f'{year}년 시작', end = ' ')
                flag=0
                if breaker == True:
                    break
                page = 1
                key_idx = 0                
                while flag<self.flagmax:
                    key = self.keys[key_idx]
                    try:
                        queryParams = '?' + urlencode({
                                quote_plus('ServiceKey') : key,
                                quote_plus('pageNo') : f'{page}',   # 1 ~ 10
                                quote_plus('numOfRows') : '1440',  # Data for every minute in a day (60*24)
                                quote_plus('dataType') : 'XML',
                                quote_plus('dataCd') : 'ASOS',
                                quote_plus('dateCd') : 'MN',
                                quote_plus('startDt') : f'{year}{self.start_date}',
                                quote_plus('endDt') : f'{year}{self.end_date}',
                                quote_plus('startMm') : self.startMm,
                                quote_plus('endMm') : self.endMm,
                                quote_plus('stnIds') : f'{std}'})
                        request = urllib.request.Request(self.url + unquote(queryParams))

                        response_body = urlopen(request, timeout=60).read()

                        decode_data = response_body.decode('utf-8')

                        xml_parse = xmltodict.parse(decode_data)     # string인 xml 파싱
                        xml_dict = json.loads(json.dumps(xml_parse))
                        result = xml_dict['response']['header']['resultMsg']
                        if result == 'NO_DATA':
                            breaker = True
                            break
                        elif result == 'LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR':
                            print('서비스 요청 제한횟수 초과')
                            time.sleep(5)
                            key_idx += 1
                            if key_idx >= len(self.keys):
                                key_idx = 0
                            continue
                        dicts = xml_dict['response']['body']['items']['item']

                        df_temp = pd.DataFrame(columns = ['날짜', '시간', '분', '지점_번호', '지점명', '기온', '강수량', '풍속', '풍향', '습도', '증기압', '이슬점온도', '현지기압', '해면기압', '일조', '일사', '적설', '3시간_신절설', '전운량', '중하층운량', '운형', '최저운고', '시정', '지면온도', '5cm_지중온도', '10cm_지중온도', '20cm_지중온도', '30cm_지중온도'])

                        for i in range(len(dicts)):
                            df_temp.loc[i] = [dicts[i]['tm'][:10], dicts[i]['tm'][11:13], dicts[i]['tm'][14:], dicts[i]['stnId'], dicts[i]['stnNm'], dicts[i]['ta'], dicts[i]['rn'], dicts[i]['ws'], dicts[i]['wd'], dicts[i]['hm'], dicts[i]['pv'], dicts[i]['td'], dicts[i]['pa'], dicts[i]['ps'], dicts[i]['ss'], dicts[i]['icsr'], dicts[i]['dsnw'], dicts[i]['hr3Fhsc'], dicts[i]['dc10Tca'], dicts[i]['dc10LmcsCa'], dicts[i]['clfmAbbrCd'], dicts[i]['lcsCh'], dicts[i]['vs'], dicts[i]['ts'], dicts[i]['m005Te'], dicts[i]['m01Te'], dicts[i]['m02Te'], dicts[i]['m03Te']]
                        df = pd.concat([df, df_temp])
                        print(f'{page}page 완료', end = ' ')
                        page += 1
                    except:
                        print(f'{page}page 오류 다시 시작. 시도횟수 {flag}/{self.flagmax} error code : {result}', end = ' ')
                        flag+=1
                    if page == 11:
                        break

                print()
                print(f'{year}완료 -- {datetime.now().time()}')
            
            if len(df.values) != 0:
                place = df['지점명'].unique()[0]
                path = f'./Data/{place}'
                if not os.path.exists(path):
                    os.makedirs(path)
                df.to_csv(f"./Data/{df['지점명'].unique()[0]}/{df['지점명'].unique()[0]}" + ".csv", index = False,encoding='utf-8 sig')
                print(f'지점번호 {std} 완료 -- {datetime.now().time()}')
            else:
                print(f'지점번호 {std} NO DATA')
