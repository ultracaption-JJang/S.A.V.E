# 서버 설명 (FastAPI)
이 프로젝트는 실시간 객체 탐지 및 이미지 캡셔닝을 처리하는 FastAPI 서버입니다. 클라이언트 애플리케이션은 이 서버와 통신하여 실시간으로 객체 탐지 및 이미지 캡셔닝 서비스를 제공합니다.

## 환경 설정
서버는 Docker 환경에서 실행되며, 필요한 패키지와 종속성은 Dockerfile을 통해 설치됩니다.

**필수 요구 사항**
* Docker
* Python 3.9 이상
* FastAPI
* YOLO v11 모델
* ClipCap 모델


## 설치 방법

1. 서버 실행을 위한 환경 설정
    프로젝트 디렉토리로 이동 후, Docker 이미지를 빌드하고 서버를 실행합니다. Docker 환경이 이미 설치되어 있어야합니다.
2. Docker 빌드 및 실행
    먼저 Docker 이미지를 빌드합니다
    ```
    docker build -t clipcap-fastapi -f dockerfile/Dockerfile .
    ```
    다음으로 Docker 컨테이너를 실행합니다.
    ```
    docker run -d --name save-api-server -v /mnt/c/Users/희정/app/clipcap:/app/clipcap -p 8000:8000 clipcap-fastapi
    ```
    이 명령어는 FastAPI 서버를 Docker 컨테이너에서 백그라운드로 실행하고, `8000`포트를 열어 외부에서 접근 할 수 있게 만듭니다.

3. FastAPI 서버 실행
    서버가 정상적으로 실행되면, http://localhost:8000에서 FastAPI 서버를 통해 API를 호출할 수 있습니다.


## 서버 엔드포인트
FastAPI 서버는 다음과 같은 주요 엔드포인트를 제공합니다.
1. `/generate-caption/` - **이미지 캡션 생성**

* **설명**: 이미지를 업로드하면 ClipCap 모델을 통해 해당 이미지에 대한 캡션을 생성합니다.
* HTTP 메소드: `POST`
* **요청**:
  * file: 업로드된 이미지 파일 (형식: JPEG, PNG 등)
* **응답**:
  *`caption`: 생성된 이미지 캡션 (문자열)

**예시**:
```
curl -X 'POST' \
  'http://localhost:8000/generate-caption/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@test_image.jpg'
```

**응답**:
```
{
  "caption": "A person is standing next to a red car."
}
```
**설명**:
* 클라이언트는 이미지를 업로드하여 서버에 캡션 생성을 요청합니다.
* 서버는 이미지를 처리한 후, ClipCap 모델을 사용하여 해당 이미지에 대한 설명을 텍스트로 반환합니다.

<!-- 2. `/detect/` - **객체 탐지**
* **설명**: 업로드된 이미지에서 YOLO 모델을 사용하여 객체를 탐지합니다. 탐지된 객체들의 정보(이름, 신뢰도, 좌표)가 반환됩니다.
HTTP 메소드: POST
요청:
file: 업로드된 이미지 파일 (형식: JPEG, PNG 등)
응답:
detected_result: 탐지된 객체들의 정보 (객체 이름, 신뢰도, 좌표)
예시:

bash
코드 복사
curl -X 'POST' \
  'http://localhost:8000/detect/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@test_image.jpg'
응답:

json
코드 복사
{
  "detected_result": [
    {
      "name": "person",
      "confidence": 0.98,
      "coordinates": [34, 56, 130, 180]
    },
    {
      "name": "car",
      "confidence": 0.91,
      "coordinates": [200, 90, 400, 250]
    }
  ]
}
설명:

클라이언트는 이미지를 업로드하여 객체 탐지를 요청합니다.
서버는 YOLO 모델을 사용하여 이미지에서 객체를 탐지하고, 탐지된 객체의 이름, 신뢰도, 좌표를 반환합니다. -->


## API 문서
    FastAPI 서버는 자동으로 Swagger UI 문서를 제공합니다. 서버가 실행된 후, 아래 URL에서 API 문서를 확인할 수 있습니다:

* Swagger UI: http://localhost:8000/docs

이 문서를 통해 각 엔드포인트의 사용법과 요청/응답 형식을 확인할 수 있습니다.

## 주의사항
* 서버는 Docker에서 실행되어야 하며, 클라이언트는 이 서버와 통신하여 객체 탐지 및 이미지 캡셔닝 결과를 실시간으로 받을 수 있습니다.
* YOLO v11 모델은 client에, ClipCap 모델은 서버에 포함되어 있으며, 이들 모델의 추론을 실시간으로 처리합니다. (clipcap 디렉터리에 튜닝한 모델의 .pt파일을 넣고, clipcap_dir 디렉터리에 clipcap의 깃허브에서 클론한 내용을 넣으면 됌.)
* 서버는 Python 3.10 버전 이상에서 실행됩니다.