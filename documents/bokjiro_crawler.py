import time
import json
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def parse_service_detail(link: str) -> dict:
    """상세 페이지 접속 후, 주요 필드 파싱"""
    try:
        res = requests.get(link, timeout=10)
        soup = BeautifulSoup(res.text, "lxml")

        title = soup.select_one(".twat-view-title").text.strip()

        def safe_select_text(selector):
            el = soup.select_one(selector)
            return el.text.strip() if el else ""

        return {
            "title": title,
            "지원대상": safe_select_text(".twat-view-cont .target"),
            "내용": safe_select_text(".twat-view-cont .cont"),
            "신청방법": safe_select_text(".twat-view-cont .way"),
            "문의처": safe_select_text(".twat-view-cont .contact"),
            "원문링크": link
        }

    except Exception as e:
        print(f"[X] 상세 파싱 실패: {link} ({e})")
        return {}


def crawl_bokjiro():
    """복지로 크롤링 메인 함수"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get("https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/moveTWAT52005M.do")

    wait = WebDriverWait(driver, 10)
    all_data = []

    region_select = Select(wait.until(EC.presence_of_element_located((By.ID, "ctpvCd"))))
    for region_option in region_select.options:
        region_value = region_option.get_attribute("value")
        region_name = region_option.text.strip()
        if not region_value:
            continue

        region_select.select_by_value(region_value)
        time.sleep(1)

        provider_select = Select(wait.until(EC.presence_of_element_located((By.ID, "svcTrgtCd"))))
        for provider_option in provider_select.options:
            provider_value = provider_option.get_attribute("value")
            provider_name = provider_option.text.strip()
            if not provider_value:
                continue

            provider_select.select_by_value(provider_value)
            time.sleep(1)

            try:
                driver.find_element(By.CLASS_NAME, "btn_inquire").click()
                time.sleep(2)

                service_rows = driver.find_elements(By.CSS_SELECTOR, ".boardList tbody tr")
                for row in service_rows:
                    title_el = row.find_element(By.CSS_SELECTOR, "td.subject a")
                    title = title_el.text.strip()
                    link = title_el.get_attribute("href")

                    detail = parse_service_detail(link)
                    if detail:
                        detail.update({
                            "지역": region_name,
                            "제공주체": provider_name
                        })
                        print(f"[✓] {region_name} | {provider_name} | {detail['title']}")
                        all_data.append(detail)

            except Exception as e:
                print(f"[X] 오류: {region_name} - {provider_name} ({e})")
                continue

    driver.quit()
    return all_data


if __name__ == "__main__":
    data = crawl_bokjiro()
    print(f"\n📦 총 수집된 서비스 수: {len(data)}")

# 저장 경로
    os.makedirs("data", exist_ok=True)
    output_path = "data/bokjiro_services.json"

    # JSON 저장
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 저장 완료: {output_path}")