import os
import sys
import django
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from typing import Literal

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hetaeki_backend.settings")
django.setup()

from documents.models import Document
from rag.utils import store_to_vectorstore

SERVICE_KEY = os.getenv("BOKJIRO_API_KEY")

def fetch_services(source: Literal["central", "local"]):
    base_url = {
        "central": "http://apis.data.go.kr/B554287/NationalWelfareInformationsV001/NationalWelfarelistV001",
        "local": "http://apis.data.go.kr/B554287/LocalGovernmentWelfareInformations/LcgvWelfarelist",
    }[source]

    service_items = []
    page = 1
    while True:
        params = {
            "serviceKey": SERVICE_KEY,
            "pageNo": str(page),
            "numOfRows": "500",
            "_type": "xml"
        }
        if source == "central":
            params["callTp"] = "L"
            params["srchKeyCode"] = "001"

        res = requests.get(base_url, params=params)
        res.encoding = "utf-8"

        try:
            root = ET.fromstring(res.text)
        except ET.ParseError:
            print("❌ XML 파싱 실패! 응답:", res.text[:500])
            break

        items = root.findall(".//servList")
        if not items:
            break

        for item in items:
            sid = item.findtext("servId")
            title = item.findtext("servNm")
            summary = item.findtext("servDgst")
            if not sid or not title:
                continue

            if source == "local":
                ctpv = item.findtext("ctpvNm") or ""
                sgg = item.findtext("sggNm") or ""
                location = f"{ctpv} {sgg}".strip()
                summary = f"[{location}] {summary}".strip()

            service_items.append((sid, title, summary))

        page += 1

    print(f"✅ {source} 서비스 ID 수집 완료: {len(service_items)}개")
    return service_items


def collect_documents(source: Literal["central", "local"]):
    items = fetch_services(source)
    for sid, title, summary in items:
        if Document.objects.filter(service_id=sid).exists():
            print(f"⚠️ 이미 존재: {sid}")
            continue

        Document.objects.update_or_create(
            service_id=sid,
            defaults={
                "title": title,
                "description": summary,
                "source": source,
            }
        )
        store_to_vectorstore(sid, f"{title}\n{summary}")
        print(f"✅ 저장 완료: {title}")

if __name__ == "__main__":
    collect_documents("local")