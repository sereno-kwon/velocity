# Velocity Korea

velocity.rubiworkshop.com 원페이지 정적 사이트 (GitHub Pages). quoc.rubiworkshop.com과 같은 구조와 디자인 체계입니다.

- `index.html` 한국어 원페이지 (VELOCITY · RANGE · DEEP V · ROAD · TOURING · GRAVEL/MTB · RIM GUIDE · STORY · SHOWROOM)
- 디자인은 rubi.kr과 같은 체계: 영문 Pretendard · 한글 에스코어 드림, 웨이트 400, 흑백과 얇은 라인, 각진 버튼, 라이트/다크 자동. 일본어 페이지는 빌드 시 Noto Sans JP로 바뀝니다.
- 헤더 로고는 이미지가 아닌 글자(`VELOCITY` 워드마크)입니다. 공식 로고로 바꾸려면 `.logo` 안의 `<span class="wordmark">`를 `<img>`로 교체하세요.
- `en/index.html`, `ja/index.html` 영어 · 일본어 페이지 (빌드로 생성, 직접 수정하지 않음)
- `index.src.html` 편집용 한국어 원본. 림 가이드 표는 `{{RIM_TABLE}}` 자리에 빌드 시 채워집니다 (`tools/build.py`의 `RIMS`).
- `i18n/` 번역 사전 (`ko.json` 원문 목록, `en.json` · `ja.json` 원문→번역)
- `tools/build.py` 한국어 페이지, 번역 페이지, sitemap.xml을 한 번에 생성
- `tools/fetch_images.py` + `.github/workflows/fetch-images.yml` Velocity USA 공식 사이트(velocityusa.com)에서 이미지 받기
- `404.html` 하위 주소(/deep-v, /quill, /cliffhanger, /dually, /rim-guide, /dealers 등)를 섹션으로 연결
- `images/` 섹션별 이미지 (`hero`, `brand`, `deepv`, `chukker`, `quill`, `aileron`, `cliffhanger`, `atlas`, `bluntss`, `blunt35`, `dually`), 파비콘, `og.jpg`

## 처음 올릴 때
1. 이 폴더를 `sereno-kwon/velocity`의 main에 푸시합니다.
2. Settings → Pages → Source: Deploy from a branch, Branch: main / (root).
3. 도메인 DNS에 `velocity` CNAME 레코드를 `sereno-kwon.github.io`로 추가하고, Pages 설정의 Custom domain에 `velocity.rubiworkshop.com`을 넣습니다 (CNAME 파일은 이미 들어 있음). 인증서가 발급되면 Enforce HTTPS를 켭니다.
4. Actions → Fetch images from Velocity USA → Run workflow 로 이미지를 받습니다 (`tools/fetch_images.py`를 고쳐 푸시해도 실행됩니다). 받은 이미지는 자동으로 커밋됩니다.
5. 파비콘(`images/favicon-48.png`, `favicon-96.png`, `apple-touch-icon.png`, `logo-512.png`)은 딥 V 단면 모양으로 임시 생성한 것입니다. 공식 로고 파일이 있으면 같은 이름으로 덮어쓰세요.

## 이미지
`fetch_images.py`는 velocityusa.com(Shopify)의 `/products.json`에서 모델 이름이 맞는 제품 사진을, 메인 · About 페이지에서 큰 이미지를 골라 저장합니다.
- 이미 있는 파일은 건너뜁니다. 바꾸려면 파일을 지우고 다시 실행하거나, 루비에서 직접 촬영한 사진을 같은 경로에 덮어쓰면 됩니다.
- 어떤 원본을 받았는지는 `images/_sources.txt`에 남습니다.
- 모델을 찾지 못하면 로그에 `FAIL`이 찍힙니다. `MODELS`의 제목 정규식을 실제 제품명에 맞게 고치세요.
- 브랜드 사진(`hero/`, `brand/`)은 페이지에서 자동으로 고르므로, 받은 뒤 한 번 확인하고 마음에 들지 않는 컷은 교체하세요.

## 문구 수정과 번역
1. `index.src.html`의 한국어 문구를 고칩니다.
2. `python3 tools/build.py` 로 한국어 페이지를 만들고, `python3 i18n/extract.py` 로 `ko.json`을 갱신합니다.
3. 새로 생기거나 바뀐 한국어 문장을 `en.json` · `ja.json`에 같은 키로 추가합니다. HTML 태그는 원문과 똑같이 유지합니다.
4. 다시 `python3 tools/build.py` 를 실행하면 번역되지 않은 문장이 있을 때 목록으로 알려줍니다.

빌드에는 `beautifulsoup4`가 필요합니다 (`pip install beautifulsoup4`).

## 확인이 필요한 내용
- 사양: 림 가이드 표와 각 Specification의 수치는 공개 자료로 확인한 대표 사양만 넣었고, 확인하지 못한 칸은 `-`로 두었습니다 (`tools/build.py`의 `RIMS`). 수입 모델 기준으로 채워 주세요.
- 링크: SHOP 버튼과 "루비워크샵에서 보기"는 `https://rubiworkshop.com/velocity`로 연결됩니다. 실제 상품 페이지 주소가 다르면 일괄 치환하세요.
- 거래처 문의: 루비서플라이 02-516-8465, 카카오톡 채널 `https://pf.kakao.com/_NFnBj/chat` (QUOC와 동일).
- 푸터 Instagram은 Velocity USA 본사 계정(`instagram.com/velocityusa`)입니다. 한국 계정이 생기면 바꾸세요.
