import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
def fetch_html(url):
    try:
        # HTTP 요청 보내기
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 처리
        # print(response.text)
        # HTML 소스 가져오기
        html_content = response.text
        return html_content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the HTML: {e}")
        return None
    
def save_as_text_file(html_content):
        # 텍스트 파일로 저장
        with open('file_name', "w", encoding="utf-8") as file:
            file.write(html_content)

def html_parser(html_content):
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
            print(data)
        
        # return ', '.join(data)
    else:
        print("No <tbody> tag found")

if __name__ == "__main__":
    url = "https://etherscan.io/accounts/1?ps=100"  # 크롤링할 페이지 URL
    html_source = fetch_html(url)
    
    if html_source:
        parsed_html_souce = html_parser(html_source)
        # save_as_text_file(parsed_html_souce)
