from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

import os
import boto3
from boto3.dynamodb.conditions import Key
import requests

load_dotenv()

app = Flask(__name__)

# DynamoDB 클라이언트 설정
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)
table = dynamodb.Table('CoinHolderCrawledData')  # DynamoDB 테이블 이름

@app.route('/')
def home():
    return "DynamoDB is connected!", 200

@app.route('/store', methods=['POST'])
def store_data():
    # 요청 데이터 가져오기
    data = request.json
    if not data or 'url' not in data:
        return jsonify({"error": "Invalid input"}), 400
    
    html_source = fetch_html(data['url'])
    if html_source:
        parsed_html_souce = html_parser(html_source)
        # 한국 시간대 (UTC+9)
        KST = timezone(timedelta(hours=9))
        # 현재 시간 (한국 시간 기준)
        current_datetime = datetime.now(KST).strftime('%Y%m%d%H%M%S')
        # DynamoDB에 데이터 저장
        table.put_item(Item={
            'url': data['url'],
            'content': parsed_html_souce,
            'timestamp': current_datetime
        })
    return jsonify({"message": "Data stored successfully"}), 201

def fetch_html(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        # HTTP 요청 보내기
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 처리
        # HTML 소스 가져오기
        html_content = response.text
        return html_content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the HTML: {e}")
        return None

def html_parser(html_content):
    result = ''
     # BeautifulSoup로 HTML 파싱
    soup = BeautifulSoup(html_content, "html.parser")

    # 특정 <tbody> 태그 선택
    tbody = soup.find("tbody", {"class": "align-middle text-nowrap"})

    # <tbody>의 내용 리턴
    if tbody:
        print("Extracted Data:")
        # 모든 <tr> 태그 찾기
        rows = tbody.find_all("tr")

        for row in rows:
            # 각 <td> 데이터 추출
            cols = row.find_all("td")
            data = [col.text.strip() for col in cols]
            result+='/ '.join(data)+'\n'
        return result
        # return ', '.join(data)
    else:
        print("No <tbody> tag found")

@app.route('/data', methods=['GET'])
def get_data():
    try:
        # 쿼리 매개변수에서 url과 timestamp 범위 가져오기
        url = request.args.get('url')
        start_timestamp = request.args.get('start_timestamp')
        end_timestamp = request.args.get('end_timestamp')

        # 필수 파라미터 검증
        if not url or not start_timestamp or not end_timestamp:
            return jsonify({"error": "Missing required parameters"}), 400

        # DynamoDB 조건 검색 (timestamp 범위 지정)
        response = table.query(
            KeyConditionExpression=Key('url').eq(url) & Key('timestamp').between(start_timestamp, end_timestamp)
        )

        # 결과 확인
        items = response.get('Items')
        if not items:
            return jsonify({"error": "No data found in the given range"}), 404

        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()

